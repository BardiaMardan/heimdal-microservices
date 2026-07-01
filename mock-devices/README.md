# mock-devices — Heimdall IIoT fleet simulator

Mock Industrial IoT devices for exercising Heimdall locally — boot a fleet,
they announce themselves and print claim codes, you claim them through the UI,
they fetch their tokens and stream telemetry over MQTT. Provisioning is
stdlib-only (`urllib`); telemetry needs one dependency (`paho-mqtt`) — install
with `pip install -r requirements.txt`.

This lives beside `backend/` and `frontend/` because it's a dev/test tool, not
part of the deployed system. Think of it as the stand-in for real ESP32 sensors
until you have hardware.

## Quick start

```bash
# 1. Backend must be running with a migrated DB (docs/notes/Note00-START-HERE.md)
cd ../backend && source venv/bin/activate && fastapi dev app/main.py

# 2. In another terminal:
cd mock-devices
python3 simulate.py            # boot fleet, print claim codes, stream after claimed
python3 simulate.py --once     # one reading per device after claim, then exit
python3 simulate.py --reset    # forget claimed state and re-onboard from scratch
```

Configure via env (defaults shown):

| Var | Default |
| --- | ------- |
| `HEIMDALL_API` | `http://localhost:8000/api/v1` |
| `HEIMDALL_INTERVAL` | `3` (seconds between readings) |
| `HEIMDALL_MQTT_HOST` | `localhost` |
| `HEIMDALL_MQTT_PORT` | `1883` |
| `HEIMDALL_MQTT_PREFIX` | `heimdall` |

Edit [`devices.json`](devices.json) to change the fleet (name, type, location).
Types: `machine`, `environmental`, `fleet`, `storage` — each streams distinct
telemetry (temp/vibration/rpm, humidity/CO₂, speed/fuel/GPS, door-open).

## How it works (the firmware lifecycle)

Each device in `devices.json` boots as a separate thread running the shared
firmware (`devices/base.py`):

1. **Announce** — `POST /provisioning/announce` with a deterministic `hardware_id`
   (uuid5 of the device name, so reruns never orphan rows) and the **sha256**
   of a locally generated 6-digit code and a provisioning secret.
2. **Print the claim code** in a big banner (you enter this in the UI).
3. **Poll** `GET /provisioning/status` every 2 seconds until a human claims it.
4. **Fetch the operational token** once via `POST /provisioning/token` (the
   provisioning secret proves it's the same device that announced). Stored in
   `.device_state.json` (gitignored) so reruns remember and skip straight to
   streaming.
5. **Stream telemetry** — `Device._send` publishes `{ts, readings}` to
   `heimdall/<hardware_id>/telemetry` (QoS 1); the per-type reading generators
   live in `devices/{machine,environmental,fleet,storage}.py`. On connect the
   device sets an MQTT Last Will so the backend flips it offline if it drops
   ungracefully, and publishes a retained `online` to clear it.

**Why this is realistic:** the device-as-client model (dial out, never listen),
the two-secret split (bootstrap code → operational token), and the control-plane
/ data-plane separation (claim over REST, telemetry over MQTT) are the shape of
AWS IoT / Azure DPS / GCP IoT Core. See
[Note07](../docs/notes/Note07-device-onboarding.md) for the reasoning.

## Transport split (by design)

Provisioning (the control plane) is HTTP over stdlib `urllib`; telemetry (the
data plane) is MQTT over `paho-mqtt` — the same split real firmware uses (HTTP/
DPS bootstrap, then an MQTT stream). Both planes are now verified end-to-end.
See [ADR-0002](../docs/adr/0002-mqtt-ingestion.md),
[ADR-0008](../docs/adr/0008-device-onboarding.md), and
[ADR-0009](../docs/adr/0009-telemetry-storage-and-ingestion.md).

## Package structure

```
mock-devices/
├── simulate.py           # threaded runner
├── devices.json          # fleet spec (name, type, location)
├── .device_state.json    # runtime (gitignored): hw_id -> {token, secret}
└── devices/
    ├── client.py         # HTTP helpers, hashing, state-file atomics
    ├── base.py           # Device class: the firmware every type shares
    ├── machine.py        # temp/vibration/rpm
    ├── environmental.py  # temp/humidity/CO₂
    ├── fleet.py          # speed/fuel/GPS
    └── storage.py        # temp/humidity/door-open
```

No `requests` (provisioning uses stdlib `urllib`); `paho-mqtt` is the sole
dependency, and only for the telemetry data plane. Runs on any Python 3.9+.
