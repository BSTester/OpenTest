from Crypto.Cipher import AES


# AES加解密算法
class AESCrypt(object):
    def __init__(self, key='', iv='', mode='ECB'):
        # AES配置
        self.key = key  # 密钥
        self.iv = iv   # 向量
        if mode == 'ECB':
            self.mode = AES.MODE_ECB
        elif mode == 'CBC':
            self.mode = AES.MODE_CBC
        self.bs = AES.block_size
        self.pad = lambda s: s + (self.bs - len(s) % self.bs) * chr(self.bs - len(s) % self.bs)
        self.unpad = lambda s: s[0:-ord(s[-1])]

    # AES加密
    def aes_encode(self, messages):
        if self.mode == AES.MODE_ECB:
            obj = AES.new(self.key, self.mode)
        else:
            obj = AES.new(self.key, self.mode, self.iv)
        return obj.encrypt(self.pad(messages))

    # AES解密
    def aes_decode(self, aes_str):
        if self.mode == AES.MODE_ECB:
            obj = AES.new(self.key, self.mode)
        else:
            obj = AES.new(self.key, self.mode, self.iv)
        return self.unpad(obj.decrypt(aes_str).decode('utf8', errors='ignore'))

    # AES加密后字节码编码成字符串
    def byte_to_string(self, aes_str):
        aes_str = bytearray(aes_str)
        buf = bytearray()
        for i in range(len(aes_str)):
            buf.append(((aes_str[i] >> 4) & 0xF) + ord('a'))
            buf.append((aes_str[i] & 0xF) + ord('a'))
        return bytes(buf).decode('utf8', errors='ignore')

    # 字符串解码成AES加密后字节码
    def string_to_byte(self, string):
        string = bytearray(string.encode('utf8', errors='ignore'))
        buf = bytearray()
        for i in range(0, len(string), 2):
            buf.append((((string[i] - ord('a')) & 0xF) << 4) + ((string[i+1] - ord('a')) & 0xF))
        return bytes(buf)
