@echo off
chcp 65001 >nul
set PYTHONIOENCODING=utf-8
cd /d "%~dp0"

rem 把這個 .bat 跟 patch_shadow_desk.py 一起放到有「報表.html / 看報表.bat」的資料夾，
rem 然後雙擊它。也可以把資料夾拖到這個 .bat 上面，改那個資料夾。

where python >nul 2>nul
if %errorlevel%==0 (set PY=python) else (set PY=py)

%PY% "%~dp0patch_shadow_desk.py" %*

echo.
echo 完成。按任意鍵關閉。
pause >nul
