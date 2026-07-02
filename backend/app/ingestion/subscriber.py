"""The telemetry subscriber.

paho-mqtt runs its network loop on a background thread (loop_start). Each
message callback fires on that thread, so it opens its OWN SessionLocal — sync
SQLAlchemy is fine across threads as long as sessions are not shared.

Restart survival (Phase 1 exit criterion): a fixed client_id + clean_session=
False gives us a *persistent session*. Messages published while the backend is
down are queued by the broker and redelivered on reconnect; QoS 1 guarantees
at-least-once, and the (device_id, ts) primary key makes the duplicate a no-op.
"""
from __future__ import annotations

import json
import logging

import paho.mqtt.client as mqtt
from paho.mqtt.enums import CallbackAPIVersion
from pydantic import ValidationError

from app.core.config import settings
from app.core.db import SessionLocal
from app.models.telemetry import TelemetryIngest
from app.services import telemetry_service
from app.services.telemetry_service import UnknownDevice

logger = logging.getLogger(__name__)

CLIENT_ID = "heimdall-ingestion"

_client: mqtt.Client | None = None


def _topics() -> list[tuple[str, int]]:
    p = settings.MQTT_TOPIC_PREFIX
    return [(f"{p}/+/telemetry", settings.MQTT_QOS), (f"{p}/+/status", settings.MQTT_QOS)]


def _hardware_id(topic: str) -> str | None:
    # heimdall/<hardware_id>/{telemetry,status}
    parts = topic.split("/")
    return parts[1] if len(parts) == 3 else None


def _on_connect(client, userdata, flags, reason_code, properties=None) -> None:
    if reason_code != 0:
        logger.error("mqtt_connect_failed", extra={"reason_code": str(reason_code)})
        return
    client.subscribe(_topics())
    logger.info("mqtt_connected", extra={"topics": [t for t, _ in _topics()]})


def _on_disconnect(client, userdata, flags, reason_code, properties=None) -> None:
    # Fixed client_id + clean_session=False means EXACTLY ONE subscriber may run.
    # A second instance (a stray `fastapi dev`, or multiple uvicorn workers) will
    # trigger the broker's "session taken over" and the two will fight forever —
    # this log is how you'd notice. paho auto-reconnects on genuine drops.
    if reason_code != 0:
        logger.warning("mqtt_disconnected", extra={"reason_code": str(reason_code)})


def _on_message(client, userdata, msg: mqtt.MQTTMessage) -> None:
    # A crash here would kill the network-loop thread and silently stop ingestion,
    # so every failure mode is caught and logged, never raised.
    hardware_id = _hardware_id(msg.topic)
    if hardware_id is None:
        return
    try:
        body = json.loads(msg.payload)
    except (json.JSONDecodeError, UnicodeDecodeError):
        logger.warning("mqtt_bad_payload", extra={"topic": msg.topic})
        return

    with SessionLocal() as db:
        try:
            if msg.topic.endswith("/status"):
                if isinstance(body, dict) and body.get("state") == "offline":
                    telemetry_service.mark_offline(db, hardware_id)
                return

            reading = TelemetryIngest.model_validate(body)
            telemetry_service.record(db, hardware_id, reading.ts, reading.readings)
        except UnknownDevice:
            logger.info("telemetry_dropped_unclaimed", extra={"hardware_id": hardware_id})
        except ValidationError as exc:
            logger.warning(
                "telemetry_invalid", extra={"hardware_id": hardware_id, "errors": exc.errors()}
            )
        except Exception:
            logger.exception("telemetry_ingest_error", extra={"hardware_id": hardware_id})


def start() -> None:
    global _client
    if _client is not None:
        return
    client = mqtt.Client(
        CallbackAPIVersion.VERSION2,
        client_id=CLIENT_ID,
        clean_session=False,  # persistent session -> queued redelivery on reconnect
        protocol=mqtt.MQTTv311,
    )
    client.on_connect = _on_connect
    client.on_disconnect = _on_disconnect
    client.on_message = _on_message
    client.reconnect_delay_set(min_delay=1, max_delay=30)
    client.connect_async(settings.MQTT_BROKER_HOST, settings.MQTT_BROKER_PORT)
    client.loop_start()
    _client = client
    logger.info(
        "ingestion_started",
        extra={"broker": f"{settings.MQTT_BROKER_HOST}:{settings.MQTT_BROKER_PORT}"},
    )


def stop() -> None:
    global _client
    if _client is None:
        return
    _client.loop_stop()
    _client.disconnect()
    _client = None
    logger.info("ingestion_stopped")
