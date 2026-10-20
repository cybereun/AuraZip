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
    cmd_iscc = [iscc_path, iss_file]
    
    ret = subprocess.run(cmd_iscc, cwd=os.path.join(BASE_DIR, "installer"))
    if ret.returncode != 0:
        print("[ERROR] Inno Setup compilation failed!")
        sys.exit(ret.returncode)

    out_dir = os.path.join(BASE_DIR, "dist_installer")
    print(f"\n[SUCCESS] Installer built successfully in: {out_dir}")
    if os.path.exists(out_dir):
        for f in os.listdir(out_dir):
            if f.endswith(".exe"):
                size_mb = os.path.getsize(os.path.join(out_dir, f)) / (1024 * 1024)
                print(f" -> {f} ({size_mb:.2f} MB)")

if __name__ == "__main__":
    main()
