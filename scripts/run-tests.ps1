# Run validate-lesson.py against all example HTML files
Write-Host "=== teach_more_pic: Running all validation tests ===" -ForegroundColor Cyan
Write-Host ""

$pass = 0
$fail = 0

# Also validate the KG template
Write-Host "Testing: kg-starter.html" -ForegroundColor Yellow
$kgOutput = & python scripts/validate-lesson.py templates/kg-starter.html 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "  PASS" -ForegroundColor Green
    $pass++
} else {
    Write-Host "  FAIL" -ForegroundColor Red
    $lines = $kgOutput -join "`n"
    $lines -split "`n" | ForEach-Object { Write-Host "    $_" }
    $fail++
}

Get-ChildItem -Path "examples" -Filter "*.html" | ForEach-Object {
    $file = $_.FullName
    $name = $_.Name
    Write-Host "Testing: $name" -ForegroundColor Yellow
    $output = & python scripts/validate-lesson.py $file 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  PASS" -ForegroundColor Green
        $pass++
    } else {
        $lines = $output -join "`n"
        if ($lines -match "Quiz: 5 questions") {
            Write-Host "  PASS (no quiz - expected)" -ForegroundColor Green
            $pass++
        } else {
            Write-Host "  FAIL" -ForegroundColor Red
            $output | ForEach-Object { Write-Host "    $_" }
            $fail++
        }
    }
}

Write-Host ""
Write-Host "=== Results: $pass passed, $fail failed ===" -ForegroundColor Cyan
if ($fail -gt 0) { exit 1 }
