@echo off
setlocal enabledelayedexpansion

REM カレントディレクトリをスクリプトの場所に設定
cd /d %~dp0

REM PYTHONPATHの設定
set PYTHONPATH=%CD%;%PYTHONPATH%

REM Pythonスクリプトのパス
set SCRIPT_PATH=src\main.py

REM コマンドライン引数の取得
set COMMAND=%1
set ARG1=%2
set ARG2=%3

REM 引数チェック
if "%COMMAND%"=="" (
    echo 使用方法:
    echo   search_news.bat search "検索キーワード" [--start-date YYYY-MM-DD] [--end-date YYYY-MM-DD]
    echo   search_news.bat add "サイト名" "URL"
    echo   search_news.bat del "サイト名" "URL"
    exit /b 1
)

REM コマンドに応じた処理
if "%COMMAND%"=="search" (
    if "%ARG1%"=="" (
        echo 検索キーワードを指定してください。
        exit /b 1
    )
    python %SCRIPT_PATH% search %*
) else if "%COMMAND%"=="add" (
    if "%ARG1%"=="" (
        echo サイト名を指定してください。
        exit /b 1
    )
    if "%ARG2%"=="" (
        echo URLを指定してください。
        exit /b 1
    )
    python %SCRIPT_PATH% add %ARG1% %ARG2%
) else if "%COMMAND%"=="del" (
    if "%ARG1%"=="" (
        echo サイト名を指定してください。
        exit /b 1
    )
    if "%ARG2%"=="" (
        echo URLを指定してください。
        exit /b 1
    )
    python %SCRIPT_PATH% del %ARG1% %ARG2%
) else (
    echo 無効なコマンドです: %COMMAND%
    echo 使用可能なコマンド: search, add, del
    exit /b 1
)

endlocal