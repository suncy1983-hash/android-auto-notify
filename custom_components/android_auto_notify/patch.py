"""Inject ``car_ui: true`` into mobile_app notifications for chosen phones.

Every Companion-app notification leaves Home Assistant through one of two
places in the mobile_app integration, whoever sent it (the legacy
``notify.mobile_app_*`` actions, the ``notify.<phone>`` entity, groups,
other integrations):

* ``PushChannel.async_send_notification`` - local push over the app's
  websocket, used while the phone is connected to Home Assistant;
* ``mobile_app.notify._send_message`` - cloud push (Firebase), used otherwise
  and as the fallback when a local push is not confirmed.

Both are wrapped here. For a phone that is enabled in this integration the
payload gets ``data.car_ui = true`` before it is sent, so the notification is
shown on Android Auto as well. Nothing is sent twice, and an explicit
``car_ui: false`` set by the sender is respected.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
import logging
from typing import Any

from homeassistant.components.mobile_app import notify as ma_notify
from homeassistant.components.mobile_app.const import ATTR_WEBHOOK_ID
from homeassistant.components.mobile_app.push_notification import PushChannel

from .const import COMMAND_MESSAGES, COMMAND_PREFIX

_LOGGER = logging.getLogger(__name__)


@dataclass
class _State:
    """Phones that are enabled, by webhook id, with their exclude words."""

    targets: dict[str, list[str]] = field(default_factory=dict)
    orig_push: Callable[..., Any] | None = None
    orig_send: Callable[..., Any] | None = None


_STATE = _State()


def _excluded(data: dict[str, Any], words: list[str]) -> bool:
    if not words:
        return False
    text = f"{data.get('title', '')} {data.get('message', '')}".lower()
    return any(word in text for word in words)


def _inject(webhook_id: str | None, data: dict[str, Any]) -> None:
    """Add car_ui to the payload in place, if this phone is enabled."""
    if webhook_id is None or webhook_id not in _STATE.targets:
        return
    if not isinstance(data, dict):
        return
    message = str(data.get("message", ""))
    if message in COMMAND_MESSAGES or message.startswith(COMMAND_PREFIX):
        return
    if _excluded(data, _STATE.targets[webhook_id]):
        return
    extra = data.get("data")
    if not isinstance(extra, dict):
        extra = {}
    if "car_ui" in extra:  # the sender decided, leave it
        return
    # A new dict, so a caller's own data dict is never changed.
    data["data"] = {**extra, "car_ui": True}


def _patched_push(self: PushChannel, data, fallback_send):
    try:
        _inject(getattr(self, "webhook_id", None), data)
    except Exception:  # never block a notification
        _LOGGER.exception("Could not add car_ui to a local push notification")
    return _STATE.orig_push(self, data, fallback_send)


async def _patched_send(session, entry, data):
    try:
        _inject(entry.data.get(ATTR_WEBHOOK_ID), data)
    except Exception:  # never block a notification
        _LOGGER.exception("Could not add car_ui to a cloud push notification")
    return await _STATE.orig_send(session, entry, data)


def enable(webhook_id: str, exclude: list[str]) -> None:
    """Turn on car_ui for one phone, installing the wrappers if needed."""
    _STATE.targets[webhook_id] = [w.strip().lower() for w in exclude if w.strip()]
    if _STATE.orig_push is None:
        _STATE.orig_push = PushChannel.async_send_notification
        PushChannel.async_send_notification = _patched_push
    if _STATE.orig_send is None:
        _STATE.orig_send = ma_notify._send_message  # noqa: SLF001
        ma_notify._send_message = _patched_send  # noqa: SLF001
    _LOGGER.debug("Android Auto notifications on for %s", webhook_id)


def disable(webhook_id: str) -> None:
    """Turn off one phone; restore mobile_app when no phone is left."""
    _STATE.targets.pop(webhook_id, None)
    if _STATE.targets:
        return
    if _STATE.orig_push is not None:
        PushChannel.async_send_notification = _STATE.orig_push
        _STATE.orig_push = None
    if _STATE.orig_send is not None:
        ma_notify._send_message = _STATE.orig_send  # noqa: SLF001
        _STATE.orig_send = None
