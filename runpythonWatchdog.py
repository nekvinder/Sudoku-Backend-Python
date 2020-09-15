from watchgod import run_process
import os

def foobar(a, b, c):
   os.system("python3 app_with_python_only.py")
   # print(a,b,c)

run_process('.', foobar, args=(1, 2, 3))