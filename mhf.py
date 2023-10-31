#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from lib.Args import ArgsParse
from lib.Banner import mhf_banner
from zipfile import ZipFile
from lib.FrameworkClass import FrameWork, tech_list
from lib.Colors import GREEN, RESET ,RED
from modules.Aab import decom_aab
from modules.React import react_android, react_ios
from modules.Cordova import cordova_ios_apk
from modules.Flutter import patch_apk
from modules.Xamav1 import xama_andorid, xama_ios
from modules.Xamav2 import xama_blob

args = {}

def main():
    global args
    parse = ArgsParse()
    args = parse.getArgs()
    try:
        if args.app_name.endswith('.aab'):
            newapk = decom_aab()
            if not newapk == None:
                args.app_name = newapk
            else:
                exit

        with ZipFile(args.app_name, 'r') as zipObject:
            file_names = zipObject.namelist()
            for file_name in file_names:
                for tech in tech_list:
                    for directory in tech.directories:
                        if file_name.find(directory) != -1:
                            zipObject.close()
                            print(f"{GREEN}\n[+] App was written in {tech.framework} {RESET}")
                            if tech.framework in [FrameWork.REACT_NATIVE]:
                                react_android()
                            if tech.framework in [FrameWork.REACT_NATIVE_IOS]:
                                react_ios()
                            if tech.framework in [FrameWork.NATIVESCRIPT]:
                                cordova_ios_apk()
                            if tech.framework in [FrameWork.FLUTTER, FrameWork.FLUTTER_IOS]:
                                patch_apk()
                            if tech.framework in [FrameWork.CORDOVA]:
                                cordova_ios_apk()
                            if tech.framework in [FrameWork.XAMARIN_BLOB]:
                                xama_blob()
                            if tech.framework in [FrameWork.XAMARIN]:
                                xama_andorid()
                            if tech.framework in [FrameWork.XAMARIN_IOS]:
                                xama_ios()
                            return
                        else:
                            continue
            # if no framework is found, return Native
            zipObject.close()
            if args.app_name.endswith('.apk'):
                print(f"{GREEN}[+] App was written in {FrameWork.NATIVE}")
            else:
                print(f"[+] App was written in {FrameWork.NATIVE_IOS} ")
    except:
        print(f"{RED}[+] ERROR: Check the application path {RESET}")
if __name__ == '__main__':
    mhf_banner()
    main()