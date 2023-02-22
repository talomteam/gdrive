from cryptography.fernet import Fernet
key = b'ApG6cwOgJPiZ_me29ePFE5zfN20rxqLjbrop6YydSaQ='

fernet = Fernet(key)

message = '1lcVcRis5-qZayIRFJsadxno6jWq9YVir'

encMessage = fernet.encrypt(message.encode())

print("original string: ", message)
print("encrypted string: ", encMessage)

decMessage = fernet.decrypt(encMessage).decode()

print("decrypted string: ", decMessage)
