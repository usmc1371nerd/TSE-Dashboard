[Setup]
AppName=TSE Dashboard
AppVersion=1.0
DefaultDirName={autopf}\TSE Dashboard
DefaultGroupName=TSE Dashboard
OutputBaseFilename=TSE-Dashboard-Installer
Compression=lzma
SolidCompression=yes

[Files]
Source: "dist\TSE-Dashboard.exe"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\TSE Dashboard"; Filename: "{app}\TSE-Dashboard.exe"
Name: "{commondesktop}\TSE Dashboard"; Filename: "{app}\TSE-Dashboard.exe"

[UninstallDelete]
Type: filesandordirs; Name: "{app}"
