$ErrorActionPreference = "Stop"

function Test-SupportedPython {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Executable,
        [string[]]$Arguments = @()
    )

    & $Executable @Arguments -c "import sys; raise SystemExit(0 if (3, 12) <= sys.version_info[:2] < (3, 14) else 1)" *> $null
    return $LASTEXITCODE -eq 0
}

function Get-DemoPython {
    param(
        [Parameter(Mandatory = $true)]
        [string]$RepoRoot
    )

    $localVenvPython = Join-Path $RepoRoot ".venv-demo\Scripts\python.exe"
    if ((Test-Path $localVenvPython) -and (Test-SupportedPython -Executable $localVenvPython)) {
        return [pscustomobject]@{
            Label = "local demo environment"
            Executable = $localVenvPython
            Arguments = @()
        }
    }

    $pyCommand = Get-Command py.exe -ErrorAction SilentlyContinue
    if ($null -eq $pyCommand) {
        $pyCommand = Get-Command py -ErrorAction SilentlyContinue
    }
    if ($null -ne $pyCommand) {
        foreach ($versionArg in @("-3.13", "-3.12")) {
            if (Test-SupportedPython -Executable $pyCommand.Source -Arguments @($versionArg)) {
                return [pscustomobject]@{
                    Label = "Python Launcher $versionArg"
                    Executable = $pyCommand.Source
                    Arguments = @($versionArg)
                }
            }
        }
    }

    foreach ($commandName in @("python.exe", "python")) {
        $pythonCommand = Get-Command $commandName -ErrorAction SilentlyContinue
        if ($null -eq $pythonCommand) {
            continue
        }
        if ($pythonCommand.Source -like "*\WindowsApps\python.exe") {
            continue
        }
        if (Test-SupportedPython -Executable $pythonCommand.Source) {
            return [pscustomobject]@{
                Label = $pythonCommand.Source
                Executable = $pythonCommand.Source
                Arguments = @()
            }
        }
    }

    return $null
}

$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
Set-Location $repoRoot

if (-not (Test-Path (Join-Path $repoRoot "scripts\run_demo.py"))) {
    Write-Host ""
    Write-Host "Could not find scripts\run_demo.py from $repoRoot."
    exit 1
}

$python = Get-DemoPython -RepoRoot $repoRoot
if ($null -eq $python) {
    Write-Host ""
    Write-Host "Python 3.12 or 3.13 was not found on this machine."
    Write-Host "Install Python from https://www.python.org/downloads/windows/ and then double-click this launcher again."
    exit 1
}

Write-Host ""
Write-Host "Hospital Charge Capture Analytics"
Write-Host "Using $($python.Label)"
Write-Host "Preparing the local demo environment. The first launch can take a minute."
Write-Host "A browser tab will open automatically when the app is ready."
Write-Host ""

& $python.Executable @($python.Arguments + @("scripts/run_demo.py"))
$exitCode = if ($null -ne $LASTEXITCODE) { $LASTEXITCODE } else { 0 }

if ($exitCode -notin @(0, 130)) {
    Write-Host ""
    Write-Host "The demo stopped with exit code $exitCode."
    Write-Host "Review the messages above and try again."
}

exit $exitCode
