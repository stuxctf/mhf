import os
import subprocess
from zipfile import ZipFile
from lib.Args import ArgsParse

apktool_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "tools", "apktool_2.8.1.jar"))
androtmp = ""
ipatmp = ""

def extract_apk(androtmp):
    global args
    parse = ArgsParse()
    args=parse.getArgs()
    app = args.app_name
    
    androtmp = os.path.splitext(app)[0]
    if os.path.exists(androtmp):
        print("\nOutput directory already exists. Skipping decompilation.")
    else:
        print(f"\nDecompiling application {app}")
        apktool_cmd = ["java", "-jar", apktool_path , "d", app , "-f", "-o", androtmp]
        subprocess.run(apktool_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return (androtmp)

def extract_ipa(ipatmp):
    global args
    parse = ArgsParse()
    args=parse.getArgs()
    app = args.app_name

    zip_filename = os.path.splitext(app)[0] + ".zip"
   
    ipatmp = os.path.splitext(zip_filename)[0]
    if os.path.exists(ipatmp):
        print("\nOutput directory already exists. Skipping decompilation.")
    else:
        print(f"\nDecompiling application {app}")
        os.rename(app, zip_filename)
        os.makedirs(ipatmp)
        
        with ZipFile(zip_filename, "r") as zip_ref:
            zip_ref.extractall(ipatmp)
        
        app = os.path.splitext(zip_filename)[0] + ".ipa"
        os.rename(zip_filename, app)
    return ipatmp