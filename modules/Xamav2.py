from lib.Colors import RED, YELLOW, RESET

def xama_blob():
    print(f"{RED}\n\t[!] APK compiled in mode Unbundled Build")
    print(f"\tThe new xamarim compression has been detected, the dll files embebed in the assemblies.blob {RESET}")
    print(f"{YELLOW}\n\t[!] To unpack and repackaging assemblies.blob and assemblies.manifest, use: {RESET}")
    print("\tPyxamstore -> https://github.com/jakev/pyxamstore/")