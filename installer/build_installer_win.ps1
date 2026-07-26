$ErrorActionPreference = "Stop"

$projectRoot = Split-Path -Parent $PSScriptRoot
Push-Location $projectRoot
try {
    $version = & uv run python -c "import sys; sys.path.insert(0, 'src'); from oledhero.version import __version__; print(__version__)"
    if ($LASTEXITCODE -ne 0) {
        throw "Could not read the OLEDHero version."
    }
} finally {
    Pop-Location
}

$compiler = Get-Command "ISCC.exe" -ErrorAction SilentlyContinue
if ($null -eq $compiler) {
    $fallback = Join-Path ${env:ProgramFiles(x86)} "Inno Setup 6\ISCC.exe"
    if (-not (Test-Path -LiteralPath $fallback)) {
        throw "Inno Setup 6 was not found. Install it or add ISCC.exe to PATH."
    }
    $compilerPath = $fallback
} else {
    $compilerPath = $compiler.Source
}

& $compilerPath "/DMyAppVersion=$version" "$PSScriptRoot\OledHero.iss"
if ($LASTEXITCODE -ne 0) {
    throw "The installer build failed."
}

Write-Host "Created dist\OledHero-$version-Setup-x64.exe"
