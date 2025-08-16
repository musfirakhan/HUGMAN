#!/bin/bash

echo "Creating HUGMAN Character Generator Transfer Package..."

# Create transfer directory
TRANSFER_DIR="hugman-transfer-$(date +%Y%m%d)"
mkdir -p "$TRANSFER_DIR"

echo "Copying core files..."
# Core Python files
cp llm.py "$TRANSFER_DIR/"
cp character_pipeline_viewer.py "$TRANSFER_DIR/"
cp character_pipeline.py "$TRANSFER_DIR/"
cp makehuman.py "$TRANSFER_DIR/"

# Animations folder
mkdir -p "$TRANSFER_DIR/animations"
cp animations/web_server.py "$TRANSFER_DIR/animations/"
cp animations/animation_viewer.html "$TRANSFER_DIR/animations/"
cp animations/text2animations.py "$TRANSFER_DIR/animations/"
cp animations/blender_retargetting.py "$TRANSFER_DIR/animations/"
cp animations/client.py "$TRANSFER_DIR/animations/"

# Docker files
cp Dockerfile "$TRANSFER_DIR/"
cp docker-compose.yml "$TRANSFER_DIR/"
cp requirements.txt "$TRANSFER_DIR/"
cp .dockerignore "$TRANSFER_DIR/"
cp DOCKER_README.md "$TRANSFER_DIR/"

# Data folders
echo "Copying data folders..."
cp -r data "$TRANSFER_DIR/"

# Model checkpoints
echo "Copying model checkpoints..."
cp -r check-point1400 "$TRANSFER_DIR/"
cp -r checkpoint-1000 "$TRANSFER_DIR/"
cp -r checkpoint-260 "$TRANSFER_DIR/"

# Configuration files
cp fashion_dataset.jsonl "$TRANSFER_DIR/"
cp dataset.json "$TRANSFER_DIR/"

# Create empty directories
mkdir -p "$TRANSFER_DIR/generated_characters"
mkdir -p "$TRANSFER_DIR/output"

# Create transfer instructions
cat > "$TRANSFER_DIR/TRANSFER_INSTRUCTIONS.txt" << 'EOF'
HUGMAN Character Generator - Transfer Instructions

1. Install Docker Desktop on the target machine
2. Extract this folder to the target machine
3. Open terminal/command prompt in this directory
4. Run: docker-compose up --build
5. Open browser to: http://localhost:5001

For Windows users:
- Install Docker Desktop for Windows
- Enable WSL 2 backend (recommended)
- Run the commands above

For troubleshooting, see DOCKER_README.md
EOF

# Create ZIP archive
echo "Creating ZIP archive..."
zip -r "${TRANSFER_DIR}.zip" "$TRANSFER_DIR"

echo "Transfer package created: ${TRANSFER_DIR}.zip"
echo "Size: $(du -h "${TRANSFER_DIR}.zip" | cut -f1)"
echo ""
echo "Transfer this ZIP file to the target machine."
echo "Extract and follow the instructions in TRANSFER_INSTRUCTIONS.txt"
