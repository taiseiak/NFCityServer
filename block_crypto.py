from Crypto.Hash import SHA256
from Crypto.Cipher import AES
from hashlib import md5
from base64 import b64decode
from base64 import b64encode
from Crypto import Random
import sys

pi_seed = 'NFCITYPI'

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
    Tested under Python 3 and PyCrypto 2.6.1.
    """

    def __init__(self, key):
        # self.key = md5(key.encode('utf8')).hexdigest()
        self.key = md5(key).hexdigest()

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


def create_check_hash(ciphertext, seed):
    return md5(ciphertext + '||' + seed).hexdigest()


def decrypt_json(hashvalue, ciphertext, machine):
    """Encrypts json sent from a source with they key

    Returns:
        dictionary with json
    """
    machines = {'pi': 'seedfilepi.txt',
                'dragon': 'seedfiledragon.txt'}
    seedfile = machines[machine]
    with open(seedfile) as seedfile_in:
        seed = seedfile_in.read()
    check_hash = create_check_hash(ciphertext, seed)
    if check_hash != hashvalue:
        raise ValueError('Hashvalues not equal')
    hashk = SHA256.new()
    hashk.update(seed)
    hashkey = hashk.digest()
    return AESCipher(hashkey).decrypt(ciphertext)
