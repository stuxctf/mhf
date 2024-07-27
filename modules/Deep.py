import os
import time
import sys
import tempfile
from xml.etree import ElementTree as ET
from tabulate import tabulate
from .Extract import extract_apk
from lib.Colors import RED, RESET

androtmp = ""
current_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

def extract_deep_links(manifest_path):
    tree = ET.parse(manifest_path)
    root = tree.getroot()
    
    deep_links = []

    for activity in root.findall(".//activity"):
        activity_name = activity.attrib.get("{http://schemas.android.com/apk/res/android}name", "")

        for intent_filter in activity.findall("intent-filter"):
            action = intent_filter.find("action")
            if action is not None and action.attrib.get("{http://schemas.android.com/apk/res/android}name") == "android.intent.action.VIEW":
                data_elements = intent_filter.findall("data")

                for data in data_elements:
                    scheme = data.attrib.get("{http://schemas.android.com/apk/res/android}scheme", "")
                    host = data.attrib.get("{http://schemas.android.com/apk/res/android}host", "")
                    path = data.attrib.get("{http://schemas.android.com/apk/res/android}path", "")
                    path_prefix = data.attrib.get("{http://schemas.android.com/apk/res/android}pathPrefix", "")
                    path_pattern = data.attrib.get("{http://schemas.android.com/apk/res/android}pathPattern", "")
                    auto_verify = intent_filter.attrib.get("{http://schemas.android.com/apk/res/android}autoVerify", "").lower() == "true"

                    if scheme and host:
                        if path_prefix or path_pattern:
                            deep_link = f"{scheme}://{host}{path_prefix}{path}{path_pattern}"
                        else:
                            deep_link = f"{scheme}://{host}/{path}"

                        if auto_verify:
                            deep_link_type = "App Links"
                        elif "http" in scheme or "https" in scheme:
                            deep_link_type = "Deep Links"
                        else:
                            deep_link_type = "Custom URL Schemes"

                        deep_links.append((activity_name, deep_link_type, deep_link))

    return deep_links

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

def display_deep_links():
    manifest_path = search_manifest_path(androtmp)
    
    if manifest_path:
        deep_links = extract_deep_links(manifest_path)
        if deep_links:
            print(f"{current_time} [INFO] Deep Links found in '{manifest_path}':\n")
            headers = ["Activity Name", "Deep Link Type", "Deep Link"]
            print(tabulate(deep_links, headers=headers, tablefmt="fancy_grid"))
        else:
            print(f"{current_time}{RED} [ERRR] No Deep Links found in '{manifest_path}'. {RESET}")
    else:
        print(f"{current_time}{RED} [ERRR] AndroidManifest.xml not found in '{androtmp}'. {RESET}")

if __name__ == "__main__":
    display_deep_links()