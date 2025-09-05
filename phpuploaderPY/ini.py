# ini io
#globals
g_url = ""
g_psw = ""
g_sepSize = 0
g_batchTime = 0
g_targetPath= [""] * 5
g_targetPaths = 0

def ini_read():
    global g_url, g_psw, g_sepSize, g_targetPath, g_targetPaths
    try:
        with open("prof.ini", "r", encoding="utf-8") as f:
            lines = f.readlines()
            if len(lines) >= 3:
                g_url = lines[0].strip()
                g_psw = lines[1].strip()
                g_sepSize = int(lines[2].strip())
                g_batchTime = int(lines[3].strip())
                g_targetPath = [line.strip() for line in lines[4:] if line.strip()]
                g_targetPaths = len(g_targetPath)
    except FileNotFoundError:
        print("ini file not found, using defaults")
    except Exception as e:
        print(f"Error reading ini file: {e}")


def ini_write():
    global g_url, g_psw, g_sepSize, g_targetPath, g_targetPaths
    g_targetPaths = len(g_targetPath)
    try:
        with open("prof.ini", "w", encoding="utf-8") as f:
            f.write(f"{g_url}\n")
            f.write(f"{g_psw}\n")
            f.write(f"{g_sepSize}\n")
            f.write(f"{g_batchTime}\n")
            for path in g_targetPath:
                f.write(f"{path}\n")
    except Exception as e:
        print(f"Error writing ini file: {e}")

                    