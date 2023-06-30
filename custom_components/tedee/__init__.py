import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_ACCESS_TOKEN
from homeassistant.core import HomeAssistant
from pytedee_async import TedeeClient

from .const import CLIENT, DOMAIN
from .coordinator import TedeeApiCoordinator

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

    tedee_client = TedeeClient(pak)

    hass.data[DOMAIN][entry.entry_id] = coordinator = TedeeApiCoordinator(hass, tedee_client)

    await coordinator.async_config_entry_first_refresh()

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
        hass.data[DOMAIN].pop(entry.entry_id)
        hass.data[DOMAIN] = {}

    return unload_ok
        