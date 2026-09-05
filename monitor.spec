# Build do executável. Gerar com:
#
#     uv run pyinstaller monitor.spec --noconfirm
#
# O resultado sai em `dist/MonitorDeHardware.exe`, arquivo único.
#
# Três coisas aqui não são preferência, são obrigatórias:
#
# 1. `upx=False` — executável comprimido com UPX é um dos padrões mais marcados por
#    antivírus, porque é o que malware usa para se esconder. O PyInstaller liga o UPX
#    sozinho quando encontra o programa instalado, então desligar precisa ser explícito.
# 2. `version="versao.txt"` — executável sem identificação é tratado como suspeito por
#    heurística.
# 3. Os arquivos de tema do CustomTkinter no `datas` — eles são JSON e PNG carregados em
#    tempo de execução, e o PyInstaller não os encontra sozinho. Sem isso o `.exe` compila
#    e quebra ao abrir a janela, que é o modo mais chato de descobrir o problema.

from pathlib import Path

import customtkinter

_CUSTOMTKINTER = Path(customtkinter.__file__).parent

a = Analysis(
    ["main.py"],
    pathex=[],
    binaries=[],
    datas=[
        (str(_CUSTOMTKINTER), "customtkinter"),
        # O `icon=` lá embaixo é o ícone do arquivo no Explorer. Este aqui é o da
        # janela aberta: são coisas diferentes, e a janela lê o arquivo em execução.
        ("assets/icone.ico", "assets"),
    ],
    hiddenimports=[
        # O plyer escolhe a implementação em tempo de execução, por nome — o PyInstaller
        # não enxerga essa importação analisando o código.
        "plyer.platforms.win.notification",
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=["pytest", "ruff"],
    noarchive=False,
    optimize=0,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name="MonitorDeHardware",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    upx_exclude=[],
    runtime_tmpdir=None,
    # Sem janela preta de terminal atrás da interface.
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon="assets/icone.ico",
    version="versao.txt",
)
