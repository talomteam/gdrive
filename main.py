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

import os
from os.path import join, dirname
from dotenv import load_dotenv

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

app = FastAPI()

app.mount("/previews", StaticFiles(directory="previews"), name="previews")

gauth = GoogleAuth()
gauth.CommandLineAuth()
drive = GoogleDrive(gauth)

# print(os.environ.get("APP_KEY"))

key = os.environ.get("APP_KEY")
domain = os.environ.get("DOMAIN_NAME")


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
async def preview(fileb64,start: int = 1, end: int = 5 ):
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
        #pages = 5

        #if len(pdf.pages) < pages:
        #    pages = len(pdf.pages)

        for page in range((start-1),end):
            pdf_writer.add_page(pdf.pages[page])
        
        pdf_writer.add_metadata(pdf.metadata)
        pdf_writer.write(out_filename)

        return StreamingResponse(iterfile(), media_type="application/pdf")
    except:
        raise HTTPException(status_code=404, detail="Item not found")


@app.get("/list_test/{path}")
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
            pdfjs_template = '[pdfjs-viewer url="https://{domain}/gdrive/preview/{file_id}" viewer_width=100% viewer_height=800px fullscreen=true download=true print=true]'.format(
                domain=domain,file_id=preview_file_id)
            download_template = 'https://{domain}/gdrive/download/{file_id}'.format(
                domain=domain,file_id=download_file_id)
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
                pdfjs_template = '[pdfjs-viewer url= "https://{domain}/gdrive/preview/{file_id}" viewer_width=100% viewer_height=800px fullscreen=true download=true print=true]'.format(
                    domain=domain,file_id=preview_file_id)
                download_template = 'https://{domain}/gdrive/download/{file_id}'.format(
                    domain=domain,file_id=download_file_id)
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

@app.get("/heartbeat/{path}")
async def heartbeat(path):
    try:
        file_list = drive.ListFile(
                {'q': "'{}' in parents and trashed=false".format(path)}).GetList()
        return {"message":"connected ok"}
    except:
        raise HTTPException(status_code=503, detail="Connect error")


@app.get("/lists/{path}")
async def lists(path):
    xls_filename = 'documentlists.xlsx'
    file_dict = dict()

    parent_folder_id = path
    parent_folder_dir = './'

    if parent_folder_dir[-1] != '/':
        parent_folder_dir = parent_folder_dir + '/'

    folder_queue = [parent_folder_id]
    dir_queue = [parent_folder_dir]
    cnt = 0

    while len(folder_queue) != 0:
        current_folder_id = folder_queue.pop(0)
        file_list = drive.ListFile(
            {'q': "'{}' in parents and trashed=false".format(current_folder_id)}).GetList()

        current_parent = dir_queue.pop(0)
        print(current_parent, current_folder_id)
        for file1 in file_list:
            if file1['title'] == xls_filename:
                file1.Delete()
            file_dict[cnt] = dict()
            file_dict[cnt]['id'] = file1['id']
            file_dict[cnt]['title'] = file1['title']
            file_dict[cnt]['dir'] = current_parent + file1['title']

            if file1['mimeType'] == 'application/vnd.google-apps.folder':
                file_dict[cnt]['type'] = 'folder'
                file_dict[cnt]['dir'] += '/'
                folder_queue.append(file1['id'])
                dir_queue.append(file_dict[cnt]['dir'])
                file_dict[cnt]['preview'] = ""
                file_dict[cnt]['download'] = ""
            else:
                preview_file_id = encryptcp("preview"+file1['id'])
                download_file_id = encryptcp("download"+file1['id'])
                pdfjs_template = '[pdfjs-viewer url= "https://{domain}z/gdrive/preview/{file_id}?start=1&end=4" viewer_width=100% viewer_height=800px fullscreen=true download=true print=true]'.format(
                    domain=domain,file_id=preview_file_id)
                download_template = 'https://{domain}/gdrive/download/{file_id}'.format(
                    domain=domain,file_id=download_file_id)
                file_dict[cnt]['type'] = 'file'
                file_dict[cnt]['preview'] = pdfjs_template
                file_dict[cnt]['download'] = download_template

            cnt += 1

    #cvsDataframe = pd.DataFrame(file_dict).transpose().head(10)
    cvsDataframe = pd.DataFrame(file_dict).transpose()
    resultExcelFile = pd.ExcelWriter(xls_filename)
    cvsDataframe.to_excel(resultExcelFile, index=False)
    resultExcelFile.save()

    gfile = drive.CreateFile({'parents': [{'id': path}]})
    gfile.SetContentFile(xls_filename)
    gfile.Upload()

    return {"message": "Please check google drive file name %s" % (xls_filename)}
