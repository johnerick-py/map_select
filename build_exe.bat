@echo off
echo ====================================
echo  GERANDO EXECUTAVEL - Mapa Municipios Goias
echo ====================================
echo.

REM Verifica se PyInstaller está instalado
pip show pyinstaller >nul 2>&1
if errorlevel 1 (
    echo PyInstaller nao encontrado. Instalando...
    pip install pyinstaller
)

echo.
echo Limpando builds anteriores...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist

echo.
echo Gerando executavel...
pyinstaller --clean app.spec

if exist "dist\MapaMunicipiosGoias\MapaMunicipiosGoias.exe" (
    echo.
    echo ====================================
    echo  SUCESSO!
    echo ====================================
    echo.
    echo Executavel criado em: dist\MapaMunicipiosGoias\
    echo.
    echo Para executar: 
    echo   dist\MapaMunicipiosGoias\MapaMunicipiosGoias.exe
    echo.
    echo Para distribuir, copie toda a pasta:
    echo   dist\MapaMunicipiosGoias\
    echo.
) else (
    echo.
    echo ERRO: Falha ao gerar o executavel.
    echo Verifique as mensagens de erro acima.
)

echo.
pause
