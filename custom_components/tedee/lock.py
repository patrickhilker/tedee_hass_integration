import logging
from pytedee import TedeeClient, TedeeClientException, Lock

from homeassistant.core import callback
from homeassistant.helpers.event import async_call_later
from homeassistant.components.lock import SUPPORT_OPEN, LockEntity
from homeassistant.const import ATTR_BATTERY_LEVEL, ATTR_ID, CONF_ACCESS_TOKEN, ATTR_BATTERY_CHARGING, STATE_UNKNOWN

from .const import (
    DOMAIN,
    NAME,
    SCAN_INTERVAL
)

ATTR_NUMERIC_STATE = "numeric_state"
ATTR_SUPPORT_PULLSPING = "support_pullspring"
ATTR_DURATION_PULLSPRING = "duration_pullspring"
ATTR_CONNECTED = "connected"

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, config, async_add_entities):
    pak = config.data.get(CONF_ACCESS_TOKEN)

    try:
        client = await hass.async_add_executor_job(lambda : TedeeClient(pak))
    except TedeeClientException as exc:
        _LOGGER.error(exc)
        return

    locks = client.get_locks()
    _LOGGER.debug("available_locks: %s", locks)

    if not locks:
        # No locks found; abort setup routine.
        _LOGGER.info("No locks found in your account")
        return

    async_add_entities([TedeeLock(lock, client) for lock in locks], True)

class TedeeLock(LockEntity):

    def __init__(self, lock, client):
        _LOGGER.debug("LockEntity: %s", lock.get_name())
        
        self._lock = lock
        self._client = client
        self._id = ""
        self._name = STATE_UNKNOWN
        self._state = STATE_UNKNOWN
        self._extra_state_attributes[ATTR_ID] = STATE_UNKNOWN
        self._extra_state_attributes[ATTR_BATTERY_LEVEL] = STATE_UNKNOWN
        self._extra_state_attributes[ATTR_BATTERY_CHARGING] = STATE_UNKNOWN
        self._extra_state_attributes[ATTR_NUMERIC_STATE] = STATE_UNKNOWN
        self._extra_state_attributes[ATTR_CONNECTED] = STATE_UNKNOWN
        self._extra_state_attributes[ATTR_SUPPORT_PULLSPING] = STATE_UNKNOWN
        self._extra_state_attributes[ATTR_DURATION_PULLSPRING] = STATE_UNKNOWN

    async def async_update(self):
        self._id = await self._lock.get_id()
        self._name = await self._lock.get_name()
        self._state = await self._lock.get_state()

        self._extra_state_attributes[ATTR_BATTERY_LEVEL] = await self._lock.get_battery_level()
        self._extra_state_attributes[ATTR_BATTERY_CHARGING] = await self._lock.get_is_charging()
        self._extra_state_attributes[ATTR_NUMERIC_STATE] = await self._lock.get_state()
        self._extra_state_attributes[ATTR_CONNECTED] = await self._lock.is_connected()
        self._extra_state_attributes[ATTR_SUPPORT_PULLSPING] = await self._lock.get_is_enabled_pullspring()
        self._extra_state_attributes[ATTR_DURATION_PULLSPRING] = await self._lock.get_duration_pullspring()

    @property
    def supported_features(self):
        return SUPPORT_OPEN

    @property
    def available(self) -> bool:
        return self._available

    @property
    def name(self) -> str:
        return self._name

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
    def extra_state_attributes(self):
        return {
            ATTR_ID: self._id,

            ATTR_BATTERY_LEVEL: self._extra_state_attributes[ATTR_BATTERY_LEVEL] ,
            ATTR_BATTERY_CHARGING: self._extra_state_attributes[ATTR_BATTERY_CHARGING],

            ATTR_NUMERIC_STATE: self._extra_state_attributes[ATTR_NUMERIC_STATE],

            ATTR_CONNECTED: self._extra_state_attributes[ATTR_CONNECTED],

            ATTR_SUPPORT_PULLSPING: self._extra_state_attributes[ATTR_SUPPORT_PULLSPING],
            ATTR_DURATION_PULLSPRING: self._extra_state_attributes[ATTR_DURATION_PULLSPRING],
        }

    @property
    def device_info(self):
        return {
            "identifiers": {
                (DOMAIN, self.unique_id)
            },
            "name": self._name,
            "manufacturer": "tedee"
        }

    @property
    def unique_id(self) -> str:
        return self._lock.get_id()

    def unlock(self, **kwargs):
        try:
            self._client.unlock(self._id)
        except TedeeClientException:
            _LOGGER.debug("Failed to unlock the door.")

    def lock(self, **kwargs):
        try:
            self._client.lock(self._id)
        except TedeeClientException:
            _LOGGER.debug("Failed to lock the door.")

    def open(self, **kwargs):
        try:
            self._client.open(self._id)
        except TedeeClientException:
            _LOGGER.debug("Failed to unlatch the door.")

    def update(self):
        self._available = self._client.update(self._id)
