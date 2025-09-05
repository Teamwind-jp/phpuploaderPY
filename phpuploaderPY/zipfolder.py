import os
import pyzipper

def zipFolder(folder_path, zip_path, password):

        # パスワード付きで圧縮 (AES暗号化)
        with pyzipper.AESZipFile(zip_path, 'w', compression=pyzipper.ZIP_DEFLATED) as zipf:
            if password.strip() != "":
                zipf.setencryption(pyzipper.WZ_AES, nbits=256)
                zipf.setpassword(password.encode('utf-8'))
            for root, _, files in os.walk(folder_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, folder_path)
                    zipf.write(file_path, arcname)
                    print(file_path)








