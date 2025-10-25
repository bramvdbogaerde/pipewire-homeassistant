# PipeWire to Home Assistant Event Bridge

Monitors PipeWire audio streams and sends events to Home Assistant when audio playback starts or stops.

## Installation

```bash
pip install -r requirements.txt
```

## Configuration

1. Copy `config.example.yaml` to `config.yaml`
2. Edit `config.yaml` with your Home Assistant URL and long-lived access token

## Usage

```bash
python main.py
```

## Events

The script fires two event types to Home Assistant:

- `pipewire_start_playing`: Fired when an audio stream starts playing
- `pipewire_stop_playing`: Fired when an audio stream stops

Each event includes:
- `node_id`: PipeWire node ID
- `application`: Application name (if available)
