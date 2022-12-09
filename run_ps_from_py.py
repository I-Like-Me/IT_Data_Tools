import subprocess
import sys

process = subprocess.Popen(["powershell.exe", "C:\\Users\\cass.golkin\\Documents\\Python\\Learn_API\\Active_directory.ps1"], stdout=sys.stdout)

process.communicate()