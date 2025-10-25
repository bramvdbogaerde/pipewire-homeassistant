# PipeWire to Home Assistant Media Player Bridge

Monitors PipeWire audio streams and updates a Home Assistant media_player entity to reflect audio playback status.

## Installation

Run the installation script:

```bash
./install.sh
```

This will:
- Install the application to `~/.local/share/pipewire-homeassistant/`
- Create a Python virtual environment with all dependencies
- Copy the example configuration to `~/.config/pipewire-homeassistant/config.yaml`
- Install the systemd user service

## Configuration

Edit the configuration file at `~/.config/pipewire-homeassistant/config.yaml`:

```yaml
homeassistant:
  url: "http://homeassistant.local:8123"
  token: "your_long_lived_access_token_here"
  # Optional: specify device name (defaults to hostname if not set)
  # device_name: "my-computer"
```

### Getting a Home Assistant Long-Lived Access Token

1. In Home Assistant, go to your profile (click your username in the sidebar)
2. Scroll down to "Long-Lived Access Tokens"
3. Click "Create Token"
4. Give it a name (e.g., "PipeWire Monitor")
5. Copy the token and paste it into your config.yaml

## Running the Service

Enable and start the systemd service:

```bash
systemctl --user enable pipewire-homeassistant.service
systemctl --user start pipewire-homeassistant.service
```

Check the service status:

```bash
systemctl --user status pipewire-homeassistant.service
```

View logs:

```bash
journalctl --user -u pipewire-homeassistant.service -f
```

## Home Assistant Integration

The service creates a media_player entity in Home Assistant with the ID:
`media_player.pipewire_<device_name>`

For example, if your hostname is `desktop-pc`, the entity will be:
`media_player.pipewire_desktop_pc`

### Entity States

- `playing`: At least one audio stream is active
- `idle`: No audio streams are active

### Entity Attributes

- `friendly_name`: Display name (e.g., "PipeWire Audio - desktop-pc")
- `device_class`: "speaker"
- `app_name`: Name of the first active application
- `active_streams`: Number of active audio streams
- `applications`: List of all active application names

### Example Automations

Trigger when audio starts playing:

```yaml
automation:
  - alias: "Audio Started Playing"
    trigger:
      - platform: state
        entity_id: media_player.pipewire_desktop_pc
        to: "playing"
    action:
      - service: notify.mobile_app
        data:
          message: "Audio playback started: {{ state_attr('media_player.pipewire_desktop_pc', 'app_name') }}"
```

Trigger when audio stops:

```yaml
automation:
  - alias: "Audio Stopped Playing"
    trigger:
      - platform: state
        entity_id: media_player.pipewire_desktop_pc
        to: "idle"
    action:
      - service: light.turn_off
        target:
          entity_id: light.office
```
