from homeassistant.components.sensor import SensorEntity, SensorDeviceClass, SensorStateClass
from homeassistant.helpers.entity import DeviceInfo
from .const import DOMAIN, CLIENT

async def async_setup_entry(hass, entry, async_add_entities):
    tedee_client = hass.data[DOMAIN][CLIENT]
    async_add_entities(
        [TedeeBatterySensor(tedee_client, lock) for lock in tedee_client.locks], True
    )

class TedeeBatterySensor(SensorEntity):

    def __init__(self, tedee_client, lock):
        self._tedee_client = tedee_client
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
            manufacturer="Tedee",
            model=self._lock.type
        )

    async def async_update(self):
        self._lock = self._tedee_client.find_lock(self._lock.id)

    @property
    def native_value(self):
        return self._tedee_client.find_lock(self._lock.id).battery_level