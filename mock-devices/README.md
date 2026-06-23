# mock-devices

Mock IIoT devices ("ESPs") for exercising Heimdall locally — register devices and
simulate them emitting telemetry. **Standard-library Python only; nothing to
install.**

This lives beside `backend/` and `frontend/` because it's a dev/test tool, not
part of the deployed system. Think of it as the stand-in for real ESP32 sensors
until you have hardware.

## Quick start

```bash
# 1. Backend must be running with a migrated DB (see ../docs/notes/Note05...)
cd ../backend && source venv/bin/activate && fastapi dev app/main.py

# 2. In another terminal:
cd mock-devices
python3 simulate.py            # registers devices.json, then streams readings
python3 simulate.py --once     # one reading per device, then exit
python3 simulate.py --register-only
```

Configure via env vars (defaults shown):

| Var | Default |
| --- | ------- |
| `HEIMDALL_API` | `http://localhost:8000/api/v1` |
| `HEIMDALL_EMAIL` | `op@factory.io` |
| `HEIMDALL_PASSWORD` | `pw12345` |
| `HEIMDALL_INTERVAL` | `3` (seconds) |

Edit [`devices.json`](devices.json) to change the simulated fleet (name, type,
location). Types must be one of: `machine`, `environmental`, `fleet`, `storage`.

## Current limitation (by design)

The **telemetry transport doesn't exist yet.** Today `simulate.py` registers
devices via REST and *prints* the readings it would send. The `send_telemetry()`
function is a deliberate seam: once the MQTT ingestion path is built, that one
function becomes an MQTT publish to `heimdall/<device_id>/telemetry` (QoS 1) and
these turn into real publishers — no other changes. See
[ADR-0002](../docs/adr/0002-mqtt-ingestion.md).
