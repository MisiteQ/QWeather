# ============================================================
# QWeather 构建脚本 (Windows / PowerShell)
# 用法: 右键"使用 PowerShell 运行"，或在该目录执行 .\build.ps1
# 前提: 已安装 Python 3
# ============================================================
$ErrorActionPreference = "Stop"
$root = $PSScriptRoot
Set-Location $root

Write-Host "[1/1] 打包 fpk ..." -ForegroundColor Cyan
python build_fp.py
if ($LASTEXITCODE -ne 0) {
    Write-Host "打包失败，请检查上方报错信息。" -ForegroundColor Red
    exit 1
}

Write-Host "" -ForegroundColor Cyan
Write-Host "打包完成！" -ForegroundColor Green
Write-Host "在飞牛 OS 应用中心 -> 左下角"手动安装" -> 选择生成的 .fpk 文件即可安装。" -ForegroundColor Green
