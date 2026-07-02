@echo off
chcp 65001 >nul

echo ====================================
echo   Obsidian 笔记一键同步脚本
echo ====================================
echo.

set VAULT_PATH=C:\Users\EDY\Documents\Obsidian Vault

if not exist "%VAULT_PATH%" (
    echo [错误] Obsidian Vault 路径不存在: %VAULT_PATH%
    pause
    exit /b 1
)

cd /d "%VAULT_PATH%"

echo [1/4] 检查更新...
git pull --rebase >nul 2>&1
if %errorlevel% neq 0 (
    echo [提示] 远程拉取失败，继续推送...
)

echo [2/4] 添加文件...
git add .

echo [3/4] 提交更新...
git commit -m "更新笔记 %date% %time%"

echo [4/4] 推送到 GitHub...
git push

echo.
if %errorlevel% equ 0 (
    echo [完成] 笔记已成功同步到 GitHub！
) else (
    echo [警告] 推送失败，请检查网络连接
)

echo.
pause
