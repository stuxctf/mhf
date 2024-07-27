import re
import jsbeautifier
import yaml
import os
import time
from lib.Colors import YELLOW, CYAN, MAGENTA, RESET, WHITE, GREEN 
from .Extract import extract_apk, extract_ipa
from .Plugins import get_plugins_info
from .Permissions import display_dangerous_permissions
from .Deep import display_deep_links
from .Exported import display_exported_components
from .Protections import get_protections
from .Security import get_security

ipatmp = ""
androtmp = ""
current_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

def cordova_android():
    search = input(f"{CYAN}\nDo you want to look for possible interesting information in the bundle file associated with the application? (Y/n): {RESET}")
    if search.lower() != "n":
        extracted = extract_apk(androtmp)
        cordova(extracted)

        #Extract permission information on the manifest 
        print(f"\n{current_time} {CYAN}[CHK] Getting information from the application manifest  {RESET}")
        print(f"{current_time} {MAGENTA}[CHK] Getting permission information  {RESET}")
        display_dangerous_permissions()

        print(f"\n{current_time} {MAGENTA}[CHK] Getting possible information about deeplinks  {RESET}")
        display_deep_links()

        print(f"\n{current_time} {MAGENTA}[CHK] Getting possible browseable components  {RESET}")
        display_exported_components()

        #Check Security and protections
        get_security()
        get_protections() 

def cordova_ios():
    search = input(f"{CYAN}\nDo you want to look for possible interesting information in the bundle file associated with the application? (Y/n): {RESET}")
    if search.lower() != "n":
        extracted = extract_ipa(ipatmp)
        cordova(extracted)

def beautify_js_files(extracted):
    print(f"{YELLOW}\n\t[DEBUG] Beautifying javascript files  {RESET}")
    is_beautified = False
    for root, dirs, files in os.walk(extracted):
        for file in files:
            if file.endswith(".js"):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, "r+", encoding="utf-8") as f:
                        content = f.read()
                        if not content.startswith("\n"):
                            f.seek(0)
                            f.write("\n" + content)
                            is_beautified = True
                        options = jsbeautifier.default_options()
                        beautified = jsbeautifier.beautify(content, options)
                        if beautified != content:
                            is_beautified = True
                            f.seek(0)
                            f.write(beautified)
                            f.truncate()
                except UnicodeDecodeError:
                    continue


def search_js(extracted):
    js_content = []
    file_paths = []
    for root, dirs, files in os.walk(extracted):
        if "css" in root  or "lib" in root or "plugins" in root:
            continue
        for file in files:
            if file.endswith(".js"):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        js_content.append(f.read())
                        file_paths.append(file_path)
                except UnicodeDecodeError:
                    continue
    return js_content, file_paths


def cordova(extracted):
        is_beautified = False
        if not is_beautified:
            beautifierjs = input(f"{CYAN}\n\tDo you want beautified all js files? (Y/n): {RESET}")
            if beautifierjs.lower() != "n":
                beautify_js_files(extracted)
                is_beautified = True
            search_js(extracted)

        if is_beautified or not is_beautified:           
            
            content, file_paths = search_js(extracted)

            #0xtract plugin information
            get_plugins_info()  

            #Extract sensitive IPs in the file 
            print(f"\n{current_time} {CYAN}[CHK] Searching IPs in js files\n  {RESET}")
            ip_pattern = re.compile(r"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b")
            for file_path, js_file_content in zip(file_paths, content):
                matches = re.findall(ip_pattern, js_file_content)
                if matches:
                    print(f"{MAGENTA}[INFO] {file_path}:  {RESET}" + f"{matches}")

            
            #Extract private keys in the js files
            print(f"\n{current_time} {CYAN}[CHK] Searching private keys in js files\n  {RESET}")
            private_key_pattern = re.compile(r"(-----BEGIN ((EC|PGP|DSA|RSA|OPENSSH) )?PRIVATE KEY( BLOCK)?-----)", re.DOTALL)
            for file_path, js_file_content in zip(file_paths, content):
                matches = re.findall(private_key_pattern, js_file_content)
                if matches:
                    print(f"{MAGENTA}[INFO] {file_path}:  {RESET}" + f"{matches}")
            
            #Extract emails in the js files
            print(f"\n{current_time} {CYAN}[CHK] Searching possible sensitive emails in js files\n  {RESET}")
            email_pattern = re.compile(r'[\w\.-]+@[\w\.-]+')
            for i, js_file_content in enumerate(content):
                emails = set()
                matches = re.findall(email_pattern, js_file_content)
                if matches:
                    for match in matches:
                        emails.add(match)
                    print(f"{MAGENTA}[INFO] Emails found in {file_paths[i]}:  {RESET}")
                    for email in emails:
                        print("\t" + email)

            #Search possible encryption fuctions
            print(f"\n{current_time} {CYAN}[CHK] Searching possible encryption functions in js files\n  {RESET}")         
            encryption_func_pattern = re.compile(r"CryptoJS\.enc|CryptoJS\.AES\.encrypt|CryptoJS\.AES\.decrypt|AES\.encrypt|AES\.decrypt")
            encrypted_func_found = False
            file_paths = []
            content, file_paths = search_js(extracted)
            for i, js_file_content in enumerate(content):
                matches = re.findall(encryption_func_pattern, js_file_content)
                if matches:
                    encrypted_func_found = True
                    print(f"{MAGENTA}[INFO] Encryption function found in file:", file_paths[i] + f"  {RESET}")
                    with open(file_paths[i], "r", encoding="utf-8") as f:
                        content = f.readlines()
                        for line_num, line in enumerate(content):
                            if encryption_func_pattern.search(line):
                                print(f"{MAGENTA}Line number", line_num + 1, ":", end=" ")
                                print(f"  {RESET}" + line.strip())       
            
            #Search high confidential secrets
            print(f"\n{current_time} {CYAN}[CHK] Searching high confidential secrets  {RESET}")         
            with open(os.path.abspath(os.path.join(os.path.dirname(__file__), "db", "high-confidence.yml"))) as f:
                secrets_patterns = yaml.safe_load(f)
            file_paths = []
            content, file_paths = search_js(extracted)
            for i, js_file_content in enumerate(content):
                for pattern in secrets_patterns['patterns']:
                    name = pattern['pattern']['name']
                    regex = pattern['pattern']['regex']
                    secrets_matches = re.findall(regex, js_file_content)
                    if secrets_matches:
                        file_paths.append(file_path)
                        print(f"{MAGENTA}\n[INFO] " + name + " identify: " + file_paths[i] +  f":  {RESET}" + str(secrets_matches))
                        
            #Search sensitive urls in the file
            print(f"\n{current_time} {CYAN}[CHK] Searching possible sensitive URLs in js files\n  {RESET}")
            url_pattern = re.compile(r"(?:https?://|www\.)\S+?\.\S+?[';\" ,]")
            omit_pattern = re.compile(r"(.*github.*)|(.*devexpress.*)|(.*mozilla.*)|(.*w3.*)|(.*webkit.*)|(.*csswg.*)|(.*angularjs.*)|(.*html5rocks.*)|(.*ionicframework.*)|(.*unicode.*)|(.*fb.*)|(.*wikipedia.*)|(.*jquery.*)|(.*example.*)|(.*apache.*)|(.*android.*)|(.*opensource.*)|(.*openxmlformats.*)|(.*angular.*)")
            files_with_results = 0  
            for i, js_file_content in enumerate(content):
                url_matches = re.findall(url_pattern, js_file_content)
                results_found = False
                for url in url_matches:
                    if not re.search(omit_pattern, url):
                        if not results_found:
                            print(f"{MAGENTA}[INFO] {file_paths[i]}:  {RESET}")
                            results_found = True
                            files_with_results += 1
                        print("\t" + url)
            
            #Search possible endpoints in the js files            
            print(f"\n{current_time} {CYAN}[CHK] Searching possible endpoints in js files\n  {RESET}")
            endpoint_pattern = re.compile(r"(?:\"|\u0027)(((?:[a-zA-Z]{1,10}://|//)[^\"\u0027/]{1,}\\.[a-zA-Z]{2,}[^\"\u0027]{0,})|((?:/|\.\./|\./)[^\"\u0027><,;| *()&$%#=\\\[\]]{1,})|([a-zA-Z0-9_\-/]{1,}/[a-zA-Z0-9_\-/]{1,}\.(?:[a-zA-Z]{1,4}|action)(?:[\\?|/][^\"|^\u0027]{0,}|))|([a-zA-Z0-9_\-]{1,}\.(?:php|asp|aspx|jsp|json|action|html|js|txt|xml)(?:\?[^\"|^\u0027]{0,}|)))(?:\"|\u0027)")

            # List of files to skip
            skip_files = {'native-bridge.js', 'cordova_plugins.js', 'cordova.js'}
            extensions = ('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.svg', '.json', '.js')

            endpoint = set()
            exported = False

            for i, js_file_content in enumerate(content):
                file_name = os.path.basename(file_paths[i])
                
                if file_name in skip_files:
                    print(f"{YELLOW}\t[INFO] Skipping file: {file_name}  {RESET}")
                    continue

                matches = re.findall(endpoint_pattern, js_file_content)
                if matches:
                    found = True
                    # Filter out endpoints ending with image extensions
                    endpoint = set(match[0] for match in matches if not match[0].startswith("./") and not match[0].lower().endswith(extensions))
                    with open("endpoints.txt", "a") as f:
                        for end in endpoint:
                            f.write(end + "\n")
                    if found:
                        print(f"{MAGENTA}\t[INFO] Endpoints found in the file: {file_paths[i]}  {RESET}")
                    else:
                        print(f"{WHITE}\t[INFO] No endpoints found in the file  {RESET}")

            print(f"{GREEN}\t[INFO] Endpoints exported to endpoints.txt  {RESET}")