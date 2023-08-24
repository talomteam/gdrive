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

def addProducts(product):
    data = {
        "name": "Premium Quality-en",
        "type": "variable",
        "regular_price": "21.99",
        "description": "Pellentesque habitant morbi tristique senectus et netus et malesuada fames ac turpis egestas. Vestibulum tortor quam, feugiat vitae, ultricies eget, tempor sit amet, ante. Donec eu libero sit amet quam egestas semper. Aenean ultricies mi vitae est. Mauris placerat eleifend leo.",
        "short_description": "Pellentesque habitant morbi tristique senectus et netus et malesuada fames ac turpis egestas.",
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
        "lang":"en",
        "images": [
            {
                "src": "http://demo.woothemes.com/woocommerce/wp-content/uploads/sites/56/2013/06/T_2_front.jpg"
            },
            {
                "src": "http://demo.woothemes.com/woocommerce/wp-content/uploads/sites/56/2013/06/T_2_back.jpg"
            }
            ]
        }
    result = wcapi.post("products", data).json()
    print(result)
    print(result["id"])

def updateProduct(product):
    pass    

def updateVariation (options,productId)
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
