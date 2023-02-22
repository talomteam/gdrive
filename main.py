from fastapi import FastAPI
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
from starlette.responses import FileResponse
from starlette.exceptions import HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import StreamingResponse
from cryptography.fernet import Fernet

from PyPDF2 import PdfReader, PdfWriter
from os.path import exists
import csv
import pandas as pd
import base64


app = FastAPI()

app.mount("/previews", StaticFiles(directory="previews"), name="previews")

gauth = GoogleAuth()
gauth.CommandLineAuth()
drive = GoogleDrive(gauth)

key = b'ApG6cwOgJPiZ_me29ePFE5zfN20rxqLjbrop6YydSaQ='

fernet = Fernet(key)


def getfile(file_id):
    generate_filename = 'downloads/%s.pdf' % (file_id)
    file = drive.CreateFile({'id': file_id})
    file.GetContentFile(generate_filename)


def encryptcp(fileb64):
    return fernet.encrypt(fileb64.encode()).decode()


def decryptcp(fileb64):
    return fernet.decrypt(fileb64.encode()).decode()


@app.get("/download/{fileb64}")
async def download(fileb64):
    try:
        file_id = decryptcp(fileb64).split("download")[1]
        generate_filename = 'downloads/%s.pdf' % (file_id)
        file_exists = exists(generate_filename)
        if file_exists:
            return FileResponse(generate_filename, media_type='application/octet-stream', filename=generate_filename.split("/")[-1])

        getfile(file_id)

        file_exists = exists(generate_filename)

        if not file_exists:
            raise HTTPException(status_code=404, detail="Item not found")

        return FileResponse(generate_filename, media_type='application/octet-stream', filename=generate_filename.split("/")[-1])

    except:
        raise HTTPException(status_code=404, detail="Item not found")


@app.get("/preview/{fileb64}")
async def preview(fileb64):
    try:
        file_id = decryptcp(fileb64).split("preview")[1]

        download_filename = 'downloads/%s.pdf' % (file_id)
        out_filename = 'previews/%s.pdf' % (file_id)

        file_preview_exists = exists(out_filename)

        def iterfile():
            with open(out_filename, mode="rb") as file_like:
                yield from file_like

        if file_preview_exists:
            return StreamingResponse(iterfile(), media_type="application/pdf")

        file_download_exists = exists(download_filename)
        if not file_download_exists:
            getfile(file_id)

        pdf = PdfReader(open(download_filename, "rb"))
        pdf_writer = PdfWriter()
        pages = 5

        if len(pdf.pages) < pages:
            pages = len(pdf.pages)

        for page in range(pages):
            pdf_writer.add_page(pdf.pages[page])

        pdf_writer.write(out_filename)

        return StreamingResponse(iterfile(), media_type="application/pdf")
    except:
        raise HTTPException(status_code=404, detail="Item not found")


@app.get("/lists/{path}")
async def lists(path):
    try:
        fieldnames = ["title", "id", "preview", "download"]
        csv_filename = 'documentlists.csv'
        xls_filename = 'documentlists.xlsx'

        fcsv = open(csv_filename, 'w')
        writer = csv.DictWriter(fcsv, fieldnames=fieldnames)
        writer.writeheader()

        file_list = drive.ListFile(
            {'q': "'{}' in parents and trashed=false".format(path)}).GetList()
        for file in file_list:
            if file['title'] == xls_filename:
                file.Delete()
            preview_file_id = encryptcp("preview"+file['id'])
            download_file_id = encryptcp("download"+file['id'])
            pdfjs_template = '[pdfjs-viewer url="https://bz-portal.xyz/gdrive/preview/{file_id}" viewer_width=100% viewer_height=800px fullscreen=true download=true print=true]'.format(
                file_id=preview_file_id)
            download_template = 'https://bz-portal.xyz/gdrive/download/{file_id}'.format(
                file_id=download_file_id)
            writer.writerow({"title": file['title'], "id": file['id'],
                            "preview": pdfjs_template, "download": download_template})
            # print('title: %s, id: %s' % (file['title'], file['id']))

        # sub folder and file
        folder_list = drive.ListFile(
            {'q': "'{}' in parents and trashed=false and mimeType='application/vnd.google-apps.folder'".format(path)}).GetList()

        for folder in folder_list:
            # print('title: %s, id: %s' % (folder['title'], folder['id']))
            file_list = drive.ListFile(
                {'q': "'{}' in parents and trashed=false".format(folder['id'])}).GetList()
            for file in file_list:
                preview_file_id = encryptcp("preview"+file['id'])
                download_file_id = encryptcp("download"+file['id'])
                pdfjs_template = '[pdfjs-viewer url= "https://bz-portal.xyz/gdrive/preview/{file_id}" viewer_width=100% viewer_height=800px fullscreen=true download=true print=true]'.format(
                    file_id=preview_file_id)
                download_template = 'https://bz-portal.xyz/gdrive/download/{file_id}'.format(
                    file_id=download_file_id)
                writer.writerow(
                    {"title": file['title'], "id": file['id'], "preview": pdfjs_template, "download": download_template})
                # print('\t title: %s, id: %s' % (file['title'], file['id']))

        fcsv.close()

        cvsDataframe = pd.read_csv(csv_filename)
        resultExcelFile = pd.ExcelWriter(xls_filename)
        cvsDataframe.to_excel(resultExcelFile, index=False)
        resultExcelFile.save()

        gfile = drive.CreateFile({'parents': [{'id': path}]})
        gfile.SetContentFile(xls_filename)
        gfile.Upload()

        return {"message": "Please check google drive file name %s" % (xls_filename)}
    except:
        raise HTTPException(status_code=404, detail="Path not found")
