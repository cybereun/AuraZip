import os
import sys
import subprocess
import shutil

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def find_iscc():
    candidates = [
        os.path.expandvars(r"%LOCALAPPDATA%\Programs\Inno Setup 6\ISCC.exe"),
        r"C:\Program Files (x86)\Inno Setup 6\ISCC.exe",
        r"C:\Program Files\Inno Setup 6\ISCC.exe",
        shutil.which("ISCC.exe")
    ]
    for c in candidates:
        if c and os.path.exists(c):
            return c
    return None

def main():
    print("=== [1/2] Building AuraZip with PyInstaller ===")
    spec_file = os.path.join(BASE_DIR, "AuraZip.spec")
    cmd_pyinstaller = [sys.executable, "-m", "PyInstaller", spec_file, "--noconfirm", "--clean"]
    
    ret = subprocess.run(cmd_pyinstaller, cwd=BASE_DIR)
    if ret.returncode != 0:
        print("[ERROR] PyInstaller build failed!")
        sys.exit(ret.returncode)

    print("\n=== [2/2] Compiling Installer with Inno Setup ===")
    iscc_path = find_iscc()
    if not iscc_path:
        print("[ERROR] Inno Setup (ISCC.exe) not found! Please ensure Inno Setup 6 is installed.")
        sys.exit(1)

    iss_file = os.path.join(BASE_DIR, "installer", "aurazip_installer.iss")
    from version import APP_VERSION
    clean_v = APP_VERSION.lstrip('vV')
    cmd_iscc = [iscc_path, f"/DMyAppVersion={clean_v}", iss_file]
    
    ret = subprocess.run(cmd_iscc, cwd=os.path.join(BASE_DIR, "installer"))
    if ret.returncode != 0:
        print("[ERROR] Inno Setup compilation failed!")
        sys.exit(ret.returncode)

    out_dir = os.path.join(BASE_DIR, "dist_installer")
    os.makedirs(out_dir, exist_ok=True)

    print("\n=== [3/3] Packaging Portable ZIP Archive ===")
    import zipfile
    from version import APP_VERSION
    portable_zip = os.path.join(out_dir, f"AuraZip_Portable_{APP_VERSION}.zip")
    src_dir = os.path.join(BASE_DIR, "dist", "AuraZip")
    if os.path.exists(src_dir):
        with zipfile.ZipFile(portable_zip, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
            for root, dirs, files in os.walk(src_dir):
                for file in files:
                    full_p = os.path.join(root, file)
                    rel_p = os.path.relpath(full_p, src_dir)
                    zf.write(full_p, os.path.join("AuraZip", rel_p))
        print(f" -> Created Portable ZIP: {portable_zip} ({os.path.getsize(portable_zip)/(1024*1024):.2f} MB)")

    print(f"\n[SUCCESS] All outputs generated successfully in: {out_dir}")
    if os.path.exists(out_dir):
        for f in os.listdir(out_dir):
            if f.endswith(".exe") or f.endswith(".zip"):
                size_mb = os.path.getsize(os.path.join(out_dir, f)) / (1024 * 1024)
                print(f" -> {f} ({size_mb:.2f} MB)")

if __name__ == "__main__":
    main()
