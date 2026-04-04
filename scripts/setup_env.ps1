param(
    [string]$venvDir = '.venv'
)

Write-Host "Creating virtual environment in $venvDir"
python -V > $null 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Error "Python not found on PATH. Install Python 3.10+ and retry."
    exit 1
}

python -m venv $venvDir
Write-Host "Installing requirements..."
Start-Process -FilePath "$venvDir\Scripts\python.exe" -ArgumentList '-m','pip','install','--upgrade','pip' -NoNewWindow -Wait
Start-Process -FilePath "$venvDir\Scripts\python.exe" -ArgumentList '-m','pip','install','-r','requirements.txt' -NoNewWindow -Wait

Write-Host "Setup complete. Activate with:`n  .\$venvDir\Scripts\Activate.ps1"
