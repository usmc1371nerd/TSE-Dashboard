# How to Build and Run TSE Dashboard

## 1. Clone the repository
```sh
git clone https://github.com/usmc1371nerd/TSE-Dashboard.git
cd TSE-Dashboard
```

## 2. Install dependencies
- Python 3.8+ required
- Tkinter is included with standard Python

## 3. Run the app
```sh
python app.py
```

## 4. Build an executable (optional)
Install PyInstaller:
```sh
pip install pyinstaller
```
Build the exe:
```sh
pyinstaller --onefile --windowed app.py
```
Find your `.exe` in the `dist` folder.

## 5. Notes
- Scripts and CMDs are stored in `scripts_folder` and `cmds_folder`.
- You can add, edit, and delete scripts and CMDs from the UI.