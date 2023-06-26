import logging

from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_ACCESS_TOKEN
from pytedee_async import TedeeClient, TedeeClientException

from .const import DOMAIN, CLIENT

PLATFORMS = ["lock", "sensor", "button"]

_LOGGER = logging.getLogger(__name__)

async def async_setup(hass, config):
    logging.debug("Setting up Tedee integration...")
    hass.data.setdefault(DOMAIN, {})
    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    pak = entry.data.get(CONF_ACCESS_TOKEN)
    try:
        tedee_client = await TedeeClient.create(pak)
    except TedeeClientException as exc:
        _LOGGER.error(exc)
        return

    _LOGGER.debug("available_locks: %s", tedee_client.locks)

    if not tedee_client.locks:
        # No locks found; abort setup routine.
        _LOGGER.warn("No locks found in your account")
        return
    
    hass.data[DOMAIN][CLIENT] = tedee_client

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
        

    return True