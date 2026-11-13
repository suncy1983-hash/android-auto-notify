"""Config flow for Android Auto értesítések."""

from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant.config_entries import (
    ConfigEntry,
    ConfigFlow,
    ConfigFlowResult,
    OptionsFlow,
)
from homeassistant.core import callback
from homeassistant.helpers import selector

from .const import CONF_EXCLUDE, CONF_WEBHOOK_ID, DOMAIN

MOBILE_APP = "mobile_app"


class AndroidAutoNotifyConfigFlow(ConfigFlow, domain=DOMAIN):
    """Pick the phone whose notifications should show on Android Auto."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        phones = {
            e.data[CONF_WEBHOOK_ID]: e.title
            for e in self.hass.config_entries.async_entries(MOBILE_APP)
            if CONF_WEBHOOK_ID in e.data
        }
        if not phones:
            return self.async_abort(reason="no_phones")

        if user_input is not None:
            webhook_id = user_input[CONF_WEBHOOK_ID]
            await self.async_set_unique_id(webhook_id)
            self._abort_if_unique_id_configured()
            return self.async_create_entry(
                title=phones.get(webhook_id, webhook_id),
                data={CONF_WEBHOOK_ID: webhook_id},
                options={CONF_EXCLUDE: user_input.get(CONF_EXCLUDE, "")},
            )

        schema = vol.Schema(
            {
                vol.Required(CONF_WEBHOOK_ID): selector.SelectSelector(
                    selector.SelectSelectorConfig(
                        options=[
                            selector.SelectOptionDict(value=k, label=v)
                            for k, v in phones.items()
                        ],
                        mode=selector.SelectSelectorMode.DROPDOWN,
                    )
                ),
                vol.Optional(CONF_EXCLUDE, default=""): selector.TextSelector(),
            }
        )
        return self.async_show_form(step_id="user", data_schema=schema)

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: ConfigEntry) -> OptionsFlow:
        return AndroidAutoNotifyOptionsFlow()


class AndroidAutoNotifyOptionsFlow(OptionsFlow):
    """Change the words that keep a notification off Android Auto."""

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        if user_input is not None:
            return self.async_create_entry(data=user_input)
        schema = vol.Schema(
            {
                vol.Optional(
                    CONF_EXCLUDE,
                    default=self.config_entry.options.get(CONF_EXCLUDE, ""),
                ): selector.TextSelector(),
            }
        )
        return self.async_show_form(step_id="init", data_schema=schema)
