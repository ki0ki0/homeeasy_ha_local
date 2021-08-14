"""BlueprintEntity class"""
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import CLIMATE, CONF_IP, DOMAIN, ICON, NAME, VERSION, ATTRIBUTION


class Entity(CoordinatorEntity):
    def __init__(self, coordinator, config_entry):
        super().__init__(coordinator)
        self.config_entry = config_entry

    @property
    def should_poll(self) -> bool:
        """No need to poll. Coordinator notifies entity of updates."""
        return False

    @property
    def unique_id(self):
        """Return a unique ID to use for this entity."""
        return self.config_entry.entry_id

    @property
    def name(self) -> str:
        """Return the name of the thermostat, if any."""
        return f"{DOMAIN}({self.config_entry.data.get(CONF_IP)})"

    @property
    def icon(self):
        """Return the icon of this switch."""
        return ICON

    # @property
    # def device_info(self):
    #     return {
    #         "identifiers": {(DOMAIN, self.unique_id)},
    #         "name": NAME,
    #         "model": VERSION,
    #         "manufacturer": NAME,
    #     }

    # @property
    # def device_state_attributes(self):
    #     """Return the state attributes."""
    #     return {
    #         "id": str(self.config_entry.entry_id),
    #         "integration": DOMAIN,
    #     }
