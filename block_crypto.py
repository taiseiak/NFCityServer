from Crypto.Hash import SHA256
from Crypto.Cipher import AES
from hashlib import md5
from base64 import b64decode
from base64 import b64encode
from Crypto import Random
import json
import sys

# Padding for the input string --not
# related to encryption itself.
BLOCK_SIZE = 16  # Bytes
pad = lambda s: s + (BLOCK_SIZE - len(s) % BLOCK_SIZE) * \
                    chr(BLOCK_SIZE - len(s) % BLOCK_SIZE)
unpad = lambda s: s[:-ord(s[len(s) - 1:])]


class AESCipher:
    """
    Usage:
        c = AESCipher('password').encrypt('message')
        m = AESCipher('password').decrypt(c)
    Tested under Python 2 and PyCrypto 2.6.1.
    """

    def __init__(self, key):
        # self.key = md5(key.encode('utf8')).hexdigest()
        #self.key = md5(key).hexdigest()
        ##hacky solution
        self.key = 'hackathongsu2017'

    def encrypt(self, raw):
        raw = pad(raw)
        iv = Random.new().read(AES.block_size)
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return b64encode(iv + cipher.encrypt(raw))

    def decrypt(self, enc):
        enc = b64decode(enc)
        iv = enc[:16]
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return unpad(cipher.decrypt(enc[16:])).decode('utf8')


def decrypt_json(hashvalue, ciphertext, machine):
    """Encrypts json sent from a source with they key

    Returns:
        dictionary with json
    """
    return AESCipher('hackathongsu2017').decrypt(ciphertext)


def main():
    with open('hashjson', 'r') as infile:
        data = json.load(infile)
    ciphertext = data["ciphertext"]
    hashvalue = data["hashvalue"]
    return_json = decrypt_json(hashvalue, ciphertext, 'pi')
    open('hashjson', 'w').close()
    return return_json


if __name__ == "__main__":
    main()
