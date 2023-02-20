from fastapi import FastAPI, File, UploadFile
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
from starlette.responses import FileResponse
from starlette.exceptions import HTTPException

from PyPDF2 import PdfReader, PdfWriter
from os.path import exists
import csv
import pandas as pd


app = FastAPI()

gauth = GoogleAuth()
gauth.CommandLineAuth()
drive = GoogleDrive(gauth)

def getfile(file_id):
    generate_filename = 'downloads/%s.pdf' % (file_id)
    file = drive.CreateFile({'id': file_id})
    file.GetContentFile(generate_filename)


@app.get("/download/{file_id}")
async def download(file_id):

    generate_filename = 'downloads/%s.pdf' % (file_id)
    file_exists = exists(generate_filename)
    if file_exists:
        return FileResponse(generate_filename, media_type='application/octet-stream', filename=generate_filename.split("/")[-1])

    # file = drive.CreateFile({'id': file_id})
    # file.GetContentFile(generate_filename)
    getfile(file_id)

    file_exists = exists(generate_filename)

    if file_exists:
        return FileResponse(generate_filename, media_type='application/octet-stream', filename=generate_filename.split("/")[-1])
    else:
        raise HTTPException(status_code=404, detail="Item not found")


@app.get("/preview/{file_id}")
async def preview(file_id):

    download_filename = 'downloads/%s.pdf' % (file_id)
    out_filename = "previews/%s.pdf" % (file_id)
    file_preview_exists = exists(out_filename)

    if file_preview_exists:
        return FileResponse(out_filename, media_type='application/octet-stream', filename=out_filename.split("/")[-1])

    file_download_exists = exists(download_filename)
    if not file_download_exists:
        getfile(file_id)

    pdf = PdfReader(open(download_filename, "rb"))
    pdf_writer = PdfWriter()
    pages = 5
    if len(pdf.pages) < len(pdf.pages):
        pages = len(pdf.pages)
        for page in range(pages):
            pdf_writer.add_page(pdf.pages[page])
        pdf_writer.write(out_filename)
    return FileResponse(out_filename, media_type='application/octet-stream', filename=out_filename.split("/")[-1])


@app.get("/lists/{path}")
async def lists(path):
    #file current folder
    #fieldnames = ["kind", "userPermission", "selfLink", "ownerNames", "lastModifyingUserName", "editable", "writersCanShare", "mimeType", "parents", "appDataContents", "iconLink", "shared", "lastModifyingUser", "owners", "copyable", "etag", "alternateLink", "embedLink",
    #              "copyRequiresWriterPermission", "spaces", "id", "title", "labels", "explicitlyTrashed", "createdDate", "modifiedDate", "modifiedByMeDate", "lastViewedByMeDate", "markedViewedByMeDate", "quotaBytesUsed", "version", "capabilities", 'thumbnailLink', 'exportLinks', 'fileSize', 'fileExtension', 'headRevisionId', 'downloadUrl', 'webContentLink', 'md5Checksum', 'originalFilename']
    fieldnames = ["title","id"]
    csv_filename = 'documentlists.csv'
    xls_filename = 'documentlists.xlsx'

    fcsv = open(csv_filename,'w')
    writer = csv.DictWriter(fcsv,fieldnames=fieldnames)
    writer.writeheader()
    file_list = drive.ListFile(
        {'q': "'{}' in parents and trashed=false".format(path)}).GetList()
    for file in file_list:
        if file['title'] == xls_filename:
            file.Delete()
        writer.writerow({"title":file['title'], "id":file['id']})
        print('title: %s, id: %s' % (file['title'], file['id']))


    # sub folder and file
    folder_list = drive.ListFile(
        {'q': "'{}' in parents and trashed=false and mimeType='application/vnd.google-apps.folder'".format(path)}).GetList()
    
    for folder in folder_list:
        print('title: %s, id: %s' % (folder['title'], folder['id']))
        file_list = drive.ListFile(
            {'q': "'{}' in parents and trashed=false".format(folder['id'])}).GetList()
        for file in file_list:
            writer.writerow({"title": file['title'], "id": file['id']})
            print('\t title: %s, id: %s' % (file['title'], file['id']))
    
    fcsv.close()

    cvsDataframe = pd.read_csv(csv_filename)
    resultExcelFile = pd.ExcelWriter(xls_filename)
    cvsDataframe.to_excel(resultExcelFile, index=False)
    resultExcelFile.save()

    gfile = drive.CreateFile({'parents': [{'id': path}]})
    gfile.SetContentFile(xls_filename)
    gfile.Upload()
    


    return {"message": "Please check google drive file name %s"%(xls_filename)}
