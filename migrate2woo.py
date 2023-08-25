from woocommerce import API
wcapi = API(
    url="https://www.shopmanual2you.com/",
    consumer_key="ck_2b201992a3b7205b97b91ebaae9b74cffd0492b2",
    consumer_secret="cs_43a4861af8b79e8d9f933c51fea31e1eb7b2af69",
    version="wc/v3",
    timeout=20
)

## create 

attributes = 4
baseUrl = "https://www.shopmanual2you.com/"
pathImage = "gimages/"

def addProducts(product):
    #set images
    
    file_images = list()
    for image in product["file_image"]:
        srcImage = {}
        srcImage["src"] = "%s%s%s.jpg"%(baseUrl,pathImage,product["file_iamge"][i])
        file_images.append(srcImage)
        
    ## create product en
    data_en = {
        "name": ("%s %s %s %s"%(product["brand"],product["categories_en"],product["booktype_en"],product["model"])),
        "type": "variable",
        "description": ("Brand : %s <br/> Booktype: %s <br/> Model: %s <br/> Serial: %s <br/> Language: %s <br/> File type: %s <br/>Number of page: %s<br/>"%(product["brand"],product["categories_en"],product["booktype_en"],product["model"],product["parts_no"],product["file_lang"],product["file_type"],product["parts_no"])),
        "short_description": ("Brand : %s <br/> Booktype: %s <br/> Model: %s <br/> Serial: %s <br/> Language: %s <br/> File type: %s <br/>Number of page: %s<br/>"%(product["brand"],product["categories_en"],product["booktype_en"],product["model"],product["parts_no"],product["file_lang"],product["file_type"],product["parts_no"])),
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
    #result = wcapi.post("products", data).json()
    #print(result)
    #print(result["id"])
    #addVariation(product,result["id"])
    
    ## create product th
    data_th = {
        "name": ("%s %s %s %s"%(product["brand"],product["categories_th"],product["booktype_th"],product["model"])),
        "type": "variable",
        "description": ("Brand : %s <br/> Booktype: %s <br/> Model: %s <br/> Serial: %s <br/> Language: %s <br/> File type: %s <br/>Number of page: %s<br/>"%(product["brand"],product["categories_th"],product["booktype_th"],product["model"],product["parts_no"],product["file_lang"],product["file_type"],product["parts_no"])),
        "short_description": ("Brand : %s <br/> Booktype: %s <br/> Model: %s <br/> Serial: %s <br/> Language: %s <br/> File type: %s <br/>Number of page: %s<br/>"%(product["brand"],product["categories_th"],product["booktype_th"],product["model"],product["parts_no"],product["file_lang"],product["file_type"],product["parts_no"])),
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
    print (data_th)
    #result = wcapi.post("products", data).json()
    #print(result)
    #print(result["id"])
    #addVariation(product,result["id"])

def updateProduct(product):
    pass    

def updateVariation (options,productId):
    pass
    
def addVariation (options,productId):
    data = options
    result = wcapi.post("products/%s/variations"%(productId), data).json()
    print (result)
    print(result["id"])
    return result["id"]

data = {
    "regular_price": "100.00",
    "attributes": [
        {
            "id": 4,
            "option": "Hard copy"
        }
    ]
}
