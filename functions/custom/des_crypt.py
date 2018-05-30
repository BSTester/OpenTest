from Crypto.Cipher import DES, DES3


# DES加解密算法
class DESCrypt(object):
    def __init__(self, key='', iv='', mode='ECB'):
        # DES配置
        self.key = key  # 密钥
        self.iv = iv   # 向量
        if mode == 'ECB':
            self.mode = DES.MODE_ECB
        elif mode == 'CBC':
            self.mode = DES.MODE_CBC
        self.bs = DES.block_size
        self.pad = lambda s: s + (self.bs - len(s) % self.bs) * chr(self.bs - len(s) % self.bs)
        self.unpad = lambda s: s[0:-ord(s[-1])]

    # DES加密
    def des_encode(self, messages):
        if self.mode == DES.MODE_ECB:
            obj = DES.new(self.key, self.mode)
        else:
            obj = DES.new(self.key, self.mode, self.iv)
        return obj.encrypt(self.pad(messages))

    # DES解密
    def des_decode(self, des_str):
        if self.mode == DES.MODE_ECB:
            obj = DES.new(self.key, self.mode)
        else:
            obj = DES.new(self.key, self.mode, self.iv)
        return self.unpad(obj.decrypt(des_str).decode('utf8', errors='ignore'))

    # DES加密后字节码编码成字符串
    def byte_to_string(self, des_str):
        des_str = bytearray(des_str)
        buf = bytearray()
        for i in range(len(des_str)):
            buf.append(((des_str[i] >> 4) & 0xF) + ord('a'))
            buf.append((des_str[i] & 0xF) + ord('a'))
        return bytes(buf).decode('utf8', errors='ignore')

    # 字符串解码成DES加密后字节码
    def string_to_byte(self, string):
        string = bytearray(string.encode('utf8', errors='ignore'))
        buf = bytearray()
        for i in range(0, len(string), 2):
            buf.append((((string[i] - ord('a')) & 0xF) << 4) + ((string[i+1] - ord('a')) & 0xF))
        return bytes(buf)


# DES3加解密算法
class DES3Crypt(object):
    def __init__(self, key='', iv='', mode='ECB'):
        # DES3配置
        self.key = key  # 密钥
        self.iv = iv   # 向量
        if mode == 'ECB':
            self.mode = DES3.MODE_ECB
        elif mode == 'CBC':
            self.mode = DES3.MODE_CBC
        self.bs = DES3.block_size
        self.pad = lambda s: s + (self.bs - len(s) % self.bs) * chr(self.bs - len(s) % self.bs)
        self.unpad = lambda s: s[0:-ord(s[-1])]

    # DES3加密
    def des3_encode(self, messages):
        if self.mode == DES3.MODE_ECB:
            obj = DES3.new(self.key, self.mode)
        else:
            obj = DES3.new(self.key, self.mode, self.iv)
        return obj.encrypt(self.pad(messages))

    # DES3解密
    def des3_decode(self, des3_str):
        if self.mode == DES3.MODE_ECB:
            obj = DES3.new(self.key, self.mode)
        else:
            obj = DES3.new(self.key, self.mode, self.iv)
        return self.unpad(obj.decrypt(des3_str).decode('utf8', errors='ignore'))

    # DES3加密后字节码编码成字符串
    def byte_to_string(self, des3_str):
        des3_str = bytearray(des3_str)
        buf = bytearray()
        for i in range(len(des3_str)):
            buf.append(((des3_str[i] >> 4) & 0xF) + ord('a'))
            buf.append((des3_str[i] & 0xF) + ord('a'))
        return bytes(buf).decode('utf8', errors='ignore')

    # 字符串解码成DES3加密后字节码
    def string_to_byte(self, string):
        string = bytearray(string.encode('utf8', errors='ignore'))
        buf = bytearray()
        for i in range(0, len(string), 2):
            buf.append((((string[i] - ord('a')) & 0xF) << 4) + ((string[i+1] - ord('a')) & 0xF))
        return bytes(buf)
