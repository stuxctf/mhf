import os
import subprocess
from zipfile import ZipFile
from lib.Args import ArgsParse
from lib.Colors import GREEN, YELLOW, RESET, RED

bundletool_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "tools", "bundletool.jar"))
signer_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "tools", "uber-apk-signer-1.2.1.jar"))

def decom_aab():
    global args
    parse = ArgsParse()
    args=parse.getArgs()
    app = args.app_name
    output = os.path.splitext(app)[0] + "/"
    newapk = None
    print(f"{GREEN}\n[+] This application is a blunde app\n {RESET}")
    # define the command to extract the .aab
    command = ["java", "-jar", bundletool_path, "build-apks", "--mode=universal", "--bundle=" + app, "--output=" + output + ".apks"]
    issigned = subprocess.check_output(command, stderr=subprocess.STDOUT)

    os.rename(output + ".apks", output + ".zip")
    with ZipFile(output + '.zip', 'r') as zip_ref:
        zip_ref.extractall(output)
    
    #get the apk file name
    apk_files = [f for f in os.listdir(output) if f.endswith(".apk")]
    if len(apk_files) > 0:
        apk_file = apk_files[0]
        print(f"[INFO] The APK file extracted from the AAB file is: {apk_file} in the directory {output}")
        newapk = output + apk_file
    else:
        print("No APK file found in the extracted content")
    os.remove(output + '.zip')

    if "WARNING: The APKs won't be signed" in issigned.decode("utf-8", errors="ignore"):
        sign_apks = input(f"{YELLOW} \n[!] WARNING: The APKs won't be signed. Do you want to sign them? (y/n): {RESET}")
        if sign_apks.lower() == "y":
            signer_cmd = ["java", "-jar", signer_path , "--apk", output + apk_file]
            subprocess.run(signer_cmd)
    return newapk