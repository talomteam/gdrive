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
from os.path import join, dirname
from dotenv import load_dotenv
from pymysqlpool.pool import Pool
import pymysql.cursors
from woocommerce import API

import csv
import pandas as pd
import os
import openpyxl 

wcapi = API(
    url="https://https://www.shopmanual2you.com/",
    consumer_key="ck_2b201992a3b7205b97b91ebaae9b74cffd0492b2",
    consumer_secret="cs_43a4861af8b79e8d9f933c51fea31e1eb7b2af69",
    version="wc/v3"
)

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
db_host = os.environ.get("DB_HOST")
db_user = os.environ.get("DB_USER")
db_password = os.environ.get("DB_PASSWORD")
db_name = os.environ.get("DB_NAME")


fernet = Fernet(key)

brands = {}
categories = {}
booktypes = {}
languages = {}


def getfile(file_id):
    generate_filename = 'downloads/%s.pdf' % (file_id)
    file = drive.CreateFile({'id': file_id})
    file.GetContentFile(generate_filename)

def getimage(file_id):
    generate_filename = 'images/%s.jpg' % (file_id)
    file_exists = exists(generate_filename)
    if not file_exists :
        file = drive.CreateFile({'id': file_id})
        file.GetContentFile(generate_filename)

def encryptcp(fileb64):
    return fernet.encrypt(fileb64.encode()).decode()

def decryptcp(fileb64):
    return fernet.decrypt(fileb64.encode()).decode()

def getIndexes():
    try:
        cursor = connection_db.cursor()
        sql = "SELECT * FROM brands"
        cursor.execute(sql)
        result_brands = cursor.fetchall()
        for brand in result_brands:
            brands[brand['name'].upper()]= brand['code']

        sql = "SELECT * FROM categories"
        cursor.execute(sql)
        result_categories = cursor.fetchall()
        for category in result_categories:
            categories[category['name'].upper()]= category['code']

        sql = "SELECT * FROM book_types"
        cursor.execute(sql)
        result_booktypes = cursor.fetchall()
        for booktype in result_booktypes:
            booktypes[booktype['name'].upper()]= booktype['code']

        sql = "SELECT * FROM languages"
        cursor.execute(sql)
        result_languages = cursor.fetchall()
        for language in result_languages:
            languages[language['name'].upper()]= language['code']
    except:
        print("connection db problem")

try:
    pool = Pool(host=db_host, port=3306, user=db_user, password=db_password, db=db_name,autocommit=True,ping_check=True,cursorclass=pymysql.cursors.DictCursor)
    connection_db = pool.get_conn()
    getIndexes()
except :
    print("Error while connecting to MySQL using Connection pool ")

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
    
    for x in file_dict:
        if file_dict[x]["type"] == "file" :
            try:
                cursor = connection_db.cursor()
                sql = "INSERT INTO files (id,title,dir,preview,download) values (%s,%s,%s,%s,%s)"
                val = (file_dict[x]["id"],file_dict[x]["title"],file_dict[x]["dir"],file_dict[x]["preview"],file_dict[x]["download"])
                cursor.execute(sql,val)
                connection_db.commit()
            except:
               print(sql)

        
    #cvsDataframe = pd.DataFrame(file_dict).transpose().head(10)
    cvsDataframe = pd.DataFrame(file_dict).transpose()
    resultExcelFile = pd.ExcelWriter(xls_filename)
    cvsDataframe.to_excel(resultExcelFile, index=False)
    resultExcelFile.close()

    gfile = drive.CreateFile({'parents': [{'id': path}]})
    gfile.SetContentFile(xls_filename)
    gfile.Upload()

    return {"message": "Please check google drive file name %s" % (xls_filename)}

@app.get("/v1/files/product")
async def file_product():
    file_id = '11OK7R6zqW7h7szSqI3F_gP4UVg-1mDps'
    generate_filename = '%s.xlsx' % (file_id)
    file = drive.CreateFile({'id': file_id})
    file.GetContentFile(generate_filename)

    wb = openpyxl.load_workbook(generate_filename)
    sheet =  wb['Exam']
    max_row = 4

    for row in range(3, max_row):
        product = {}
        product["no"] = sheet.cell(row=row,column=1).value
        product["brand"] = sheet.cell(row=row,column=2).value
        product["categories_en"] = sheet.cell(row=row,column=4).value
        product["categories_th"] = sheet.cell(row=row,column=5).value
        product["booktype_en"] = sheet.cell(row=row,column=7).value
        product["booktype_th"] = sheet.cell(row=row,column=8).value
        product["parts_no"] = sheet.cell(row=row,column=10).value
        product["model"] = sheet.cell(row=row,column=11).value
        product["serial_no"] = sheet.cell(row=row,column=12).value
        product["page_no"] = sheet.cell(row=row,column=13).value
        product["file_type"] = sheet.cell(row=row,column=14).value
        product["file_lang"] = sheet.cell(row=row,column=15).value
        product["price"] = sheet.cell(row=row,column=17).value
        product["price2"] = sheet.cell(row=row,column=18).value
        product["sku"] = 'S2Y-%s%s-%s%s-%s'%(brands[product["brand"].upper()],categories[product["categories_en"].upper()],booktypes[product["booktype_en"].upper()],languages[product["file_lang"].upper()],product["no"])

        product["file_download_id"] = (sheet.cell(row=row,column=24).value).split("/")[-2]
        product["images"] = (sheet.cell(row=row,column=25).value).split(",")
        product["file_image"] = list()
        for image in product["images"]:
            if (image.strip() != ""):
                product["file_image"].append(image.split("/")[-2])
                getimage(image.split("/")[-2])
        product_update(product)

    return {"message": "file product ok"}


@app.post("/v1/indexes")
async def add_index():
    getIndexes()
    print (brands)
    print (categories)
    print (booktypes)
    print (languages)
    return {"message": "indexes is ok"}

def checkValue(origin,word):
    if origin == word :
        return True
    return False

def product_update(product):
    #check record
        #if exist update
            #check column exist update
                #if exist column and call api
        #if not exist new record
            #create and call api

    cursor = connection_db.cursor()
    sql = "select * from products where no=%s Limit 1"
    val = (product["no"])
    cursor.execute(sql,val)
    row =  cursor.fetchone()
    row_count = cursor.rowcount

    if row_count <= 0:
        val = (product["no"],product["brand"].upper(),product["categories_en"].upper(),product["categories_th"],product["booktype_en"].upper(),product["booktype_th"],product["parts_no"],product["model"],product["serial_no"],str(product["page_no"]),product["file_type"],product["file_lang"].upper(),product["price"],product["sku"],product["file_download_id"],','.join(product["file_image"]),product["price2"])
        print(val)
        cursor = connection_db.cursor()
        sql = "INSERT INTO products (no,brand,categories_en,categories_th,booktype_en,booktype_th,part_no,model,serial_no,page_no,file_type,file_lang,price,sku,file_download_id,images,price2) value (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
        cursor.execute(sql,val)
        connection_db.commit()
    else: 
        columns = []
        for k,y in product:
            if checkValue(y,row[k]) == False:
                print (k)
                columns.append(k)

        if len(columns) == 0 :
            val = []
            query = "update products set "
            field = ""
            for column in columns:
                field += column+"=%s,"
                val.append(product[column])

            sql = query +  field[0:-1]+ " where no="+product["no"]
            cursor.execute(sql,val)
            connection_db.commit()    
        
    