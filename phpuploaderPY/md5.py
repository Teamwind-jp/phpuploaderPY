import hashlib

def getFileMD5(path):
    # MD5ハッシュオブジェクトを作成
    md5_hash = hashlib.md5()
    # バイナリモードでopen
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            md5_hash.update(chunk)
    
    # 16進数
    return md5_hash.hexdigest()

