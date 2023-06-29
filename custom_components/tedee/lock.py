import logging
from pytedee_async import TedeeClientException
from homeassistant.components.lock import SUPPORT_OPEN, LockEntity
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.const import ATTR_BATTERY_LEVEL, ATTR_ID, ATTR_BATTERY_CHARGING
from homeassistant.core import callback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, CLIENT


ATTR_NUMERIC_STATE = "numeric_state"
ATTR_SUPPORT_PULLSPING = "support_pullspring"
ATTR_DURATION_PULLSPRING = "duration_pullspring"
ATTR_CONNECTED = "connected"

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, entry, async_add_entities):
    
    coordinator = hass[DOMAIN][entry.entry_id]
    async_add_entities(
        [TedeeLock(lock, coordinator) for lock in coordinator.data.values()]
    )

class TedeeLock(CoordinatorEntity, LockEntity):

    def __init__(self, lock, coordinator):
        super().__init__(coordinator)
        _LOGGER.debug("LockEntity: %s", lock.name)
        
        self._lock = lock
        self._id = self._lock.id

        self._attr_has_entity_name = True
        self._attr_name = "Lock"
        self._attr_unique_id = f"{lock.id}-lock"
        
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, self._lock.id)},
            name=self._lock.name,
            manufacturer="Tedee",
            model=self._lock.type
        )

    @property
    def supported_features(self):
        return SUPPORT_OPEN

    @property
    def is_locked(self) -> bool:
        return self._state == 6

    @property
    def is_unlocking(self) -> bool:
        return self._state == 4

    @property
    def is_locking(self) -> bool:
        return self._state == 5
    
    @property
    def is_jammed(self) -> bool:
        return self._state == 3

    @property
    def extra_state_attributes(self):
        return {
            ATTR_ID: self._id,
            ATTR_BATTERY_LEVEL: self._lock.battery_level,
            ATTR_BATTERY_CHARGING: self._lock.is_charging,
            ATTR_NUMERIC_STATE: self._lock.state,
            ATTR_CONNECTED: self._lock.is_connected,
            ATTR_SUPPORT_PULLSPING: self._lock.is_enabled_pullspring,
            ATTR_DURATION_PULLSPRING: self._lock.duration_pullspring,
        }
    
    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self._lock = self.coordinator.data[self._id]
        self.async_write_ha_state()

        
    async def async_unlock(self, **kwargs):
        try:
            await self.coordinator._tedee_client.unlock(self._id)
        except TedeeClientException:
            _LOGGER.debug("Failed to unlock the door.")

    async def async_lock(self, **kwargs):
        try:
            await self.coordinator._tedee_client.lock(self._id)
        except TedeeClientException:
            _LOGGER.debug("Failed to lock the door.")

    async def async_open(self, **kwargs):
        try:
            await self.coordinator._tedee_client.open(self._id)
        except TedeeClientException:
            _LOGGER.debug("Failed to unlatch the door.")        
