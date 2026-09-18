param(
    [ValidateSet('Build','Preview','Render','Export','Validate','StageChecks','All')]
    [string]$Task = 'Preview',
    [string]$Blender = 'D:\Program Files\Steam\steamapps\common\Blender\blender.exe'
)
$ErrorActionPreference = 'Stop'
$projectDir = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot '..')).Path
if (-not (Test-Path -LiteralPath $Blender)) { throw "Blender executable not found: $Blender" }
function Invoke-GsxBlender([string[]]$BlenderArgs) {
    & $Blender @BlenderArgs
    if ($LASTEXITCODE -ne 0) { throw "Blender failed with exit code $LASTEXITCODE" }
}
Push-Location -LiteralPath $projectDir
try {
    if ($Task -in @('Build','All')) { Invoke-GsxBlender @('--background','--factory-startup','--python','scripts/build_all.py') }
    if ($Task -in @('Preview','Render','Export','All') -and -not (Test-Path -LiteralPath 'blends/10_final.blend')) { throw 'Run -Task Build before rendering or exporting.' }
    if ($Task -eq 'Preview') { Invoke-GsxBlender @('--background','blends/10_final.blend','--python','scripts/render.py','--','--preview') }
    if ($Task -in @('Export','All')) { Invoke-GsxBlender @('--background','blends/10_final.blend','--python','scripts/export_model.py') }
    if ($Task -in @('Validate','All')) { Invoke-GsxBlender @('--background','--factory-startup','--python','scripts/validate_exports.py') }
    if ($Task -in @('StageChecks','All')) { Invoke-GsxBlender @('--background','--factory-startup','--python','scripts/render_stages.py') }
    if ($Task -in @('Render','All')) { Invoke-GsxBlender @('--background','blends/10_final.blend','--python','scripts/render.py','--','Camera_Front_3Q','Camera_Right_Ortho','Camera_Rear_3Q','Camera_Left_3Q','Camera_Cockpit','Camera_Wheel_Detail') }
} finally { Pop-Location }
