#!/usr/bin/env python3
"""Main script for PipeWire to Home Assistant media player bridge."""

import logging
import signal
import sys
import yaml
from pathlib import Path
from pipewire_monitor import PipeWireMonitor
from homeassistant_client import HomeAssistantClient

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def load_config():
    """Load configuration from config.yaml."""
    # Try XDG config directory first, then local config directory
    xdg_config = Path.home() / '.config' / 'pipewire-homeassistant' / 'config.yaml'
    local_config = Path(__file__).parent / 'config' / 'config.yaml'

    if xdg_config.exists():
        config_path = xdg_config
    elif local_config.exists():
        config_path = local_config
    else:
        logger.error("config.yaml not found. Copy config/config.example.yaml to ~/.config/pipewire-homeassistant/config.yaml or config/config.yaml")
        sys.exit(1)

    with open(config_path, 'r') as f:
        return yaml.safe_load(f)


def main():
    """Main entry point."""
    config = load_config()

    ha_config = config.get('homeassistant', {})
    ha_client = HomeAssistantClient(
        url=ha_config.get('url'),
        token=ha_config.get('token'),
        device_name=ha_config.get('device_name')
    )

    monitor = PipeWireMonitor(
        on_start_playing=ha_client.send_start_playing,
        on_stop_playing=ha_client.send_stop_playing
    )

    # Handle graceful shutdown
    def signal_handler(sig, frame):
        logger.info("Shutting down...")
        monitor.stop()
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # Start monitoring
    monitor.start()

    # Keep main thread alive
    signal.pause()


if __name__ == '__main__':
    main()
