from homeassistant.components.sensor import (SensorDeviceClass, SensorEntity,
                                             SensorStateClass)
from homeassistant.core import callback
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN


async def async_setup_entry(hass, entry, async_add_entities):
    
    coordinator = hass.data[DOMAIN][entry.entry_id]

    async_add_entities(
        [TedeeBatterySensor(lock, coordinator) for lock in coordinator.data.values()]
    )

class TedeeBatterySensor(CoordinatorEntity, SensorEntity):

    def __init__(self, lock, coordinator):
        super().__init__(coordinator)
        self._lock = lock
        self._attr_device_class = SensorDeviceClass.BATTERY
        self._attr_native_unit_of_measurement = '%'
        self._attr_state_class = SensorStateClass.MEASUREMENT
        self._attr_has_entity_name = True
        self._attr_name = "Battery"
        self._attr_unique_id = f"{lock.id}-battery-sensor"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, self._lock.id)},
            name=self._lock.name,
            manufacturer="tedee",
            model=self._lock.type
        )

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self._lock = self.coordinator.data[self._lock.id]
        self.async_write_ha_state()

    @property
    def native_value(self):
        return self._lock.battery_level