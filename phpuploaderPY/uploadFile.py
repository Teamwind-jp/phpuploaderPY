import requests


def upload(url, path):
    #url = "http://localhost:8000/md5.php"
    files = {"file": open(path, "rb")}
    response = requests.post(url, files=files)
    return response.text
