"""Android Auto értesítések: every notification to a phone also on Android Auto."""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from . import patch
from .const import CONF_EXCLUDE, CONF_WEBHOOK_ID


def _excludes(entry: ConfigEntry) -> list[str]:
    raw = entry.options.get(CONF_EXCLUDE, "") or ""
    return [w for w in raw.split(",") if w.strip()]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Enable car_ui for the phone this entry was set up for."""
    patch.enable(entry.data[CONF_WEBHOOK_ID], _excludes(entry))
    entry.async_on_unload(entry.add_update_listener(_async_update))
    return True


async def _async_update(hass: HomeAssistant, entry: ConfigEntry) -> None:
    patch.enable(entry.data[CONF_WEBHOOK_ID], _excludes(entry))


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Stop adding car_ui for this phone."""
    patch.disable(entry.data[CONF_WEBHOOK_ID])
    return True
