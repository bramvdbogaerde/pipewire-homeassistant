#!/usr/bin/env python3
"""Home Assistant media player state update client."""

import logging
import requests
import socket
from typing import Dict, Any, Optional, Set

logger = logging.getLogger(__name__)


class HomeAssistantClient:
    """Client for updating media_player entity states in Home Assistant."""

    def __init__(self, url: str, token: str, device_name: Optional[str] = None):
        self.url = url.rstrip('/')
        self.token = token
        self.device_name = device_name or socket.gethostname()
        self.headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
        self.active_streams: Dict[int, str] = {}

    def update_state(self, entity_id: str, state: str, attributes: Dict[str, Any]) -> bool:
        """Update entity state in Home Assistant."""
        try:
            response = requests.post(
                f'{self.url}/api/states/{entity_id}',
                json={'state': state, 'attributes': attributes},
                headers=self.headers,
                timeout=5
            )
            response.raise_for_status()
            logger.info(f"State updated for {entity_id}: {state}")
            return True
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to update state for {entity_id}: {e}")
            return False

    def send_start_playing(self, node_id: int, app_name: str):
        """Update state when audio starts playing."""
        self.active_streams[node_id] = app_name
        logger.info(f"Stream started: {app_name} (node {node_id})")
        self._update_media_player_state()

    def send_stop_playing(self, node_id: int, app_name: str):
        """Update state when audio stops playing."""
        self.active_streams.pop(node_id, None)
        logger.info(f"Stream stopped: {app_name} (node {node_id})")
        self._update_media_player_state()

    def _update_media_player_state(self):
        """Update the media_player state in Home Assistant."""
        state = "playing" if self.active_streams else "idle"
        entity_id = f"media_player.pipewire_{self.device_name.lower().replace('-', '_')}"

        # Get application names
        app_names = list(self.active_streams.values())

        attributes = {
            'friendly_name': f'PipeWire Audio - {self.device_name}',
            'device_class': 'speaker',
            'supported_features': 0,  # Read-only media player
            'app_name': app_names[0] if app_names else None,
            'active_streams': len(self.active_streams),
            'applications': app_names
        }

        self.update_state(entity_id=entity_id, state=state, attributes=attributes)
