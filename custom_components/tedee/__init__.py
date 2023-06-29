import logging

from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_ACCESS_TOKEN
from homeassistant.exceptions import ConfigEntryAuthFailed, ConfigEntryNotReady
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from pytedee_async import TedeeClient, TedeeClientException, TedeeAuthException, TedeeConnectionException
from datetime import timedelta

from .const import DOMAIN, CLIENT

PLATFORMS = ["lock", "sensor", "button"]
SCAN_INTERVAL = timedelta(seconds=15)

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
    hass.data[DOMAIN][entry.entry_id] = tedee_client

    coordinator = TedeeApiCoordinator(tedee_client)
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
        hass.data[DOMAIN].pop(CLIENT)
        hass.data[DOMAIN] = {}

    return unload_ok


class TedeeApiCoordinator(DataUpdateCoordinator):

    def __init__(self, hass, tedee_client):
        """Initialize coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            # Name of the data. For logging purposes.
            name="tedee API coordinator",
            # Polling interval. Will only be polled if there are subscribers.
            update_interval=SCAN_INTERVAL,
        )
        self._tedee_client = tedee_client

    async def _async_update_data(self):
        try:
            _LOGGER.debug("Update coordinator: Getting locks from API")
            self._tedee_client.get_locks()
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

        if not self._tedee_client.locks:
            # No locks found; abort setup routine.
            _LOGGER.warn("No locks found in your account")

        _LOGGER.debug(f"available_locks: {self._tedee_client.locks.keys()}")

        return self._tedee_client.locks
        