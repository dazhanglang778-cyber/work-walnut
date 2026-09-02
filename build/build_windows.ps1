$ErrorActionPreference = "Stop"

$ProjectRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$OutputRoot = Join-Path $ProjectRoot "build-output"
$DistRoot = Join-Path $OutputRoot "dist"
$WorkRoot = Join-Path $OutputRoot "work-windows"
$ReleaseRoot = Join-Path $OutputRoot "release"
$ArtifactName = "工作坚果-Windows-x64-v1.0.0"
$ArtifactPath = Join-Path $ReleaseRoot "$ArtifactName.zip"

New-Item -ItemType Directory -Force -Path $OutputRoot, $ReleaseRoot | Out-Null

python -m PyInstaller `
    --clean `
    --noconfirm `
    --distpath $DistRoot `
    --workpath $WorkRoot `
    (Join-Path $PSScriptRoot "WorkWalnut.spec")

if ($LASTEXITCODE -ne 0) {
    throw "PyInstaller 构建失败，退出代码：$LASTEXITCODE"
}

$BuiltFolder = Join-Path $DistRoot "工作坚果"
if (-not (Test-Path -LiteralPath $BuiltFolder -PathType Container)) {
    throw "构建输出不存在：$BuiltFolder"
}

if (Test-Path -LiteralPath $ArtifactPath) {
    Remove-Item -LiteralPath $ArtifactPath -Force
}

Compress-Archive `
    -LiteralPath $BuiltFolder `
    -DestinationPath $ArtifactPath `
    -CompressionLevel Optimal

$Hash = (Get-FileHash -Algorithm SHA256 -LiteralPath $ArtifactPath).Hash.ToLowerInvariant()
Set-Content `
    -LiteralPath (Join-Path $ReleaseRoot "SHA256SUMS-Windows.txt") `
    -Encoding utf8 `
    -Value "$Hash  $ArtifactName.zip"

Write-Output $ArtifactPath
