import logging

from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_ACCESS_TOKEN
from homeassistant.exceptions import ConfigEntryAuthFailed, ConfigEntryNotReady
from pytedee_async import TedeeClient, TedeeClientException, TedeeAuthException

from .const import DOMAIN, CLIENT

PLATFORMS = ["lock", "sensor", "button"]

_LOGGER = logging.getLogger(__name__)

async def async_setup(hass, config):
    logging.debug("Setting up Tedee integration...")
    hass.data.setdefault(DOMAIN, {})
    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Integration setup"""
    entry.async_on_unload(entry.add_update_listener(options_update_listener))

    pak = entry.data.get(CONF_ACCESS_TOKEN)

    try:
        tedee_client = await TedeeClient.create(pak)
    except TedeeAuthException as ex:
        _LOGGER.error(f"Authentication failed. \
                        Personal Key is either invalid, doesn't have the correct scopes \
                        (Devices: Read, Locks: Operate) or is expired."
                        )
        return False
        # TODO: raise ConfigEntryAuthFailed(...) from ex
        # TODO: implement handler in config_flow 
    except (TedeeClientException, Exception) as ex:
        _LOGGER.error(ex)
        raise ConfigEntryNotReady(f"Tedee failed to setup. Error: {ex}.") from ex

    _LOGGER.debug("available_locks: %s", tedee_client.locks)

    if not tedee_client.locks:
        # No locks found; abort setup routine.
        _LOGGER.warn("No locks found in your account")
        return False
    
    hass.data[DOMAIN][CLIENT] = tedee_client

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
        
    return True


async def options_update_listener(hass: HomeAssistant, entry: ConfigEntry):
    """Handle options update."""
    await hass.config_entries.async_reload(entry.entry_id)


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Unload a config entry."""
    # services = list(hass.services.async_services().get(DOMAIN).keys())
    # [hass.services.async_remove(DOMAIN, service) for service in services]

    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

    if unload_ok:
        hass.data[DOMAIN].pop(CLIENT)
        hass.data[DOMAIN] = {}

    return unload_ok