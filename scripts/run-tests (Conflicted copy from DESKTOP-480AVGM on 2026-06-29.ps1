# Run all validation tests (lesson and report)
Write-Host "=== context2html: Running all validation tests ===" -ForegroundColor Cyan
Write-Host ""

$pass = 0
$fail = 0

# --- Unit tests ---
Write-Host "--- Unit test: validate-lesson.py ---" -ForegroundColor Yellow
$unitOut = & python scripts/test_validate.py 2>&1
$unitLines = $unitOut -join "`n"
Write-Host $unitLines
if ($LASTEXITCODE -eq 0) {
    $pass++
} else {
    $fail++
}

Write-Host "--- Unit test: validate-report.py ---" -ForegroundColor Yellow
$rptUnitOut = & python scripts/test_validate-report.py 2>&1
$rptUnitLines = $rptUnitOut -join "`n"
Write-Host $rptUnitLines
if ($LASTEXITCODE -eq 0) {
    $pass++
} else {
    $fail++
}

# --- report-starter.html ---
Write-Host "--- Validate: report-starter.html ---" -ForegroundColor Yellow
$tplOut = & python scripts/validate-report.py templates/report-starter.html 2>&1
$tplLines = $tplOut -join "`n"
Write-Host $tplLines
if ($LASTEXITCODE -eq 0) {
    $pass++
} else {
    $fail++
}

# --- Demo report ---
Write-Host "--- Validate: 0001-demo-report.html ---" -ForegroundColor Yellow
$demoOut = & python scripts/validate-report.py examples/0001-demo-report.html 2>&1
$demoLines = $demoOut -join "`n"
Write-Host $demoLines
if ($LASTEXITCODE -eq 0) {
    $pass++
} else {
    $fail++
}

# --- lesson-starter.html (via lesson validator, from teach_more_pic) ---
$lsnPath = "templates/lesson-starter.html"
if (Test-Path $lsnPath) {
    Write-Host "--- Validate: lesson-starter.html ---" -ForegroundColor Yellow
    $lsnOut = & python scripts/validate-lesson.py $lsnPath 2>&1
    $lsnLines = $lsnOut -join "`n"
    Write-Host $lsnLines
    if ($LASTEXITCODE -eq 0) { $pass++ } else { $fail++ }
} else {
    Write-Host "--- Skip: lesson-starter.html not present ---" -ForegroundColor DarkYellow
    $pass++
}

Write-Host ""
Write-Host "=== Results: $pass passed, $fail failed ===" -ForegroundColor Cyan
if ($fail -gt 0) { exit 1 }
