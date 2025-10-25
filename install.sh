#!/bin/bash
set -e

echo "Installing PipeWire to Home Assistant Media Player Bridge..."

# Installation paths
INSTALL_DIR="$HOME/.local/share/pipewire-homeassistant"
CONFIG_DIR="$HOME/.config/pipewire-homeassistant"
SYSTEMD_DIR="$HOME/.config/systemd/user"
VENV_DIR="$INSTALL_DIR/venv"

# Create directories
echo "Creating directories..."
mkdir -p "$INSTALL_DIR"
mkdir -p "$CONFIG_DIR"
mkdir -p "$SYSTEMD_DIR"

# Copy Python files
echo "Copying application files..."
mkdir -p "$INSTALL_DIR/src"
cp src/main.py "$INSTALL_DIR/src/"
cp src/pipewire_monitor.py "$INSTALL_DIR/src/"
cp src/homeassistant_client.py "$INSTALL_DIR/src/"
cp requirements.txt "$INSTALL_DIR/"

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv "$VENV_DIR"

# Install Python dependencies
echo "Installing Python dependencies..."
"$VENV_DIR/bin/pip" install --upgrade pip
"$VENV_DIR/bin/pip" install -r "$INSTALL_DIR/requirements.txt"

# Copy config file if it doesn't exist
if [ ! -f "$CONFIG_DIR/config.yaml" ]; then
    echo "Creating default config file..."
    cp config/config.example.yaml "$CONFIG_DIR/config.yaml"
    echo "Please edit $CONFIG_DIR/config.yaml with your Home Assistant settings"
else
    echo "Config file already exists, skipping..."
fi

# Install systemd service
echo "Installing systemd service..."
cp config/pipewire-homeassistant.service "$SYSTEMD_DIR/"

# Reload systemd
echo "Reloading systemd..."
systemctl --user daemon-reload

echo ""
echo "Installation complete!"
echo ""
echo "Next steps:"
echo "1. Edit the configuration file: $CONFIG_DIR/config.yaml"
echo "2. Enable the service: systemctl --user enable pipewire-homeassistant.service"
echo "3. Start the service: systemctl --user start pipewire-homeassistant.service"
echo "4. Check status: systemctl --user status pipewire-homeassistant.service"
echo "5. View logs: journalctl --user -u pipewire-homeassistant.service -f"
