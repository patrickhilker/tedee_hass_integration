import logging
from homeassistant.components.button import ButtonEntity
from homeassistant.helpers.entity import DeviceInfo

from .const import DOMAIN, CLIENT

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, entry, async_add_entities):
    tedee_client = hass.data[DOMAIN][CLIENT]
    async_add_entities(
        [TedeeUnlatchButton(tedee_client, lock) for lock in tedee_client.locks], True
    )

class TedeeUnlatchButton(ButtonEntity):

    def __init__(self, tedee_client, lock):
        self._tedee_client = tedee_client
        self._lock = lock
        self._attr_has_entity_name = True
        self._attr_name = "Unlatch"
        self._attr_unique_id = f"{lock.id}-unlatch-button"

        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, self._lock.id)},
            name=self._lock.name,
            manufacturer="Tedee",
            model=self._lock.type
        )
        
    async def async_update(self):
        self._lock = self._tedee_client.find_lock(self._lock.id)

    async def async_press(self, **kwargs) -> None:
        await self._tedee_client.open(self._lock.id)