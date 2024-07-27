import os
import magic
import re
import jsbeautifier
import yaml
import time
from lib.Colors import CYAN, YELLOW, MAGENTA, GREEN, WHITE, RESET
from .Extract import extract_apk, extract_ipa
from .Permissions import get_dangerous_permissions

ipatmp = ""
androtmp = ""
current_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

def react_android():
    search = input(f"{CYAN}\nDo you want to look for possible interesting information in the bundle file associated with the application? (Y/n): {RESET}")
    if search.lower() != "n":
        extracted = extract_apk(androtmp)
        react(extracted, "index.android.bundle")
        
def react_ios():
    search = input(f"{CYAN}\nDo you want to look for possible interesting information in the bundle file associated with the application? (Y/n): {RESET}")
    if search.lower() != "n":
        extracted = extract_ipa(ipatmp)
        react(extracted, "main.jsbundle")


def react(extracted,search_file ):
   
    for root, dirs, files in os.walk(extracted):
        for file in files:
            if file == search_file:
                file_path = os.path.join(root, file)
                file_type = magic.from_file(file_path)
                
                # Detect if is hermes enable
                if file_type == "data" or "Hermes" in file_type:
                    print(
                        f"\nThe file {file} is optimized with Hermes and this is not soported for operations in this tool.\n\n Read for more information consult:\n\nhttps://suam.wtf/posts/react-native-application-static-analysis-en/\nhttps://github.com/bongtrop/hbctool")
                else:

                    # Beauty the react code
                    search = input(f"{CYAN}\nDo you want beautified the react code? (Y/n): {RESET}")
                    if search.lower() != "n":
                        print(f"{YELLOW}\n\t[DEBUG] Using jsbeautifier in the {file} {RESET}")
                        with open(file_path, "r") as f:
                            content = f.read()
                            beautified_content = jsbeautifier.beautify(content)
                        with open(file_path, "w") as f:
                            f.write(beautified_content)
                            print(f"\nDone!!! Open {file_path} in your favorite editor")

                    # Option for search sensitive info
                    # Search sensitive IPs in the file
                    print(f"\n{current_time} {CYAN}[CHK] Searching possible internal IPs in the file\n {RESET}")
                    ip_pattern = re.compile(r"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b")
                    with open(file_path, "r", encoding="utf-8") as f:
                        content = f.read()
                        matches = re.findall(ip_pattern, content)
                        if matches:
                            print(f"{matches}")

                    # Search sensitive emails in the file
                    print(f"\n{current_time} {CYAN}[CHK] Searching possible emails in the file\n {RESET}")
                    email_pattern = re.compile(r'[\w\.-]+@[\w\.-]+')
                    emails = set()
                    with open(file_path, "r", encoding="utf-8") as f:
                        content = f.read()
                        matches = re.findall(email_pattern, content)
                        if matches:
                            for match in matches:
                                emails.add(match)
                                print(f"[INFO] Emails found:", emails)

                    # Search possible encryption functions
                    print(f"\n{current_time} {CYAN}[CHK] Searching possible encryption functions in the file\n {RESET}")
                    encryption_func_pattern = re.compile(
                        r"CryptoJS\.enc|CryptoJS\.AES\.encrypt|CryptoJS\.AES\.decrypt|AES\.encrypt|AES\.decrypt|EncryptionHelper\.")
                    with open(file_path, "r", encoding="utf-8") as f:
                        content = f.readlines()
                        for line_num, line in enumerate(content):
                            matches = re.findall(encryption_func_pattern, line)
                            if matches:
                                print(
                                    f"{MAGENTA}[INFO] Encryption function found in line {line_num + 1}: {RESET}")
                                print(line.strip())

                    # Search sensitive private keys
                    print(f"\n{current_time} {CYAN}[CHK] Searching Private Keys in the file\n {RESET}")
                    private_key_pattern = re.compile(
                        r"(-----BEGIN ((EC|PGP|DSA|RSA|OPENSSH) )?PRIVATE KEY( BLOCK)?-----)", re.DOTALL)
                    with open(file_path, "r", encoding="utf-8") as f:
                        content = f.read()
                        matches = re.findall(private_key_pattern, content)
                        if matches:
                            print(f"{MAGENTA}[INFO] Private key found in {file_path} {RESET}")
                            for match in matches:
                                print(f"\t{match}")

                    # Search interesting words
                    print(f"\n{current_time} {CYAN}[CHK] Searching possible interesting words in the file\n {RESET}")
                    words_pattern = re.compile(r"\b(accessToken|oauth_token|TokenSecret|PaymentMethod)\b")
                    words = set()
                    with open(file_path, "r", encoding="utf-8") as f:
                        content = f.read()
                        matches = re.findall(words_pattern, content)
                        for word in matches:
                            if word not in words:
                                words.add(word)
                                print(word)

                    # Search high confidential secrets
                    print(f"\n{current_time} {CYAN}[CHK] Searching high confidential secrets {RESET}")
                    with open(os.path.abspath(
                            os.path.join(os.path.dirname(__file__), "db", "high-confidence.yml"))) as f:
                        secrets_patterns = yaml.safe_load(f)

                    with open(file_path, 'r') as f:
                        content = f.read()

                    for pattern in secrets_patterns['patterns']:
                        name = pattern['pattern']['name']
                        regex = pattern['pattern']['regex']
                        secrets_matches = re.findall(regex, content)
                        if secrets_matches:
                            print(f"{MAGENTA}\n[INFO] " + name + " identify " + file_path + f":{RESET}" + str(
                                secrets_matches))

                    # Search sensitive urls in the file
                    print(f"\n{current_time} {CYAN}[CHK] Searching possible sensitive URLs in js files\n {RESET}")
                    url_pattern = re.compile(r"(?:https?://|www\.)\S+?\.\S+?[';\" ,]")
                    omit_pattern = re.compile(
                        r"(.*github.*)|(.*facebook.*)|(.*mozilla.*)|(.*w3.*)|(.*webkit.*)|(.*csswg.*)|(.*reactnavigation.*)|(.*dottoro.*)|(.*momentjs.*)|(.*fxtf.*)|(.*fb.*)|(.*reactjs.*)")
                    with open(file_path, "r") as f:
                        content = f.read()
                        url_matches = re.findall(url_pattern, content)
                        for url in url_matches:
                            if not re.search(omit_pattern, url):
                                print(url)

                    # Search sensitive urls in the file
                    print(f"\n{current_time} {CYAN}[CHK] Searching possible endpoints in js files\n {RESET}")
                    endpoint_pattern = re.compile(
                        r"(?:\"|\u0027)(((?:[a-zA-Z]{1,10}://|//)[^\"\u0027/]{1,}\\.[a-zA-Z]{2,}[^\"\u0027]{0,})|((?:/|\.\./|\./)[^\"\u0027><,;| *()&$%#=\\\[\]]{1,})|([a-zA-Z0-9_\-/]{1,}/[a-zA-Z0-9_\-/]{1,}\.(?:[a-zA-Z]{1,4}|action)(?:[\\?|/][^\"|^\u0027]{0,}|))|([a-zA-Z0-9_\-]{1,}\.(?:php|asp|aspx|jsp|json|action|html|js|txt|xml)(?:\?[^\"|^\u0027]{0,}|)))(?:\"|\u0027)")
                    endpoint = set()
                    exported = False
                    with open(file_path, "r") as f:
                        content = f.read()
                        matches = re.findall(endpoint_pattern, content)
                        if matches:
                            found = True
                            endpoint = set(match[0] for match in matches if not match[0].startswith("./"))
                            with open("endpoints.txt", "a") as f:
                                for end in endpoint:
                                    f.write(end + "\n")
                                if found:
                                    print(f"{MAGENTA}\t[INFO] Endpoints found in the file: {file_path} {RESET}")
                                else:
                                    print(f"{WHITE}\t[INFO] No endpoints found in the file  {RESET}")
                        print(f"{GREEN}\t[INFO] Endpoints exported to endpoints.txt  {RESET}")