$ErrorActionPreference = "Stop"

$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$pythonExe = Join-Path $repoRoot "runtime\python.exe"

if (-not (Test-Path $pythonExe)) {
    Write-Host ""
    Write-Host "The portable runtime is missing: $pythonExe"
    Write-Host "Rebuild the Windows portable package and try again."
    exit 1
}

Write-Host ""
Write-Host "Hospital Charge Capture Analytics"
Write-Host "Starting the portable demo runtime."
Write-Host "A browser tab will open automatically when the app is ready."
Write-Host ""

& $pythonExe -m ri_control_room --repo-root $repoRoot demo
$exitCode = if ($null -ne $LASTEXITCODE) { $LASTEXITCODE } else { 0 }

if ($exitCode -notin @(0, 130)) {
    Write-Host ""
    Write-Host "The portable demo stopped with exit code $exitCode."
    Write-Host "Review the messages above and rebuild the package if the runtime is incomplete."
}

exit $exitCode
