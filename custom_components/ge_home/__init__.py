"""The ge_home integration."""

import logging
from homeassistant.const import EVENT_HOMEASSISTANT_STOP
import voluptuous as vol

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.const import CONF_REGION
from .const import DOMAIN
from .update_coordinator import GeHomeUpdateCoordinator

_LOGGER = logging.getLogger(__name__)
CONFIG_SCHEMA = vol.Schema({DOMAIN: vol.Schema({})}, extra=vol.ALLOW_EXTRA)


async def async_setup(hass: HomeAssistant, config: dict):
    return True

async def async_migrate_entry(hass: HomeAssistant, config_entry: ConfigEntry):
    """Migrate old entry."""
    _LOGGER.debug("Migrating from version %s", config_entry.version)

    if config_entry.version == 1:

        new = {**config_entry.data}
        new[CONF_REGION] = "US"

        config_entry.version = 2
        hass.config_entries.async_update_entry(config_entry, data=new)

    _LOGGER.info("Migration to version %s successful", config_entry.version)

    return True    


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Set up the ge_home component."""
    hass.data.setdefault(DOMAIN, {})

    """Set up ge_home from a config entry."""
    coordinator = GeHomeUpdateCoordinator(hass, entry)
    hass.data[DOMAIN][entry.entry_id] = coordinator

    if not await coordinator.async_setup():
        return False

    hass.bus.async_listen_once(EVENT_HOMEASSISTANT_STOP, coordinator.shutdown)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Unload a config entry."""
    coordinator: GeHomeUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    ok = await coordinator.async_reset()
    if ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return ok


async def async_update_options(hass, config_entry):
    """Update options."""
    await hass.config_entries.async_reload(config_entry.entry_id)
