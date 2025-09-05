import hashlib

def getFileMD5(path):
    # MD5�n�b�V���I�u�W�F�N�g���쐬
    md5_hash = hashlib.md5()
    # �o�C�i�����[�h��open
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            md5_hash.update(chunk)
    
    # 16�i��
    return md5_hash.hexdigest()

