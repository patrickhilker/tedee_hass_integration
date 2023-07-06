import logging
from datetime import timedelta

from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.update_coordinator import (DataUpdateCoordinator,
                                                      UpdateFailed)
from pytedee_async import TedeeAuthException, TedeeClientException

SCAN_INTERVAL = timedelta(seconds=3600)

_LOGGER = logging.getLogger(__name__)



class TedeeApiCoordinator(DataUpdateCoordinator):
    """Class to handle fetching data from the tedee API centrally"""

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
            await self._tedee_client.get_locks()
        except TedeeAuthException as ex:
            msg = "Authentication failed. \
                            Personal Key is either invalid, doesn't have the correct scopes \
                            (Devices: Read, Locks: Operate) or is expired."
            _LOGGER.error(msg)
            raise ConfigEntryAuthFailed(msg) from ex
        except (TedeeClientException, Exception) as ex:
            _LOGGER.error(ex)
            raise UpdateFailed("Querying API failed. Error: %s", ex)
        
        if not self._tedee_client.locks_dict:
            # No locks found; abort setup routine.
            _LOGGER.warn("No locks found in your account.")

        _LOGGER.debug("available_locks: %s", ", ".join(map(str, self._tedee_client.locks_dict.keys())))

        return self._tedee_client.locks_dict