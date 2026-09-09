# EEDLAVS

v3.0 Packaging Instructions

1. Open cmd and navigate to the project directory
2. Clean up old PyInstaller generated files only (if present)
if exist build rd /s /q build
if exist dist rd /s /q dist
if exist main.spec del /q main.spec
3. Create and activate a virtual environment, and install project dependencies
if not exist venv\Scripts\python.exe py -3 -m venv venv
call venv\Scripts\activate.bat
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

Do not execute pip freeze > requirements.txt as it will overwrite the original project dependency list.

4. Package
python -m PyInstaller --clean --noconfirm --onefile --windowed --name EEDLAVS --paths=. --add-data "TarGo_v1.3.html;." main.py
5. Finished. Executable generated: dist\EEDLAVS.exe


