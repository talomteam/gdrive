from woocommerce import API
import os
import random
import string
import os

wcapi = API(
    url="https://www.shopmanual2you.com/",
    consumer_key=os.environ.get("WC_CK"),
    consumer_secret=os.environ.get("WC_CS"),
    version="wc/v3",
    timeout=60
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
        "description": ("Brand : %s <br/> Booktype: %s <br/> Model: %s <br/> Serial: %s <br/> Language: %s <br/> File type: %s <br/>Number of page: %s Preview: <br>%s<br/>"%(product["brand"],product["booktype_en"],product["model"],product["serial_no"],product["file_lang"],product["file_type"],product["page_no"],product["preview"])),
        "short_description": ("Brand : %s <br/> Booktype: %s <br/> Model: %s <br/> Serial: %s <br/> Language: %s <br/> File type: %s <br/>Number of page: %s<br/> "%(product["brand"],product["booktype_en"],product["model"],product["serial_no"],product["file_lang"],product["file_type"],product["page_no"])),
        "sku": product["sku"]+"-EN",
        "categories": [
            {
                "id": int(product["brands_ref"][product["brand"]]["en"])
            },
            {
                "id": int(product["categories_ref"][product["categories_en"]]["en"])
            }
        ],
        "tags":[
            {
                "id": int(product["brands_ref"][product["brand"]]["tag_en"])
            },
            {
                "id": int(product["booktype_ref"][product["booktype_en"]]["en"])
            }
        ],
        "attributes": [
            {
                "id": 4,
                "position": 0,
                "visible": False,
                "variation": True,
                "options": [
                    "Book",
                    "PDF File"
                ]
            }
        ],
        "default_attributes": [
            {
                "id": 4,
                "option": "Book"
            },
            
        ],
        "lang":"en"
        }
    print (data_en)
    
   
    ## create product th
    data_th = {
        "name": ("%s %s %s %s"%(product["brand"],product["categories_th"],product["booktype_th"],product["model"])),
        "type": "variable",
        "description": ("Brand : %s <br/> Booktype: %s <br/> Model: %s <br/> Serial: %s <br/> Language: %s <br/> File type: %s <br/>Number of page: %s preview:<br> %s<br/>"%(product["brand"],product["booktype_en"],product["model"],product["serial_no"],product["file_lang"],product["file_type"],product["page_no"],product["preview"])),
        "short_description": ("Brand : %s <br/> Booktype: %s <br/> Model: %s <br/> Serial: %s <br/> Language: %s <br/> File type: %s <br/>Number of page: %s<br/> "%(product["brand"],product["booktype_en"],product["model"],product["serial_no"],product["file_lang"],product["file_type"],product["page_no"])),
        "sku": product["sku"]+"-TH",
        "categories": [
            {
                "id": int(product["brands_ref"][product["brand"]]["th"])
            },
            {
                "id": int(product["categories_ref"][product["categories_en"]]["th"])
            }
        ],
        "tags":[
            {
                "id":int(product["brands_ref"][product["brand"]]["tag_th"])
            },
            {
                "id": int(product["booktype_ref"][product["booktype_en"]]["th"])
            }
        ],
        "attributes": [
            {
                "id": 4,
                "position": 0,
                "visible": False,
                "variation": True,
                "options": [
                    "หนังสือ",
                    "ไฟล์"
                ]
            }
        ],
        "default_attributes": [
            {
                "id": 4,
                "option": "ไฟล์"
            },
            
        ],
        "lang":"th"
        }
    
    print (data_th)
    try:
        result_en = wcapi.post("products", data_en).json()
        result_th = wcapi.post("products", data_th).json()
        print("product en id",result_en["id"] )
        print("product th id",result_th["id"] )
        #add ref db
   
        cursor = connection_db.cursor()
        sql = "INSERT INTO woo_products (product_no,woo_product_en_id,woo_product_th_id) values (%s,%s,%s)"
        val = (product["no"],result_en["id"],result_th["id"])
        cursor.execute(sql,val)
        connection_db.commit()

        updateTranslations(result_en["id"],result_th["id"])
        addVariation(product,result_en["id"],result_th["id"])
    except Exception as e:
        print(e)
        #print(sql,val)
    

    p_images = {
        "images": file_images
    }
    try :
        result_images_en = wcapi.put("products/%s"%(result_en["id"]), p_images).json()
        result_images_en = wcapi.put("products/%s"%(result_th["id"]), p_images).json()
    except Exception as e:
        print(e)

def updateTranslations(product_en_id,product_th_id):

    translation = 'a:2:{s:2:"th";i:%s;s:2:"en";i:%s;}'%(product_th_id,product_en_id)
    #en
    en_prefix = "pll_74e"
    en_random = ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))
    #insert wp_terms
    cursor = connection_db.cursor()
    sql = "INSERT INTO wordpress.wp_terms (name,slug,term_group) values (%s,%s,%s)"
    val = (en_prefix+en_random,en_prefix+en_random,0)
    cursor.execute(sql,val)
    en_term_id = cursor.lastrowid
    #insert wp_term_relationships
    sql = "INSERT INTO wordpress.wp_term_relationships (object_id,term_taxonomy_id,term_order) values (%s,%s,%s)"
    val = (product_en_id,en_term_id,0)
    cursor.execute(sql,val)
    #insert wp_term_taxonomy
    sql = "INSERT INTO wordpress.wp_term_taxonomy (term_taxonomy_id,term_id,taxonomy,description) values (%s,%s,%s,%s)"
    val = (en_term_id,en_term_id,'post_translations',translation)
    cursor.execute(sql,val)


    #th
    th_prefix = "pll_84e"
    th_random = ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))
    #insert wp_terms
    cursor = connection_db.cursor()
    sql = "INSERT INTO wordpress.wp_terms (name,slug,term_group) values (%s,%s,%s)"
    val = (th_prefix+th_random,th_prefix+th_random,0)
    cursor.execute(sql,val)
    th_term_id = cursor.lastrowid
    #insert wp_term_relationships
    sql = "INSERT INTO wordpress.wp_term_relationships (object_id,term_taxonomy_id,term_order) values (%s,%s,%s)"
    val = (product_th_id,th_term_id,0)
    cursor.execute(sql,val)
    #insert wp_term_taxonomy
    sql = "INSERT INTO wordpress.wp_term_taxonomy (term_taxonomy_id,term_id,taxonomy,description) values (%s,%s,%s,%s)"
    val = (th_term_id,th_term_id,'post_translations',translation)
    cursor.execute(sql,val)


def updateProduct(col,product,row):

    price = col.index('price') if 'price' in col else -1
    price2 = col.index('price2') if 'price2' in col else -1
    if price > -1  or price2 > -1:
        updateVariation(col,product,row) 

   

def updateVariation (col,product,row):
    #en
    data_h_en = {
        "regular_price": str(product["price2"]),
    }
    
    data_s_en = {
        "regular_price": str(product["price"]),
        
    }
    #th
    data_h_th = {
        "regular_price": str(product["price2"]),
    }
    
    data_s_th = {
        "regular_price": str(product["price"]),
        
    }
    result_h_en = wcapi.put("products/%s/variations/%s"%(row["woo_product_en_id"],row["woo_variation_h_en"]), data_h_en).json()
    result_s_en = wcapi.put("products/%s/variations/%s"%(row["woo_product_en_id"],row["woo_variation_s_en"]), data_s_en).json()

    result_h_th = wcapi.put("products/%s/variations/%s"%(row["woo_product_th_id"],row["woo_variation_h_th"]), data_h_th).json()
    result_s_th = wcapi.put("products/%s/variations/%s"%(row["woo_product_th_id"],row["woo_variation_s_th"]), data_s_th).json()
    
def addVariation (product,productIden,productIdth):

    pfiles = list()
    for download in product["download"]:
        pfile = {}
        pfile["name"] = (product["brand"]+"-"+product["parts_no"])
        pfile["file"] = download
        pfiles.append(pfile)

    ## create product variation en
    data_h_en = {
        "regular_price": str(product["price2"]),
        "attributes": [
            {
                "id": 4,
                "option": "Book"
            }
        ]
    }
    
    
    data_s_en = {
        "regular_price": str(product["price"]),
        "virtual": True,
        "downloadable": True,
        "attributes": [
            {
                "id": 4,
                "option": "PDF File"
            }
        ],
        "downloads": pfiles
    }
    result_h_en = wcapi.post("products/%s/variations"%(productIden), data_h_en).json()
    result_s_en = wcapi.post("products/%s/variations"%(productIden), data_s_en).json()

    ## create product variation en
    data_h_th = {
        "regular_price": str(product["price2"]),
        "attributes": [
            {
                "id": 4,
                "option": "หนังสือ"
            }
        ]
    }
    
    data_s_th = {
        "regular_price": str(product["price"]),
        "virtual": True,
        "downloadable": True,
        "attributes": [
            {
                "id": 4,
                "option": "ไฟล์"
            }
        ],
        "downloads": pfiles
    }
    result_h_th = wcapi.post("products/%s/variations"%(productIdth), data_h_th).json()
    result_s_th = wcapi.post("products/%s/variations"%(productIdth), data_s_th).json()

    print("v h en id",result_h_en["id"] )
    print("v s en id",result_s_en["id"] )

    print("v h th id",result_h_th["id"] )
    print("v s th id",result_s_th["id"] )

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



