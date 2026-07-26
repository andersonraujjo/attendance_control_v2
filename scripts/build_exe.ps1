# Gera o executável Windows do Ponto Eletrônico v.2
$ErrorActionPreference = "Stop"
Set-Location (Split-Path -Parent $PSScriptRoot)

Write-Host ">> Instalando PyInstaller (se necessário)..."
.\.venv\Scripts\python -m pip install -q pyinstaller

Write-Host ">> Empacotando com flet pack..."
.\.venv\Scripts\flet.exe pack run.py `
  -n "PontoEletronicoV2" `
  -y `
  --product-name "Ponto Eletronico v.2" `
  --file-description "Ponto Eletronico v.2" `
  --product-version "2.0.0" `
  --file-version "2.0.0.0" `
  --hidden-import "pandas" `
  --hidden-import "openpyxl" `
  --hidden-import "app" `
  --hidden-import "app.main" `
  --hidden-import "app.ui.app" `
  --hidden-import "app.services.ponto_service" `
  --hidden-import "app.services.export_service" `
  --hidden-import "app.repository.registro_repo" `
  --hidden-import "app.db.database" `
  --hidden-import "app.models.registro" `
  --hidden-import "app.paths"

$exe = Join-Path (Get-Location) "dist\PontoEletronicoV2.exe"
if (Test-Path $exe) {
    Write-Host ""
    Write-Host "OK — executavel gerado em:"
    Write-Host $exe
    Write-Host ""
    Write-Host "Ao rodar o .exe, banco e exports ficam ao lado dele:"
    Write-Host "  dist\data\ponto_v2.db"
    Write-Host "  dist\exports\relatorio_ponto_*.csv"
} else {
    Write-Error "Falha: executavel nao encontrado em dist"
}
