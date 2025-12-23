import os
import subprocess
import zipfile
from struct import unpack
from statistics import mean
from packaging.version import Version

from lib.Args import ArgsParse
from lib.Colors import RED, RESET

from elftools.elf.elffile import ELFFile
from elftools.elf.enums import ENUM_E_MACHINE
from elftools.elf.sections import SymbolTableSection

signer_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "tools", "uber-apk-signer-1.2.1.jar"))

# =========================================================
# ZIP / ELF helpers
# =========================================================

def open_elf_from_apk(apk_path, so_path):
    z = zipfile.ZipFile(apk_path, 'r')
    f = z.open(so_path)
    return z, f, ELFFile(f)


def find_lib(app, name):
    with zipfile.ZipFile(app) as z:
        for f in z.namelist():
            if f.endswith(name):
                return f
    raise Exception(f"{name} not found in APK")


# =========================================================
# libapp.so – snapshot
# =========================================================

def extract_snapshot_info(app, libapp_path):
    z, f, elf = open_elf_from_apk(app, libapp_path)

    dynsym = elf.get_section_by_name('.dynsym')
    sym = dynsym.get_symbol_by_name('_kDartVmSnapshotData')[0]

    f.seek(sym['st_value'] + 20)
    snapshot_hash = f.read(32).decode(errors="ignore")

    data = f.read(256)
    flags = data[:data.index(b'\0')].decode(errors="ignore").strip().split(' ')

    f.close()
    z.close()
    return snapshot_hash, flags


# =========================================================
# libflutter.so – Dart version
# =========================================================

def extract_flutter_info(app, libflutter_path):
    z, f, elf = open_elf_from_apk(app, libflutter_path)

    section = elf.get_section_by_name('.rodata')
    data = section.data()

    dart_version = None
    epos = data.find(b' (stable) (')
    if epos != -1:
        pos = data.rfind(b'\x00', 0, epos) + 1
        dart_version = data[pos:epos].decode(errors="ignore")

    f.close()
    z.close()
    return dart_version, 'android'


# =========================================================
# AOT / JIT detection
# =========================================================

def detect_aot_jit(app, libapp_path, flags):
    z, f, elf = open_elf_from_apk(app, libapp_path)

    reasons = []
    dynsym = elf.get_section_by_name('.dynsym')

    if dynsym and dynsym.get_symbol_by_name('_kDartVmSnapshotInstructions'):
        reasons.append("SnapshotInstructions symbol present")

    if '--precompiled' in flags:
        reasons.append("Snapshot flag --precompiled")

    f.close()
    z.close()

    if reasons:
        return "AOT", ", ".join(reasons)

    return "JIT", "No AOT indicators found"


# =========================================================
# Obfuscation detection
# =========================================================

def detect_obfuscation(app, libapp_path, flags):
    z, f, elf = open_elf_from_apk(app, libapp_path)
    reasons = []

    if '--obfuscate' in flags:
        reasons.append("Snapshot flag --obfuscate")

    sym_lens = []
    dart_syms = 0

    for sec in elf.iter_sections():
        if isinstance(sec, SymbolTableSection):
            for sym in sec.iter_symbols():
                if not sym.name:
                    continue
                sym_lens.append(len(sym.name))
                if sym.name.startswith('Dart_'):
                    dart_syms += 1

    if sym_lens and mean(sym_lens) < 8:
        reasons.append("Short symbol names (avg < 8 chars)")

    if dart_syms < 5:
        reasons.append("Very few Dart symbols exposed")

    f.close()
    z.close()

    if reasons:
        return "Yes", "; ".join(reasons)

    return "No", "Readable symbols present"


# =========================================================
# Dart session_verify_cert_chain offset
# =========================================================

OFFSET_RANGES = [
    ("2.10.6", "2.17.6", "0x006E8578"),
    ("3.9.0",  "3.10.2", "0x0071ABFC"),
]


def get_session_verify_cert_chain_offset(dart_version):
    if not dart_version:
        return "Unknown"

    v = Version(dart_version)

    for start, end, offset in OFFSET_RANGES:
        if Version(start) <= v < Version(end):
            return offset

    return "Unknown"


# =========================================================
# UI helpers
# =========================================================

def card(title, body):
    print(f"\n╔═ {title}")
    for k, v in body.items():
        print(f"║ {k:<30}: {v}")
    print("╚" + "═" * 60)


# =========================================================
# Flutter app handler (called externally)
# =========================================================

def patch_apk():
    global args
    parse = ArgsParse()
    args = parse.getArgs()
    app = args.app_name

    if not app.endswith(".apk"):
        print(f"{RED}\nPatch not supported for iOS on Windows/Linux{RESET}")
        return

    libapp = find_lib(app, "libapp.so")
    libflutter = find_lib(app, "libflutter.so")

    snapshot_hash, flags = extract_snapshot_info(app, libapp)
    dart_version, os_name = extract_flutter_info(app, libflutter)

    mode, mode_reason = detect_aot_jit(app, libapp, flags)
    obf, obf_reason = detect_obfuscation(app, libapp, flags)
    offset = get_session_verify_cert_chain_offset(dart_version)

    # ---------------- OUTPUT ----------------

    card("Framework Detection", {
        "OS": os_name
    })

    card("Dart Snapshot", {
        "Snapshot Hash": snapshot_hash,
        "Snapshot Flags": ", ".join(flags)
    })

    card("Compilation Mode", {
        "Mode": mode,
        "Evidence": mode_reason
    })

    card("Obfuscation", {
        "Enabled": obf,
        "Evidence": obf_reason
    })

    card("Dart SDK", {
        "Dart Version": dart_version or "Unknown"
    })

    card("Dart session_verify_cert_chain offset", {
        "Offset": offset
    })

    # ---------------- PATCHING ----------------

    search = input("\nDo you want patch apk file with reflutter? (Y/n): ")
    if search.lower() == "n":
        return

    subprocess.run(["reflutter", app], shell=False)

    search = input("\nDo you want patch signing apk file? (y/n): ")
    if search.lower() != "n":
        subprocess.run(
            ["java", "-jar", signer_path, "--apk", "./release.RE.apk"],
            shell=False
        )
