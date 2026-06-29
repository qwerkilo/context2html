# start-server.ps1 — 课程 HTTP 服务器一键启动
# 用法: powershell -ExecutionPolicy Bypass -File start-server.ps1
# 使用 Python 内置 HTTP 服务器，自动打开浏览器到第一课

param(
  [int]$Port = 8000,
  [string]$DefaultLesson = ""
)

# 检测默认课程（index.html 或第一课）
if (-not $DefaultLesson) {
  if (Test-Path "index.html") {
    $DefaultLesson = "http://localhost:$Port/index.html"
  } else {
    # 找 lessons/NNNN-slug.html 中的第一个
    $first = Get-ChildItem -Path "lessons" -Filter "*.html" | Sort-Object Name | Select-Object -First 1
    if ($first) {
      $DefaultLesson = "http://localhost:$Port/lessons/$($first.Name)"
    } else {
      $DefaultLesson = "http://localhost:$Port/"
    }
  }
}

Write-Host "=== teach_more_pic 课程服务器 ===" -ForegroundColor Cyan
Write-Host "端口: $Port" -ForegroundColor Green
Write-Host "打开: $DefaultLesson" -ForegroundColor Green
Write-Host "按 Q 键停止服务器" -ForegroundColor Yellow
Write-Host ""

# 打开浏览器
Start-Process $DefaultLesson

# 启动 Python HTTP 服务器（后台 job）
$job = Start-Job -ScriptBlock {
  param($p)
  Set-Location $using:PWD
  python -m http.server $p --bind 127.0.0.1
} -ArgumentList $Port

# 等待 Q 键
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
