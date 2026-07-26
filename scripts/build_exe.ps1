# Gera o executável Windows do Ponto Eletrônico v.2 na raiz do projeto
$ErrorActionPreference = "Stop"
Set-Location (Split-Path -Parent $PSScriptRoot)

Write-Host ">> Instalando PyInstaller (se necessario)..."
.\.venv\Scripts\python -m pip install -q pyinstaller

Write-Host ">> Empacotando com flet pack..."
.\.venv\Scripts\flet.exe pack run.py `
  -n "PontoEletronicoV2" `
  -y `
  --distpath "dist_build" `
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

$built = Join-Path (Get-Location) "dist_build\PontoEletronicoV2.exe"
$exe = Join-Path (Get-Location) "PontoEletronicoV2.exe"

if (-not (Test-Path $built)) {
    Write-Error "Falha: executavel nao encontrado em dist_build"
}

Copy-Item $built $exe -Force
Remove-Item -Recurse -Force dist_build -ErrorAction SilentlyContinue

Write-Host ""
Write-Host "OK — executavel na raiz do projeto:"
Write-Host $exe
Write-Host ""
Write-Host "Banco e exports (mesmo caminho do python -m app.main):"
Write-Host "  data\ponto_v2.db"
Write-Host "  exports\relatorio_ponto_*.csv"
