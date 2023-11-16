"""Tedee sensor entities."""
from collections.abc import Callable
from dataclasses import dataclass

from pytedee_async import TedeeLock

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .entity import TedeeEntity, TedeeEntityDescription


@dataclass
class TedeeBinarySensorEntityDescriptionMixin:
    """Mixin functions for Tedee sensor entity description."""

    is_on_fn: Callable[[TedeeLock], bool | None]


@dataclass
class TedeeBinarySensorEntityDescription(
    BinarySensorEntityDescription,
    TedeeEntityDescription,
    TedeeBinarySensorEntityDescriptionMixin,
):
    """Describes Tedee sensor entity."""


ENTITIES: tuple[TedeeBinarySensorEntityDescription, ...] = (
    TedeeBinarySensorEntityDescription(
        key="battery_charging_sensor",
        translation_key="battery_charging_sensor",
        unique_id_fn=lambda lock: f"{lock.lock_id}-battery-charging-sensor",
        device_class=BinarySensorDeviceClass.BATTERY_CHARGING,
        is_on_fn=lambda lock: lock.is_charging,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Tedee sensor entity."""
    coordinator = hass.data[DOMAIN][entry.entry_id]

    for entity_description in ENTITIES:
        async_add_entities(
            [
                TedeeBinarySensorEntity(lock, coordinator, entity_description)
                for lock in coordinator.data.values()
                if lock.lock_type == "Tedee PRO"
            ]
        )


class TedeeBinarySensorEntity(TedeeEntity, BinarySensorEntity):
    """Tedee sensor entity."""

    entity_description: TedeeBinarySensorEntityDescription

    @property
    def is_on(self) -> bool | None:
        """Return true if the binary sensor is on."""
        return self.entity_description.is_on_fn(self._lock)
