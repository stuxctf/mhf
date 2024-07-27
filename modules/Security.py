import os
import sys
import subprocess
import time
from lib.Colors import CYAN, RED, RESET 
from lib.Args import ArgsParse

def run_apkid(apk_file):
    """Run apkid and print the output."""
    try:
        subprocess.run(["apkid", apk_file], check=True)
    except subprocess.CalledProcessError as e:
        print(f"\n{current_time} {RED}[ERR] apkid failed with error code {e.returncode}. Output:\n{e.output} {RESET}")

def get_security():
    current_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    print(f"\n{current_time} {CYAN}[CHK] Identifies many compilers, packers, obfuscators with APKiD {RESET}")
    global args
    parse = ArgsParse()
    args=parse.getArgs()
    app = args.app_name

    app_name = args.app_name
    if not app_name.endswith('.apk'):
        print(f"{current_time} {RED}[ERR] Not a valid APK file {app_name} {RESET}")
        return 

    run_apkid(app_name)