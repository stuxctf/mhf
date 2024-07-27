import os
import time
import sys
import tempfile
from xml.etree import ElementTree as ET
from tabulate import tabulate
from lib.Colors import RED, RESET
from .Extract import extract_apk

androtmp = ""
current_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

DANGEROUS_PERMISSIONS = {
    "android.permission.READ_CALENDAR",
    "android.permission.WRITE_CALENDAR",
    "android.permission.CAMERA",
    "android.permission.READ_CONTACTS",
    "android.permission.WRITE_CONTACTS",
    "android.permission.GET_ACCOUNTS",
    "android.permission.ACCESS_FINE_LOCATION",
    "android.permission.ACCESS_COARSE_LOCATION",
    "android.permission.RECORD_AUDIO",
    "android.permission.READ_PHONE_STATE",
    "android.permission.CALL_PHONE",
    "android.permission.READ_CALL_LOG",
    "android.permission.WRITE_CALL_LOG",
    "android.permission.ADD_VOICEMAIL",
    "android.permission.USE_SIP",
    "android.permission.PROCESS_OUTGOING_CALLS",
    "android.permission.BODY_SENSORS",
    "android.permission.SEND_SMS",
    "android.permission.RECEIVE_SMS",
    "android.permission.READ_SMS",
    "android.permission.RECEIVE_WAP_PUSH",
    "android.permission.RECEIVE_MMS",
    "android.permission.READ_EXTERNAL_STORAGE",
    "android.permission.WRITE_EXTERNAL_STORAGE",
}

def get_dangerous_permissions(manifest_path):
    tree = ET.parse(manifest_path)
    root = tree.getroot()
    
    permissions = []

    for elem in root.iter('uses-permission'):
        perm_name = elem.attrib.get('{http://schemas.android.com/apk/res/android}name')
        if perm_name in DANGEROUS_PERMISSIONS:
            permissions.append(perm_name)

    return permissions

def search_manifest_path(androtmp):
    stdout_orig = sys.stdout
    stderr_orig = sys.stderr
    sys.stdout = tempfile.TemporaryFile(mode='w+')
    sys.stderr = sys.stdout

    try:
        extracted = extract_apk(androtmp)
    except Exception:
        extracted = None

    sys.stdout = stdout_orig
    sys.stderr = stderr_orig

    if extracted is not None:
        for root, dirs, files in os.walk(extracted):
            if "AndroidManifest.xml" in files:
                file_path = os.path.join(root, "AndroidManifest.xml")
                return file_path
    return None

def display_dangerous_permissions():
    manifest_path = search_manifest_path(androtmp)
    

    if manifest_path:
        permissions = get_dangerous_permissions(manifest_path)
        
        if permissions:
            table_data = [[perm] for perm in permissions]
            print(tabulate(table_data, headers=["Dangerous Permissions"], tablefmt="fancy_grid"))
        else:
            print(f"{current_time} {RED}[INFO] No dangerous permissions found in the AndroidManifest.xml file. {RESET}")
    else:
        print(f"{current_time} {RED}[ERR] No valid AndroidManifest.xml file found for analysis. {RESET}")