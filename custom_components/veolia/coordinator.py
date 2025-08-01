"""DataUpdateCoordinator for integration_blueprint."""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import TYPE_CHECKING

from veolia_api import VeoliaAPI
from veolia_api.exceptions import VeoliaAPIError
from veolia_api.model import VeoliaAccountData
from veolia_api.veolia_api import ConsumptionType

from homeassistant.const import CONF_PASSWORD, CONF_USERNAME
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import DOMAIN, LOGGER
from .data import VeoliaConfigEntry

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant


class VeoliaDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching data from the API."""

    config_entry: VeoliaConfigEntry

    def __init__(
        self,
        hass: HomeAssistant,
        config_entry: VeoliaConfigEntry,
    ) -> None:
        """Initialize."""
        super().__init__(
            hass=hass,
            logger=LOGGER,
            name=DOMAIN,
            update_interval=timedelta(hours=12),
        )
        self.config_entry = config_entry
        LOGGER.debug("Initializing client VeoliaAPI")
        LOGGER.debug("Username: %s", self.config_entry.data[CONF_USERNAME])
        LOGGER.debug("Config entry data keys: %s", list(self.config_entry.data.keys()))

        try:
            self.client_api = VeoliaAPI(
                username=self.config_entry.data[CONF_USERNAME],
                password=self.config_entry.data[CONF_PASSWORD],
            )
            LOGGER.debug("VeoliaAPI client created successfully")
        except Exception as e:
            LOGGER.error("Failed to create VeoliaAPI client: %s", e)
            raise

    async def test_connection(self) -> bool:
        """Test the connection to Veolia API."""
        try:
            LOGGER.debug("Testing connection to Veolia API...")
            result = await self.client_api.login()
            LOGGER.debug("Login test result: %s", result)
            return result
        except Exception as e:
            LOGGER.error("Connection test failed: %s", e)
            return False

    async def _async_update_data(self) -> VeoliaAccountData:
        """Update data via library."""
        try:
            now = datetime.now()
            LOGGER.debug(
                f"Fetching consumption data for {ConsumptionType.MONTHLY.value} "
                f"Year:{now.year} Month:{now.month}",
            )
            LOGGER.debug("About to call fetch_all_data...")
            await self.client_api.fetch_all_data(now.year, now.month)
            LOGGER.debug("fetch_all_data completed successfully")
            LOGGER.debug("Data fetched successfully = %s", self.client_api.account_data)
        except VeoliaAPIError as exception:
            LOGGER.error("VeoliaAPIError occurred: %s", exception)
            LOGGER.error("Exception type: %s", type(exception).__name__)
            raise ConfigEntryAuthFailed(exception) from exception
        except Exception as exception:
            LOGGER.error("Unexpected error during data fetch: %s", exception)
            LOGGER.error("Exception type: %s", type(exception).__name__)
            raise
        else:
            LOGGER.debug("Returning account data: %s", self.client_api.account_data)
            return self.client_api.account_data
