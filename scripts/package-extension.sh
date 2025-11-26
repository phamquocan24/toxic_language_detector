#!/bin/bash
# Package Chrome Extension

set -e

echo "📦 Packaging Toxic Language Detector Extension..."
echo ""

# Get version from manifest
VERSION=$(grep -oP '"version":\s*"\K[^"]+' extension/manifest.json)
OUTPUT_NAME="toxic-detector-extension-v${VERSION}.zip"
OUTPUT_PATH="dist/${OUTPUT_NAME}"

# Create dist directory
mkdir -p dist

# Remove old package if exists
rm -f "${OUTPUT_PATH}"

echo "📋 Extension Info:"
echo "   Version: ${VERSION}"
echo "   Output:  ${OUTPUT_PATH}"
echo ""

# Create ZIP excluding unnecessary files
echo "🗜️  Creating ZIP package..."
cd extension
zip -r "../${OUTPUT_PATH}" . \
  -x "*.git*" \
  -x "*.DS_Store" \
  -x "node_modules/*" \
  -x "*.md" \
  -x "*.sh" \
  -x "*.ps1" \
  -x "test/*" \
  -x "*.map"

cd ..

# Verify package
if [ -f "${OUTPUT_PATH}" ]; then
    SIZE=$(du -h "${OUTPUT_PATH}" | cut -f1)
    echo ""
    echo "✅ Extension packaged successfully!"
    echo ""
    echo "📦 Package Details:"
    echo "   File:    ${OUTPUT_PATH}"
    echo "   Size:    ${SIZE}"
    echo "   Version: ${VERSION}"
    echo ""
    echo "📋 Package Contents:"
    unzip -l "${OUTPUT_PATH}" | head -20
    echo ""
    echo "🚀 Next Steps:"
    echo "   1. Go to: https://chrome.google.com/webstore/devconsole/"
    echo "   2. Click 'New Item' or update existing"
    echo "   3. Upload: ${OUTPUT_PATH}"
    echo "   4. Fill store listing details"
    echo "   5. Submit for review"
    echo ""
    echo "📝 Store Listing Checklist:"
    echo "   [ ] Product name and description"
    echo "   [ ] Category: Social & Communication"
    echo "   [ ] Icon: 128x128 pixels"
    echo "   [ ] Screenshots: At least 1 (1280x800 or 640x400)"
    echo "   [ ] Privacy policy URL (if collecting data)"
    echo "   [ ] Single purpose description"
    echo "   [ ] Permission justifications"
else
    echo "❌ Packaging failed!"
    exit 1
fi

