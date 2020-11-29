"""Platform for lock integration."""
import logging
from datetime import timedelta
from pytedee import TedeeClient
from pytedee import TedeeClientException
from pytedee import Lock
import voluptuous as vol

import pkg_resources
from pkg_resources import parse_version

import homeassistant.helpers.config_validation as cv
from homeassistant.core import callback
from homeassistant.helpers.event import async_call_later
# Import the device class from the component that you want to support
from homeassistant.components.lock import PLATFORM_SCHEMA, SUPPORT_OPEN, LockEntity
from homeassistant.const import ATTR_BATTERY_LEVEL, ATTR_ID, CONF_PASSWORD, CONF_USERNAME, STATE_LOCKED, STATE_UNLOCKED

ATTR_NUMERIC_STATE = "numeric_state"
ATTR_SUPPORT_PULLSPING = "support_pullspring"
ATTR_DURATION_PULLSPRING = "duration_pullspring"
ATTR_CONNECTED = "connected"
ATTR_CHARGING = "charging"

_LOGGER = logging.getLogger(__name__)

# Validation of the user's configuration
PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_USERNAME, default='admin'): cv.string,
    vol.Required(CONF_PASSWORD): cv.string,
})


def setup_platform(hass, config, add_entities, discovery_info=None):
    """Set up the Tedee Lock platform."""
    try:
        #_LOGGER.error("Creds: %s, %s", config[CONF_USERNAME], config[CONF_PASSWORD])
        tedee = TedeeClient(config[CONF_USERNAME], config[CONF_PASSWORD])
    except TedeeClientException as exc:
        _LOGGER.error(exc)
        return
    available_locks = tedee.get_locks()
    _LOGGER.debug("available_locks: %s", available_locks)
    if not available_locks:
        # No locks found; abort setup routine.
        _LOGGER.info("No locks found in your account")
        return
    add_entities([TedeeLock(lock, tedee) for lock in available_locks], True)


class TedeeLock(LockEntity):
    """Representation of a Tedee lock."""

    def __init__(self, tedee_lock, client):
        _LOGGER.debug("LockEntity: %s", tedee_lock.get_name())
        """Initialize the lock."""
        self._sensor = tedee_lock
        self._lock_id = tedee_lock.get_id()
        self._client = client
        self._state = STATE_LOCKED
        self._battery_level = tedee_lock.get_battery_level()
        self._available = True
        self._device_attrs = {
            ATTR_ID: self._lock_id,
            ATTR_BATTERY_LEVEL: self._battery_level
        }
        if parse_version('0.0.2') <= parse_version(pkg_resources.get_distribution('pytedee').version):
            self._device_attrs[ATTR_SUPPORT_PULLSPING] = self._sensor.get_is_enabled_pullspring()
            self._device_attrs[ATTR_DURATION_PULLSPRING] = self._sensor.get_duration_pullspring()

    @property
    def supported_features(self):
        """Flag supported features."""
        if parse_version('0.0.2') <= parse_version(pkg_resources.get_distribution('pytedee').version):
            if self._sensor.get_is_enabled_pullspring():
                return SUPPORT_OPEN
            else:
                return None
        else:
            return SUPPORT_OPEN

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return self._available

    def update(self):
        self._available = self._client.update(self._lock_id)
        #self._battery_level = self._sensor.get_battery_level()
        self._state = self.decode_state(self._sensor.get_state())

    @property
    def name(self):
        """Return the name of the lock."""
        name = self._sensor.get_name()
        return name

    @property
    def is_locked(self):
        """Return true if lock is locked."""
        return self.decode_state(self._sensor.get_state())

    @property
    def device_state_attributes(self):
        """Return the device specific state attributes."""
        self._device_attrs[ATTR_BATTERY_LEVEL] = self._battery_level
        self._device_attrs[ATTR_NUMERIC_STATE] = self._sensor.get_state()
        if parse_version('0.0.2') <= parse_version(pkg_resources.get_distribution('pytedee').version):
            self._device_attrs[ATTR_CONNECTED] = self._sensor.is_connected()
            self._device_attrs[ATTR_CHARGING] = self._sensor.get_is_charging()
        return self._device_attrs

    def unlock(self, **kwargs):
        """Unlock the door."""
        try:
            self._client.unlock(self._lock_id)
        except TedeeClientException:
            _LOGGER.debug("Failed to unlock the door.")
        else:
            #self._state = self.decode_state(self._sensor.get_state())
            #self.async_write_ha_state()
            async_call_later(self.hass, 3, self.force_update)

    def lock(self, **kwargs):
        """Lock the door."""
        try:
            self._client.lock(self._lock_id)
        except TedeeClientException:
            _LOGGER.debug("Failed to lock the door.")
        else:
            #self._state = self.decode_state(self._sensor.get_state())
            #self.async_write_ha_state()
            async_call_later(self.hass, 3, self.force_update)

    def open(self, **kwargs):
        """Unlatch the door."""
        try:
            self._client.open(self._lock_id)
        except TedeeClientException:
            _LOGGER.debug("Failed to unlatch the door.")
        else:
            #self._state = self.decode_state(self._sensor.get_state())
            #self.async_write_ha_state()
            async_call_later(self.hass, 5, self.force_update)

    @callback
    def force_update(self, _):
        self._state = self.decode_state(self._sensor.get_state())
        self.async_write_ha_state()

    def decode_state(self, state):
        #_LOGGER.error("decode_state: %d", state)
        if state == 5:
            return True
        elif state == 6:
            return True
        else:
            return False

