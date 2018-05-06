import cx_Freeze
import sys
import matplotlib
import os

base = None

if sys.platform == 'win32':
	base = "win32GUI"

os.environ['TCL_LIBRARY'] = r'C:\Python36\tcl\tcl8.6'
os.environ['TK_LIBRARY'] = r'C:\Python36\tcl\tk8.6'

executables = [cx_Freeze.Executable("Transportstyrelsen_dashboard.py", base=base, icon=r'pictures\ts_logo_cut.ico')]

cx_Freeze.setup(name = "Transportstyrelsen statistics", options = {"build_exe": {"packages":["tkinter","matplotlib","Webbrowser","requests", "idna","pandas","numpy"],"excludes": ["scipy", "zmq", "sqlite3","tqdm","sklearn"], "include_files":["tcl86t.dll", "tk86t.dll",r"pictures\ts_logo_cut.ico", r"pictures\connected.png",
r"pictures\disconnected.png",r"pictures\TS.png"]}},
version = "1.0",
description = "Transportstyrelsen statistics application",
executables = executables
)

''' Excludes:
scipy
sklearn
sqlite3
zmq

,"tqdm","sklearn","notebook","IPython","test","tornado"
'''