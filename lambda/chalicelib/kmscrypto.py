import boto3
import os
import base64
kms = boto3.client('kms', region_name = 'us-east-1')

class Crypto:
    def __init__(self, kmskey):
        self.kmskey = 'alias/'+ kmskey

    def encrypt(self, plaintext ):
        ciphertext = kms.encrypt(KeyId=self.kmskey,Plaintext=plaintext)
        return base64.b64encode(ciphertext["CiphertextBlob"]).decode('utf-8')

    def decrypt(self, data):
        plaintext = kms.decrypt(CiphertextBlob=bytes(base64.b64decode(data)))
        return plaintext["Plaintext"].decode("utf-8")         

if __name__ == "__main__":
    os.environ["kmskey"] = "password-site"
    crypt = Crypto("password-site")
    print(crypt.kmskey)
    s = crypt.encrypt("this is my secret")
    print(s)
    d = crypt.decrypt(s)
    print(d)