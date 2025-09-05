# python GUI for file uploader to php server
# サーバーメンテナンスツール Windows Server Maintenance Tools
# (c)Teamwind japan h.hayashi

# Python環境のPyPIにて下記インストールしました
# tkinterdnd2ライブラリインストール
# pyzipperライブラリインストール (パスワード付きzip圧縮用)
# requestsライブラリインストール (ファイルアップロード用)

from pydoc import text
import tkinter as tk
from tkinterdnd2 import TkinterDnD, DND_FILES
import tkinter.ttk as ttk
import asyncio
import os
import time
import threading

#-------------------------------------------------------------------------------------
# import my code
import ini
import zipfolder
import md5
import uploadFile

#-------------------------------------------------------------------------------------
# スレッド用実行指示フラグ
f_Go = False

#timer用処理実行フラグ
f_timerGo = False

#次回実行時間
next_exec_time = None

#-------------------------------------------------------------------------------------
# GUI設定　
root = TkinterDnD.Tk()
root.geometry("350x450")

#タイトル
root.title("php uploaderPY (c)Teamwind jp")  

#-------------------------------------------------------------------------------------
# 処理開始ボタンのイベント
def batchStart():
    global f_timerGo, next_exec_time, button
    global ini, txfolders, txurl, cbcutsize, txpsw, batchtime

    if f_timerGo == True:
        # タイマー処理中は停止
        f_timerGo = False
        # 開始表示
        button.config(text = "開始")
    else:
        # 最初から始める　

        # iniに保存
        # url
        ini.g_url = txurl.get()
        # folders
        ini.g_targetPaths = 0
        ini.g_targetPath= [""] * 5
        for i in range(len(txfolders)):
            path = txfolders[i].get()
            if os.path.exists(path) and os.path.isdir(path):
                ini.g_targetPath[i] = path
                ini.g_targetPaths += 1
            else:
                ini.g_targetPath[i] = ""
        # cut size
        ini.g_sepSize = int(cbcutsize.get())
        # psw
        ini.g_psw = txpsw.get()
        # batch time
        if batchtime.get() == "now":
            ini.g_batchTime = -1
        else:
            ini.g_batchTime = int(batchtime.get())

        # 入力チェック
        if ini.g_url == "":
            button.config(text="URLがありません")
            return
        if ini.g_targetPaths == 0:
            button.config(text="フォルダがありません")
            return
        # 保存
        ini.ini_write()

        # 次回実行時間をクリア
        next_exec_time = None
        # タイマー有効化
        f_timerGo = True

#-------------------------------------------------------------------------------------
# フォルダドロップイベントの処理
def on_drop(event, textbox):
    if os.path.exists(event.data) and os.path.isdir(event.data):
        # ドロップされたフォルダパスをテキストボックスに表示
        textbox.delete(0, tk.END)
        textbox.insert(0, event.data)

#-------------------------------------------------------------------------------------
# コンテンツ配置
yStep = 0
def getNextYpos():
    global yStep
    yStep += 25
    return yStep

# コンテンツ配置
# URL入力欄
label = tk.Label(root, text="upload URL [http://yourphpserver/receive.php]")
label.place(x=10, y = getNextYpos())
txurl = tk.Entry(width=50)
txurl.place(x=10, y =  getNextYpos())

# バックアップ対象フォルダ入力欄
label = tk.Label(root, text="drop backup folder")
label.place(x=10, y = getNextYpos())

# バックアップ対象フォルダ
txfolders = [tk.Entry(width=50), tk.Entry(width=50), tk.Entry(width=50), tk.Entry(width=50), tk.Entry(width=50)]
for tx in txfolders:
    tx.place(x=10, y = getNextYpos())
    tx.drop_target_register(DND_FILES)
    tx.dnd_bind('<<Drop>>', lambda event, tb=tx: on_drop(event, tb))

# カットサイズ
label = tk.Label(root, text="cut size (Mbyte)")
label.place(x=10, y = getNextYpos())
# コンボボックス
cutsize = []
for i in range(256):
    cutsize.append(i + 1)
cbcutsize = ttk.Combobox(root, state="readonly", values=cutsize, width=10)
cbcutsize.place(x=10, y = getNextYpos())

# zip password
label = tk.Label(root, text="zip password")
label.place(x=10, y = getNextYpos())
txpsw = tk.Entry(width=50)
txpsw.place(x=10, y = getNextYpos())

# バッチ処理時刻
label = tk.Label(root, text="start hour")
label.place(x=10, y = getNextYpos())
# コンボボックス
batchtime = []
batchtime.append("now")
for i in range(0,24):
    batchtime.append(i)
batchtime = ttk.Combobox(root, state="readonly", values=batchtime, width=10)
batchtime.place(x=10, y = getNextYpos())

# 開始ボタン
button = tk.Button(root, text="開始", command=batchStart, width=20)  
button.place(x=10, y = getNextYpos())

#-------------------------------------------------------------------------------------
#ini read
ini.ini_read()

# iniからセット
# url
txurl.insert(0, ini.g_url)
# folders
for i in range(ini.g_targetPaths):
    if i < len(txfolders):
        txfolders[i].insert(0, ini.g_targetPath[i])
# cut size
if 1 <= ini.g_sepSize <= 256:
    cbcutsize.set(ini.g_sepSize )
else:
    cbcutsize.set(1)
# zip psw
txpsw.insert(0, ini.g_psw)
# batch time
if 1 <= ini.g_batchTime <= 24:
    batchtime.set(ini.g_batchTime - 1)
else:
    batchtime.set("now")


#-------------------------------------------------------------------------------------
# スレッド処理
def mainThread():

    global f_Go, f_timerGo, button, batchtime

    print("スレッド開始")

    while True:

        # 開始指示判定
        if f_Go == True:

            print("スレッド処理Start")

            #開始
            button.config(text="処理中")

            # フォルダ毎に処理
            for i in range(ini.g_targetPaths):
                path = ini.g_targetPath[i]
                if os.path.exists(path) and os.path.isdir(path):
                    # zip化
                    zipfolder.zipFolder(path, path + ".zip", ini.g_psw)
                    #print(path + ".zip")
                    # zipのmd5値取得
                    zipMD5 = md5.getFileMD5(path + ".zip")
                    # zip分割
                    if ini.g_sepSize >= 1:
                        sepSize = ini.g_sepSize * 1024 * 1024
                    else:
                        sepSize = 10 * 1024 * 1024
                    # zip分割ファイル名とmd5値保管
                    partFilenames = []
                    partFileMD5s = []
                    # 分割ファイル数
                    part_num = 0
                    # 分割
                    if os.path.getsize(path + ".zip") > sepSize:
                        with open(path + ".zip", "rb") as f:
                            while True:
                                chunk = f.read(sepSize)
                                if not chunk:
                                    break
                                partFilenames.append(path + f".zip.{part_num:03d}")
                                with open(partFilenames[part_num], "wb") as part_file:
                                    part_file.write(chunk)
                                # 分割ファイルのmd5値取得
                                partFileMD5s.append(md5.getFileMD5(partFilenames[part_num]))
                                # 分割数
                                part_num += 1
                    else:
                        # 分割しない場合はそのままリネーム
                        partFilenames.append(path + ".zip.000")
                        try:
                            os.remove(partFilenames[0])
                        except :              
                            pass
                        os.rename(path + ".zip", partFilenames[0] )
                        # 分割ファイルのmd5値取得
                        partFileMD5s.append(md5.getFileMD5(partFilenames[0]))
                        # 分割数
                        part_num += 1

                    # 分割ファイルアップロード
                    for j in range(part_num):
	                    # prmを生成  zipファイル名+分割番号,分割番号,最終分割番号,当該md5,結合したzipのmd5
                        # url+"?prm=abc.zip.000,2,xxxxxxxxxxxxxxxxxxxx(md5値),xxxxxxxxxxxxxxxxxxxx(md5値)"

                        # ファイル名
                        prm = f"?prm={os.path.basename(partFilenames[j])},{j},{part_num - 1},{partFileMD5s[j]},{zipMD5}"
                        uploadFile.upload(ini.g_url+prm, partFilenames[j])
                        # 分割ファイル削除
                        try:
                            os.remove(partFilenames[j])
                        except Exception as e:
                            print(f"Error deleting part file: {e}")




                    # upload
                    #import uploader
                    #uploader.uploadFile(ini.g_url, "backup.zip", ini.g_psw, ini.g_sepSize)
                    continue
                    # zip削除
                    try:
                        os.remove("backup.zip")
                    except Exception as e:
                        print(f"Error deleting zip file: {e}")
                    

            # zip


            print("スレッド処理End")

            #次の指示を待つ
            f_Go = False

            # now以外はタイマー有効化
            if batchtime.get() != "now":
               f_timerGo = True

            button.config(text="開始")


        #print("スレッドループ")
        time.sleep(1)
    

    print("スレッド終了")



#-------------------------------------------------------------------------------------
# タイマーイベント処理
# タイマーはバッチ開始時刻判定用にループしています。
# 1回のみのnow指定の場合は、f_timerGo=Falseにして判定をスキップ(無効)しています。


# 次回実行時間の設定
# hour: 0-23
def set_next_exec_time(hour):
        global next_exec_time
        try:
            from datetime import datetime, timedelta
            now = datetime.now()
            next_exec_time = now.replace(hour=hour, minute=0, second=0, microsecond=0)
            if next_exec_time <= now:
                next_exec_time += timedelta(days=1)
            print("next exec time set to " + next_exec_time.strftime("%Y-%m-%d %H:%M:%S"))
        except ValueError:
            print("Invalid hour value")
            next_exec_time = None

def timer_task():

    # 次回実行時刻
    global next_exec_time, f_Go, button, f_timerGo

    # timer有効判定
    if f_timerGo == False:
        #無効なのでbye
        root.after(1000, timer_task)  
        return

    #print("on timer")

    # 次回実行時間が未設定なら設定
    if next_exec_time is None:
        #初回なので次回実行時間を今に設定
        from datetime import datetime
        next_exec_time = datetime.now()

    # バッチ時刻判定
    from datetime import datetime
    now = datetime.now()

    #print("check")

    if now >= next_exec_time:

        # 次回実行時間に到達したのでスレッドに処理開始を指示
        f_Go = True

        # タイマーは無効にする
        f_timerGo = False

        #次回実行時間を設定
        if batchtime.get() == "now":
            # 1回のみの処理なので処理時刻は消す
            next_exec_time = None
        else:
            # 次回時刻を設定
            set_next_exec_time(int(batchtime.get()))
    else:
        # 未到達なので次回時刻を表示
        button.config(text="次回 " + next_exec_time.strftime("%d日 %H時"))

    #print("on timer")

    # ループ継続
    root.after(1000, timer_task)  

    
#-------------------------------------------------------------------------------------
# メインループ

# スレッドの作成
thread = threading.Thread(target=mainThread)
# スレッドの開始
thread.start()

#timer on
root.after(1000, timer_task)  

# tkinter loop
root.mainloop()

