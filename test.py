from woocommerce import API
wcapi = API(
    url="https://www.shopmanual2you.com/",
    consumer_key="ck_2b201992a3b7205b97b91ebaae9b74cffd0492b2",
    consumer_secret="cs_43a4861af8b79e8d9f933c51fea31e1eb7b2af69",
    version="wc/v3",
    timeout=20
)
data= {
        "regular_price": "2500",
        "attributes": [
            {
                "id": 4,
                "option": "Hard copy"
            }
        ]
    }
    

result= wcapi.get("products/tags?page=2&per_page=100").json()
for c in result:
    print ("id:%s name:%s slug:%s"%(c['id'],c['name'],c['slug']))
#print (result)