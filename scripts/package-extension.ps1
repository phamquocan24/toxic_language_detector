# Package Chrome Extension (Windows PowerShell)

Write-Host "📦 Packaging Toxic Language Detector Extension..." -ForegroundColor Green
Write-Host ""

# Get version from manifest
$manifest = Get-Content "extension/manifest.json" | ConvertFrom-Json
$version = $manifest.version
$outputName = "toxic-detector-extension-v$version.zip"
$outputPath = "dist/$outputName"

# Create dist directory
New-Item -ItemType Directory -Force -Path "dist" | Out-Null

# Remove old package if exists
if (Test-Path $outputPath) {
    Remove-Item $outputPath
}

Write-Host "📋 Extension Info:" -ForegroundColor Cyan
Write-Host "   Version: $version" -ForegroundColor White
Write-Host "   Output:  $outputPath" -ForegroundColor White
Write-Host ""

# Files to exclude
$excludePatterns = @(
    "*.git*",
    "*.DS_Store",
    "node_modules",
    "*.md",
    "*.sh",
    "*.ps1",
    "test",
    "*.map"
)

# Create ZIP
Write-Host "🗜️  Creating ZIP package..." -ForegroundColor Cyan

# Get all files in extension folder, excluding patterns
$files = Get-ChildItem -Path "extension" -Recurse | Where-Object {
    $item = $_
    $exclude = $false
    foreach ($pattern in $excludePatterns) {
        if ($item.FullName -like "*$pattern*") {
            $exclude = $true
            break
        }
    }
    !$exclude -and !$item.PSIsContainer
}

# Create archive
Compress-Archive -Path $files.FullName -DestinationPath $outputPath -Force

# Verify package
if (Test-Path $outputPath) {
    $size = [math]::Round((Get-Item $outputPath).Length / 1KB, 2)
    
    Write-Host ""
    Write-Host "✅ Extension packaged successfully!" -ForegroundColor Green
    Write-Host ""
    Write-Host "📦 Package Details:" -ForegroundColor Cyan
    Write-Host "   File:    $outputPath" -ForegroundColor White
    Write-Host "   Size:    $size KB" -ForegroundColor White
    Write-Host "   Version: $version" -ForegroundColor White
    Write-Host ""
    Write-Host "🚀 Next Steps:" -ForegroundColor Yellow
    Write-Host "   1. Go to: https://chrome.google.com/webstore/devconsole/"
    Write-Host "   2. Click 'New Item' or update existing"
    Write-Host "   3. Upload: $outputPath"
    Write-Host "   4. Fill store listing details"
    Write-Host "   5. Submit for review"
    Write-Host ""
    Write-Host "📝 Store Listing Checklist:" -ForegroundColor Yellow
    Write-Host "   [ ] Product name and description"
    Write-Host "   [ ] Category: Social & Communication"
    Write-Host "   [ ] Icon: 128x128 pixels"
    Write-Host "   [ ] Screenshots: At least 1 (1280x800 or 640x400)"
    Write-Host "   [ ] Privacy policy URL (if collecting data)"
    Write-Host "   [ ] Single purpose description"
    Write-Host "   [ ] Permission justifications"
} else {
    Write-Host "❌ Packaging failed!" -ForegroundColor Red
    exit 1
}

