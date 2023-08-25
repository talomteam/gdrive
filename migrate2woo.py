from woocommerce import API
import os
from pymysqlpool.pool import Pool
import pymysql.cursors

wcapi = API(
    url="https://www.shopmanual2you.com/",
    consumer_key="ck_2b201992a3b7205b97b91ebaae9b74cffd0492b2",
    consumer_secret="cs_43a4861af8b79e8d9f933c51fea31e1eb7b2af69",
    version="wc/v3",
    timeout=20
)
connection_db = None
## create 

attributes = 4
baseUrl = "https://www.shopmanual2you.com/"
pathImage = "gimages/"

def addProducts(product):
    #set images

    file_images = list()
    for image in product["file_image"]:
        srcImage = {}
        srcImage["src"] = "%s%s%s.jpg"%(baseUrl,pathImage,image)
        file_images.append(srcImage)
        
    ## create product en
    data_en = {
        "name": ("%s %s %s %s"%(product["brand"],product["categories_en"],product["booktype_en"],product["model"])),
        "type": "variable",
        "description": ("Brand : %s <br/> Booktype: %s <br/> Model: %s <br/> Serial: %s <br/> Language: %s <br/> File type: %s <br/>Number of page: %s<br/>"%(product["brand"],product["booktype_en"],product["model"],product["serial_no"],product["file_lang"],product["file_type"],product["page_no"])),
        "short_description": ("Brand : %s <br/> Booktype: %s <br/> Model: %s <br/> Serial: %s <br/> Language: %s <br/> File type: %s <br/>Number of page: %s<br/>"%(product["brand"],product["booktype_en"],product["model"],product["serial_no"],product["file_lang"],product["file_type"],product["page_no"])),
        "categories": [
            {
                "id": 9
            },
            {
                "id": 14
            }
        ],
        "attributes": [
            {
                "id": 4,
                "position": 0,
                "visible": False,
                "variation": True,
                "options": [
                    "Hard copy",
                    "Soft file"
                ]
            }
        ],
        "default_attributes": [
            {
                "id": 4,
                "option": "Hard copy"
            },
            
        ],
        "lang":"en",
        "images": file_images
        }
    print (data_en)
    
    ## create product th
    data_th = {
        "name": ("%s %s %s %s"%(product["brand"],product["categories_th"],product["booktype_th"],product["model"])),
        "type": "variable",
        "description": ("Brand : %s <br/> Booktype: %s <br/> Model: %s <br/> Serial: %s <br/> Language: %s <br/> File type: %s <br/>Number of page: %s<br/>"%(product["brand"],product["booktype_en"],product["model"],product["serial_no"],product["file_lang"],product["file_type"],product["page_no"])),
        "short_description": ("Brand : %s <br/> Booktype: %s <br/> Model: %s <br/> Serial: %s <br/> Language: %s <br/> File type: %s <br/>Number of page: %s<br/>"%(product["brand"],product["booktype_en"],product["model"],product["serial_no"],product["file_lang"],product["file_type"],product["page_no"])),
        "categories": [
            {
                "id": 9
            },
            {
                "id": 14
            }
        ],
        "attributes": [
            {
                "id": 4,
                "position": 0,
                "visible": False,
                "variation": True,
                "options": [
                    "Hard copy",
                    "Soft file"
                ]
            }
        ],
        "default_attributes": [
            {
                "id": 4,
                "option": "Soft file"
            },
            
        ],
        "lang":"th",
        "images": file_images
        }
    print (data_th)
    result_en = wcapi.post("products", data_en).json()
    result_th = wcapi.post("products", data_th).json()
    print("product en id",result_en["id"] )
    print("product th id",result_en["id"] )
    #add ref db
    try:
        cursor = connection_db.cursor()
        sql = "INSERT INTO woo_products (product_no,woo_product_en_id,woo_product_th_id) values (%s,%s,%s)"
        val = (product["no"],result_en["id"],result_th["id"])
        cursor.execute(sql,val)
        connection_db.commit()
    except Exception as e:
        print(e)
        print(sql,val)

    addVariation(product,result_en["id"],result_th["id"])
    

def updateProduct(product):
    pass    

def updateVariation (options,productId):
    pass
    
def addVariation (product,productIden,productIdth):

    ## create product variation en
    data_h_en = {
        "regular_price": product["price2"],
        "attributes": [
            {
                "id": 4,
                "option": "Hard copy"
            }
        ]
    }
    
    data_s_en = {
        "regular_price": product["price"],
        "attributes": [
            {
                "id": 4,
                "option": "Soft file"
            }
        ]
    }
    result_h_en = wcapi.post("products/%s/variations"%(productIden), data_h_en).json()
    result_s_en = wcapi.post("products/%s/variations"%(productIden), data_s_en).json()

    ## create product variation en
    data_h_th = {
        "regular_price": product["price2"],
        "attributes": [
            {
                "id": 4,
                "option": "Hard copy"
            }
        ]
    }
    
    data_s_th = {
        "regular_price": product["price"],
        "attributes": [
            {
                "id": 4,
                "option": "Soft file"
            }
        ]
    }
    result_h_th = wcapi.post("products/%s/variations"%(productIdth), data_h_th).json()
    result_s_th = wcapi.post("products/%s/variations"%(productIdth), data_s_th).json()

    #add ref db
    try:
        cursor = connection_db.cursor()
        sql = "update woo_products set woo_variation_h_en=%s,woo_variation_s_en=%s,woo_variation_h_th=%s,woo_variation_s_th=%s where product_no=%s"
        val = (result_h_en["id"],result_s_en["id"],result_h_th["id"],result_s_th["id"],product["no"])
        cursor.execute(sql,val)
        connection_db.commit()
    except Exception as e :
        print(e)
        print(sql,val)



