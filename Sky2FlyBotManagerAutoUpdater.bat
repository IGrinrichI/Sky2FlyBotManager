@echo off
chcp 65001

if exist "%1" (
    :retry_1
    :: Пытаемся переименовать файл сам в себя.
    :: Если он занят другим процессом, команда выдаст ошибку.
    ren "%1" "%1" 2>nul
    if errorlevel 1 (
        timeout /t 1 /nobreak >nul
        goto retry_1
    )
    timeout /t 1 /nobreak >nul
    del /f /q "%1"
)

curl -k -L -o "%1" %2

@REM if exist "%1" (
@REM     :retry_2
@REM     :: Пытаемся переименовать файл сам в себя.
@REM     :: Если он занят другим процессом, команда выдаст ошибку.
@REM     ren "%1" "%1" 2>nul
@REM     if errorlevel 1 (
@REM         timeout /t 1 /nobreak >nul
@REM         goto retry_2
@REM     )
@REM     timeout /t 1 /nobreak >nul
@REM     set "PATH=%~dp0;%PATH%"
@REM     cd /d "%~dp0"
@REM     start "" %1
@REM @REM     start "" cmd.exe /c start "" %1
@REM )

del /f /q "%~f0" & exit