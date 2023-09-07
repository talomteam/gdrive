#from woocommerce import API
#wcapi = API(
#    url="https://www.shopmanual2you.com/",
#    consumer_key="ck_2b201992a3b7205b97b91ebaae9b74cffd0492b2",
#    consumer_secret="cs_43a4861af8b79e8d9f933c51fea31e1eb7b2af69",
#    version="wc/v3",
#    timeout=20
#)
#data= {
#        "translations": {
#                "en":"5809"
#            }
#
#    }
    

#result= wcapi.put("products/5811",data).json()
#for c in result:
#    print ("id:%s name:%s slug:%s"%(c['id'],c['name'],c['slug']))
#print (result)


# import all the libraries
#from PIL import Image
#image = Image.open("images/1r5lJiBr4iFezMdgvGuBfa1BHYQkZg4KC-34-600x375.jpg")
#image_watermask = Image.open("images/T1C3.png")
#width_of_watermark , height_of_watermark = image_watermask.size
#width,height = image.size
#position = (int(width/2-width_of_watermark/2),int(height/2-height_of_watermark/2))

#image.paste(image_watermask,position,image_watermask)
#image.save("images/sample.jpg")
from PyPDF2 import PdfReader, PdfWriter
download_filename = 'images/document.pdf'
watermask_filename = 'images/watermask.pdf'
pdf = PdfReader(open(download_filename, "rb"))
pdf_writer = PdfWriter()

watermask = PdfReader(open(watermask_filename, "rb"))
watermask_page = watermask.pages[0]


for page in range(0,4):
    content_page = pdf.pages[page]
    #mediabox = content_page.mediabox
    content_page.merge_page(watermask_page)
    #content_page.mediabox = mediabox
    pdf_writer.add_page(content_page)
       
pdf_writer.add_metadata(pdf.metadata)
pdf_writer.write('images/sample.pdf')