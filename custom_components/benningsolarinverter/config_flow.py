"""Config flow for the HASS Benning Solar Inverter Integration integration."""

from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.const import CONF_HOST, CONF_PASSWORD, CONF_USERNAME
from homeassistant.core import HomeAssistant
from homeassistant.helpers.storage import Store

from .exceptions.cannot_connect import CannotConnect
from .exceptions.invalid_auth import InvalidAuth

from .benning_client import BenningClient

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_HOST): str,
        vol.Required(CONF_USERNAME): str,
        vol.Required(CONF_PASSWORD): str,
    }
)


async def validate_input(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, Any]:
    """
    Validate the user input allows us to connect.
    This will also load all available entries and store them (which causes this function to take a couple of minutes).
    """

    _LOGGER.info("Setting up benning integration...")

    client = BenningClient(hass, data[CONF_HOST], data[CONF_USERNAME], data[CONF_PASSWORD])

    await client.authenticate()

  
    # Load all available entities and store the entities
    # NOTE: this may take a couple of minutes.
    available_entries = await client.get_available_entries()

    _LOGGER.info("Saving all available entries to store...")

    store = Store(hass, 1, "benning_config")
    await store.async_save({
        "available_entries": available_entries,
        "host": data[CONF_HOST],
        "username": data[CONF_USERNAME],
        "password": data[CONF_PASSWORD]
    })

    _LOGGER.info("Saved all available entries to store!")


    # If you cannot connect:
    # throw CannotConnect
    # If the authentication is wrong:
    # InvalidAuth

    _LOGGER.info("Successfully set up integration!")

    # Return info that you want to store in the config entry.
    return {"title": "Benning Inverter"}


class ConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for HASS Benning Solar Inverter Integration."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}
        if user_input is not None:
            try:
                info = await validate_input(self.hass, user_input)
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except InvalidAuth:
                errors["base"] = "invalid_auth"
            except Exception:
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"
            else:
                return self.async_create_entry(title=info["title"], data=user_input)

        return self.async_show_form(
            step_id="user", data_schema=STEP_USER_DATA_SCHEMA, errors=errors
        )




