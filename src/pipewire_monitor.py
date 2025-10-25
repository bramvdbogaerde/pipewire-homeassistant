#!/usr/bin/env python3
"""Monitor PipeWire audio streams using pw-dump -m."""

import logging
import subprocess
import json
import threading
from typing import Callable, Set, Dict

logger = logging.getLogger(__name__)


class PipeWireMonitor:
    """Monitor PipeWire streams for playback state changes."""

    def __init__(self, on_start_playing: Callable, on_stop_playing: Callable):
        self.on_start_playing = on_start_playing
        self.on_stop_playing = on_stop_playing
        self.active_streams: Dict[int, str] = {}  # node_id -> app_name
        self.known_nodes: Set[int] = set()  # All known audio output nodes
        self.process = None
        self.monitor_thread = None
        self._running = False

    def _process_snapshot(self, nodes: list):
        """Process a complete snapshot from pw-dump."""
        current_nodes = set()

        for node in nodes:
            if node.get('type') != 'PipeWire:Interface:Node':
                continue

            info = node.get('info', {})
            props = info.get('props', {})
            state = info.get('state')
            node_id = node.get('id')

            # Check if this is an output/playback stream
            media_class = props.get('media.class', '')
            if 'Stream/Output/Audio' not in media_class and 'Audio/Sink' not in media_class:
                continue

            if not node_id:
                continue

            current_nodes.add(node_id)
            app_name = props.get('application.name', 'Unknown')

            # Detect state changes
            if state == 'running' and node_id not in self.active_streams:
                self.active_streams[node_id] = app_name
                self.on_start_playing(node_id, app_name)
            elif state in ['idle', 'suspended', 'paused'] and node_id in self.active_streams:
                app_name = self.active_streams.pop(node_id)
                self.on_stop_playing(node_id, app_name)
            elif state == 'running' and node_id in self.active_streams:
                # Update app name in case it changed
                self.active_streams[node_id] = app_name

        # Detect removed nodes - if a node was active and is now gone, mark as stopped
        removed_nodes = self.known_nodes - current_nodes
        for node_id in removed_nodes:
            if node_id in self.active_streams:
                app_name = self.active_streams.pop(node_id)
                logger.info(f"Node {node_id} removed from PipeWire")
                self.on_stop_playing(node_id, app_name)

        self.known_nodes = current_nodes

    def _monitor_loop(self):
        """Main monitoring loop reading from pw-dump -m."""
        try:
            self.process = subprocess.Popen(
                ['pw-dump', '-m'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            buffer = ""
            while self._running:
                char = self.process.stdout.read(1)
                if not char:
                    break

                buffer += char

                # Complete JSON array detected
                if char == '\n' and buffer.strip().endswith(']'):
                    try:
                        data = json.loads(buffer.strip())
                        if isinstance(data, list):
                            self._process_snapshot(data)
                        buffer = ""
                    except json.JSONDecodeError:
                        # Not complete yet, keep accumulating
                        pass

        except Exception as e:
            logger.error(f"Error in monitor loop: {e}")
        finally:
            if self.process:
                self.process.terminate()
                self.process.wait()

    def start(self):
        """Start monitoring PipeWire streams."""
        if self._running:
            return

        self._running = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        logger.info("Started monitoring PipeWire streams...")

    def stop(self):
        """Stop monitoring."""
        self._running = False
        if self.process:
            self.process.terminate()
        if self.monitor_thread:
            self.monitor_thread.join(timeout=2)
