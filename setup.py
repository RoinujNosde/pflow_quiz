import sys
from cx_Freeze import setup, Executable


# GUI applications require a different base on Windows (the default is for a
# console application).
base = None
if sys.platform == "win32":
    base = "Win32GUI"

build_exe_options = {'include_files':[("icon.ico", "icon.ico"),]}

shortcut_table = [
    ("DesktopShortcut",          # Shortcut
     "DesktopFolder",            # Directory_
     "PflowQuiz",                # Name
     "TARGETDIR",                # Component_
     "[TARGETDIR]pflow_quiz.exe",# Target
     None,                       # Arguments
     None,                       # Description
     None,                       # Hotkey
     None,                       # Icon
     0,                          # IconIndex
     None,                       # ShowCmd
     'TARGETDIR'                 # WkDir
     ),
    ("StartMenuShortcut",        # Shortcut
     "StartMenuFolder",          # Directory_
     "PflowQuiz",                # Name
     "TARGETDIR",                # Component_
     "[TARGETDIR]pflow_quiz.exe",# Target
     None,                       # Arguments
     None,                       # Description
     None,                       # Hotkey
     None,                       # Icon
     0,                          # IconIndex
     None,                       # ShowCmd
     'TARGETDIR'                 # WkDir
     )
    ]

# Now create the table dictionary
msi_data = {"Shortcut": shortcut_table}

# Change some default MSI options and specify the use of the above defined tables
bdist_msi_options = {'data': msi_data, 'install_icon': 'icon.ico'}

setup(  name = "PflowQuiz",
        version = "1.0",
        author = "Edson Passos",
        options = {
            "build_exe": {
                "include_files": ["icon.ico",]
                },
                "bdist_msi": bdist_msi_options,
            },
        executables = [
            Executable(
                "pflow_quiz.py",
                base=base,
                shortcutName="PflowQuiz",
                shortcutDir="DesktopFolder",
                icon="icon.ico",
                )
            ]
        )
