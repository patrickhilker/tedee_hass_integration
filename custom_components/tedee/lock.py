import logging

from homeassistant.components.lock import SUPPORT_OPEN, LockEntity
from homeassistant.const import (ATTR_BATTERY_CHARGING, ATTR_BATTERY_LEVEL,
                                 ATTR_ID)
from homeassistant.core import callback
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from pytedee_async import TedeeClientException

from .const import DOMAIN, UNLOCK_PULLS_LATCH

ATTR_NUMERIC_STATE = "numeric_state"
ATTR_SUPPORT_PULLSPING = "support_pullspring"
ATTR_DURATION_PULLSPRING = "duration_pullspring"
ATTR_CONNECTED = "connected"
ATTR_SEMI_LOCKED = "semi_locked"

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, entry, async_add_entities):
    
    coordinator = hass.data[DOMAIN][entry.entry_id]

    entities = []
    for lock in coordinator.data.values():
        if lock.is_enabled_pullspring:
            entities.append(TedeeLockWithLatch(lock, coordinator, entry))
        else:
            entities.append(TedeeLock(lock, coordinator, entry))

    async_add_entities(entities)

class TedeeLock(CoordinatorEntity, LockEntity):
    """A tedee lock that doesn't have pullspring enabled"""

    def __init__(self, lock, coordinator, entry):
        _LOGGER.debug("Setting up LockEntity for %s", lock.name)
        super().__init__(coordinator)
        
        self._lock = lock
        self._id = self._lock.id

        self._attr_has_entity_name = True
        self._attr_name = "Lock"
        self._attr_unique_id = f"{lock.id}-lock"
        
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, self._lock.id)},
            name=self._lock.name,
            manufacturer="tedee",
            model=self._lock.type
        )

    @property
    def is_locked(self) -> bool:
        return self._lock.state == 6

    @property
    def is_unlocking(self) -> bool:
        return self._lock.state == 4
    
    @property
    def is_locking(self) -> bool:
        return self._lock.state == 5
    
    @property
    def is_jammed(self) -> bool:
        return self._lock.is_state_jammed

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
            ATTR_SEMI_LOCKED: self._lock.state == 3
        }

    @property
    def available(self) -> bool:
        return self._lock.is_connected
    
    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self._lock = self.coordinator.data[self._lock.id]
        self.async_write_ha_state()

        
    async def async_unlock(self, **kwargs):
        try:
            self._lock.state = 4
            self.async_write_ha_state()

            await self.coordinator._tedee_client.unlock(self._id)
            await self.coordinator.async_request_refresh()
        except (TedeeClientException, Exception) as ex:
            _LOGGER.debug("Failed to unlock the door. Lock %s", self._id)
            raise HomeAssistantError(ex) from ex

    async def async_lock(self, **kwargs):
        try:
            self._lock.state = 5
            self.async_write_ha_state()

            await self.coordinator._tedee_client.lock(self._id)
            await self.coordinator.async_request_refresh()
        except (TedeeClientException, Exception) as ex:
            _LOGGER.debug("Failed to lock the door. Lock %s", self._id)
            raise HomeAssistantError(ex) from ex



class TedeeLockWithLatch(TedeeLock):
    """A tedee lock but has pullspring enabled, so it additional features"""

    def __init__(self, lock, coordinator, entry):
        super().__init__(lock, coordinator, entry)
        self._unlock_pulls_latch = entry.data.get(UNLOCK_PULLS_LATCH, False)
        _LOGGER.debug("Unlock pulls latch: %s", str(self._unlock_pulls_latch))

    @property
    def supported_features(self):
        return SUPPORT_OPEN


    async def async_unlock(self, **kwargs):
        try:
            self._lock.state = 4
            self.async_write_ha_state()

            if self._unlock_pulls_latch:
                await self.coordinator._tedee_client.open(self._id)
            else:
                await self.coordinator._tedee_client.unlock(self._id)
            await self.coordinator.async_request_refresh()
        except (TedeeClientException, Exception) as ex:
            _LOGGER.debug("Failed to unlock the door. Lock %s", self._id)
            raise HomeAssistantError(ex) from ex


    async def async_open(self, **kwargs):
        try:
            self._lock.state = 4
            self.async_write_ha_state()

            await self.coordinator._tedee_client.open(self._id)
            await self.coordinator.async_request_refresh()
        except (TedeeClientException, Exception) as ex:
            _LOGGER.debug("Failed to unlatch the door. Lock %s", self._id)     
            raise HomeAssistantError(ex) from ex   