from functions.custom.aes_crypt import AESCrypt
from functions.custom.des_crypt import DESCrypt, DES3Crypt
from urllib.parse import quote_plus, unquote_plus, quote, unquote
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5
import base64


# AES加密并编码成字符串
def aes_encode_to_string(string='', key='', iv='', mode='ECB'):
    obj = AESCrypt(key=key, iv=iv, mode=mode)
    aes_str = obj.aes_encode(string)
    return obj.byte_to_string(aes_str)


# AES加密并编码成字符串对应解密方法
def aes_decode_from_string(string='', key='', iv='', mode='ECB'):
    obj = AESCrypt(key=key, iv=iv, mode=mode)
    aes_str = obj.string_to_byte(string)
    return obj.aes_decode(aes_str)


# AES加密并进行base64编码
def aes_encode_to_b64(string='', key='', iv='', mode='ECB'):
    obj = AESCrypt(key=key, iv=iv, mode=mode)
    aes_str = obj.aes_encode(string)
    return base64.b64encode(aes_str).decode('utf8', errors='ignore')


# AES加密并进行base64编码对应解密方法
def aes_decode_from_b64(string='', key='', iv='', mode='ECB'):
    obj = AESCrypt(key=key, iv=iv, mode=mode)
    aes_str = base64.b64decode(string)
    return obj.aes_decode(aes_str)


# AES加密并进行base64编码后再URLEncode
def aes_encode_to_b64_url_encode(string='', key='', iv='', mode='ECB'):
    obj = AESCrypt(key=key, iv=iv, mode=mode)
    aes_str = obj.aes_encode(string)
    return quote_plus(base64.b64encode(aes_str))


# AES加密并进行base64编码后再URLEncode对应解密方法
def aes_decode_from_b64_url_encode(string='', key='', iv='', mode='ECB'):
    obj = AESCrypt(key=key, iv=iv, mode=mode)
    aes_str = base64.b64decode(unquote_plus(string))
    return obj.aes_decode(aes_str)


# DES加密并进行base64编码
def des_encode_to_b64(string='', key='', iv='', mode='ECB'):
    obj = DESCrypt(key=key, iv=iv, mode=mode)
    des_str = obj.des_encode(string)
    return base64.b64encode(des_str).decode('utf8', errors='ignore')


# DES加密并进行base64编码对应解密方法
def des_decode_from_b64(string='', key='', iv='', mode='ECB'):
    obj = DESCrypt(key=key, iv=iv, mode=mode)
    des_str = base64.b64decode(string)
    return obj.des_decode(des_str)


# DES加密并进行base64编码后再URLEncode
def des_encode_to_b64_url_encode(string='', key='', iv='', mode='ECB'):
    obj = DESCrypt(key=key, iv=iv, mode=mode)
    des_str = obj.des_encode(string)
    return quote(base64.b64encode(des_str))


# DES加密并进行base64编码后再URLEncode对应解密方法
def des_decode_from_b64_url_encode(string='', key='', iv='', mode='ECB'):
    obj = DESCrypt(key=key, iv=iv, mode=mode)
    des_str = base64.b64decode(unquote(string))
    return obj.des_decode(des_str)


# DES3加密并进行base64编码
def des3_encode_to_b64(string='', key='', iv='', mode='ECB'):
    obj = DES3Crypt(key=key, iv=iv, mode=mode)
    des3_str = obj.des3_encode(string)
    return base64.b64encode(des3_str).decode('utf8', errors='ignore')


# DES3加密并进行base64编码对应解密方法
def des3_decode_from_b64(string='', key='', iv='', mode='ECB'):
    obj = DES3Crypt(key=key, iv=iv, mode=mode)
    des3_str = base64.b64decode(string)
    return obj.des3_decode(des3_str)


# DES3加密并进行base64编码后再URLEncode
def des3_encode_to_b64_url_encode(string='', key='', iv='', mode='ECB'):
    obj = DES3Crypt(key=key, iv=iv, mode=mode)
    des3_str = obj.des3_encode(string)
    return quote(base64.b64encode(des3_str))


# DES3加密并进行base64编码后再URLEncode对应解密方法
def des3_decode_from_b64_url_encode(string='', key='', iv='', mode='ECB'):
    obj = DES3Crypt(key=key, iv=iv, mode=mode)
    des3_str = base64.b64decode(unquote(string))
    return obj.des3_decode(des3_str)


# RSA加密并进行base64编码
def rsa_encode_to_b64(string='', key='../static/jushi_pub.key', iv='', mode='200'):
    with open(key, 'r') as pub_file:
        pub_key = PKCS1_v1_5.new(RSA.importKey(pub_file.read()))
    res = []
    for i in range(0, len(string), int(mode)):
        res.append(pub_key.encrypt(string[i:i+int(mode)].encode('utf8', errors='ignore')))
    return base64.b64encode(b"".join(res)).decode('utf8', errors='ignore')


# RSA加密并进行base64编码对应解密方法
def rsa_decode_from_b64(string='', key='../static/pri_6615126990652570.key', iv='', mode='256'):
    with open(key, 'r') as pvt_file:
        pvt_key = PKCS1_v1_5.new(RSA.importKey(pvt_file.read()))
    res = []
    string = base64.b64decode(string)
    for i in range(0, len(string), int(mode)):
        res.append(pvt_key.decrypt(string[i:i+int(mode)], 'xyz'))
    text = b"".join(res)
    return text if isinstance(text, str) else text.decode('utf8', errors='ignore')
