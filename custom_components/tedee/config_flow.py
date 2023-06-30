from typing import Any, Dict

import homeassistant.helpers.config_validation as cv
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_ACCESS_TOKEN
from homeassistant.core import callback

from .const import DOMAIN, NAME

PERSONAL_KEY_SCHEMA = vol.Schema({vol.Required(CONF_ACCESS_TOKEN): cv.string})

class TedeeConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    
    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_CLOUD_POLL

    reauth_entry: ConfigEntry = None
    
    def __init__(self):
        self._errors = {}
        self._reload = False
    
    async def async_step_user(self, user_input=None):
        self._errors = {}
        
        if user_input is not None:
            return self.async_create_entry(
                    title=NAME, 
                    data=user_input
                    
                )
        
        return self.async_show_form(
            step_id="user", data_schema=PERSONAL_KEY_SCHEMA
        )
    
    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: ConfigEntry,
    ) -> config_entries.OptionsFlow:
        """Create the options flow."""
        return OptionsFlowHandler(config_entry)
    
    
    async def async_step_reauth(self, user_input=None):
        """Perform reauth upon an API authentication error."""
        self.reauth_entry = self.hass.config_entries.async_get_entry(
            self.context["entry_id"]
        )
        return await self.async_step_reauth_confirm()

    async def async_step_reauth_confirm(self, user_input=None):
        """Dialog that informs the user that reauth is required."""
        if user_input is None:
            return self.async_show_form(
                step_id="reauth_confirm",
                data_schema=PERSONAL_KEY_SCHEMA,
            )
        self.hass.config_entries.async_update_entry(
                self.reauth_entry, data=user_input
            )   
        await self.hass.config_entries.async_reload(self.reauth_entry.entry_id)
        return self.async_abort(reason="reauth_successful")
    
    
class OptionsFlowHandler(config_entries.OptionsFlow):
    """Handles options flow for the component."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        self.config_entry = config_entry

    async def async_step_init(
        self, user_input: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Manage the options for the custom component."""
        errors: Dict[str, str] = {}

        if user_input is not None:
            if not errors:
                # write entry to config and not options dict, pass empty options out
                self.hass.config_entries.async_update_entry(
                    self.config_entry, data=user_input, options=self.config_entry.options
                )   
                return self.async_create_entry(
                    title="",
                    data={}
                )

        options_schema = PERSONAL_KEY_SCHEMA

        return self.async_show_form(
            step_id="init", data_schema=options_schema, errors=errors
        )