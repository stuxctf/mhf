from lib.Colors import RED, YELLOW, RESET

def xama_blob_so():
    print(f"{RED}\n\t[!] APK compiled in mode Unbundled Build")
    print(f"\tThe new xamarim compression in MAUI 9 has been detected, the dll files embebed in the libassemblies.ARCH.blob.so {RESET}")
    print(f"{YELLOW}\n\t[!] To unpack and repackaging libassemblies.ARCH.blob.so, use: {RESET}")
    print("\tpymauistore -> https://github.com/mwalkowski/pymauistore")