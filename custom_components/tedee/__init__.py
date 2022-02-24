from .const import (
    DOMAIN,
)

COMPONENT_TYPES = ["lock"]

async def async_setup(hass, config):
    return True

async def async_setup_entry(hass, entry):
    for component in COMPONENT_TYPES:
        hass.async_create_task(
            hass.config_entries.async_forward_entry_setup(entry, component)
        )

    return True