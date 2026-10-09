import os
import shutil
import subprocess
import sys

# 1. Konfigurimi i rrugëve (Paths)
TARGET_CNC_PC_PATH = (
    r"\\ACERAIO\CNC_App"  # Vendosni IP-në e saktë ose emrin e PC të CNC
)
EXE_NAME = "KinetixCNC.exe"

# 2. Komanda për paketim me PySide6 / PyInstaller
# --noconsole heq dritaren e zezë të cmd, --onefile e bën 1 skedar të vetëm
build_command = [
    "pyinstaller",
    "--noconsole",
    "--onefile",
    "--name=KinetixCNC",
    "main.py",
]


def build_and_deploy():
  print("1. Po fillon paketimi i skedarit .exe...")
  result = subprocess.run(build_command)

  if result.returncode != 0:
    print("X Gabim gjatë krijimit të .exe!")
    return

  local_exe = os.path.join("dist", EXE_NAME)

  if not os.path.exists(local_exe):
    print("X Skedari .exe nuk u gjet te dosja 'dist'!")
    return

  print(f"2. Po kopjohet në PC-në e CNC-së: {TARGET_CNC_PC_PATH}...")
  try:
    # Sigurohemi që dosja e destinacionit ekziston
    if not os.path.exists(TARGET_CNC_PC_PATH):
      print(
          f"X Nuk mund të qaseshet rruga e rrjetit: {TARGET_CNC_PC_PATH}. Kontrolloni"
          " lidhjen e rrjetit!"
      )
      return

    destination = os.path.join(TARGET_CNC_PC_PATH, EXE_NAME)
    shutil.copy2(local_exe, destination)
    print("✓ Skedari .exe u dërgua me sukses në PC e CNC!")

  except PermissionError:
    print(
        "X Gabim Aksesi! Sigurohuni që programi nuk është i hapur në PC e"
        " CNC-së gjatë ndërrimit."
    )
  except Exception as e:
    print(f"X Gabim gjatë kopjimit: {e}")


if __name__ == "__main__":
  build_and_deploy()