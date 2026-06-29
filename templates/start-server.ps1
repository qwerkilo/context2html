# start-server.ps1 — 报告 HTTP 服务器一键启动
# 用法: powershell -ExecutionPolicy Bypass -File start-server.ps1
# 使用 Python 内置 HTTP 服务器，自动打开浏览器到当前目录下的报告

param(
  [int]$Port = 8000,
  [string]$DefaultReport = ""
)

if (-not $DefaultReport) {
  if (Test-Path "index.html") {
    $DefaultReport = "http://localhost:$Port/index.html"
  } else {
    # 找当前目录第一个 *.html 报告文件
    $first = Get-ChildItem -Path "." -Filter "*.html" | Sort-Object Name | Select-Object -First 1
    if ($first) {
      $DefaultReport = "http://localhost:$Port/$($first.Name)"
    } else {
      $DefaultReport = "http://localhost:$Port/"
    }
  }
}

Write-Host "=== context2html 报告服务器 ===" -ForegroundColor Cyan
Write-Host "端口: $Port" -ForegroundColor Green
Write-Host "打开: $DefaultReport" -ForegroundColor Green
Write-Host "按 Q 键停止服务器" -ForegroundColor Yellow
Write-Host ""

Start-Process $DefaultReport

$job = Start-Job -ScriptBlock {
  param($p)
  Set-Location $using:PWD
  python -m http.server $p --bind 127.0.0.1
} -ArgumentList $Port

while ($true) {
  if ([Console]::KeyAvailable) {
    $key = [Console]::ReadKey($true)
    if ($key.Key -eq 'Q') {
      Write-Host "`n正在停止服务器..." -ForegroundColor Yellow
      Stop-Job $job
      Remove-Job $job
      Write-Host "服务器已停止" -ForegroundColor Green
      break
    }
  }
  Start-Sleep -Milliseconds 200
  if ($job.State -eq 'Failed') {
    $msg = Receive-Job $job
    Write-Host "服务器启动失败: $msg" -ForegroundColor Red
    Write-Host "请确保 Python 已安装 (python --version)" -ForegroundColor Yellow
    Remove-Job $job
    break
  }
}
