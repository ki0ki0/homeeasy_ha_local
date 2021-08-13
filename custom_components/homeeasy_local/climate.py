"""Climate platform for Home Easy HVAC Local."""
from custom_components.homeeasy_local.api import ApiClient
from typing import List

from homeeasy.DeviceState import Mode, FanMode, HorizontalFlowMode, VerticalFlowMode
from homeeasy.HomeEasyLib import HomeEasyLib, DeviceState

from homeassistant.components.climate import ClimateEntity
from homeassistant.components.climate.const import (
    HVAC_MODE_OFF,
    HVAC_MODE_AUTO,
    HVAC_MODE_COOL,
    HVAC_MODE_DRY,
    HVAC_MODE_FAN_ONLY,
    HVAC_MODE_HEAT,
    SUPPORT_TARGET_TEMPERATURE,
    SUPPORT_FAN_MODE,
    SUPPORT_SWING_MODE,
)
from homeassistant.const import ATTR_TEMPERATURE, TEMP_CELSIUS, TEMP_FAHRENHEIT

from .const import DEFAULT_NAME, DOMAIN, ICON, CLIMATE
from .entity import Entity

SUPPORT_FAN = [
    "Auto",
    "Lowest",
    "Low",
    "Mid-low",
    "Mid-high",
    "High",
    "Highest",
    "Quite",
    "Turbo",
]

SUPPORT_HVAC = [
    HVAC_MODE_OFF,
    HVAC_MODE_AUTO,
    HVAC_MODE_COOL,
    HVAC_MODE_DRY,
    HVAC_MODE_FAN_ONLY,
    HVAC_MODE_HEAT,
]

HA_STATE_TO_MODE_MAP = {
    HVAC_MODE_AUTO: Mode.Auto,
    HVAC_MODE_COOL: Mode.Cool,
    HVAC_MODE_DRY: Mode.Dry,
    HVAC_MODE_FAN_ONLY: Mode.Fan,
    HVAC_MODE_HEAT: Mode.Heat,
}

MODE_TO_HA_STATE_MAP = {value: key for key, value in HA_STATE_TO_MODE_MAP.items()}

SWING_MODES = {
    "Stop": (HorizontalFlowMode.Stop, VerticalFlowMode.Stop),
    "Horizontal": (HorizontalFlowMode.Swing, VerticalFlowMode.Stop),
    "Vertical": (HorizontalFlowMode.Stop, VerticalFlowMode.Swing),
    "Both": (HorizontalFlowMode.Swing, VerticalFlowMode.Swing),
    "Custom": (HorizontalFlowMode.Stop, VerticalFlowMode.Stop),
}


async def async_setup_entry(hass, entry, async_add_devices):
    """Setup climate platform."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_devices([HomeEasyHvacLocal(coordinator, entry)])


class HomeEasyHvacLocal(Entity, ClimateEntity):
    """Home Easy Local climate class."""

    @property
    def should_poll(self) -> bool:
        """Return True if entity has to be polled for state.

        False if entity pushes its state to HA.
        """
        return True

    @property
    def supported_features(self) -> int:
        """Return the list of supported features."""
        return SUPPORT_TARGET_TEMPERATURE | SUPPORT_FAN_MODE | SUPPORT_SWING_MODE

    @property
    def name(self) -> str:
        """Return the name of the thermostat, if any."""
        return f"{DEFAULT_NAME}_{CLIMATE}"

    @property
    def temperature_unit(self) -> str:
        """Return the unit of measurement."""
        return (
            TEMP_CELSIUS
            if not self.coordinator.api.state.temperatureScale
            else TEMP_FAHRENHEIT
        )

    @property
    def current_temperature(self) -> float:
        """Return the current temperature."""
        return self.coordinator.api.state.indoorTemperature

    @property
    def target_temperature(self) -> float:
        """Return the temperature we try to reach."""
        return self.coordinator.api.state.desiredTemperature

    async def async_set_temperature(self, **kwargs) -> None:
        """Set new target temperature."""
        temperature = kwargs.get(ATTR_TEMPERATURE)
        await self.coordinator.api.ensure_connected()
        if temperature is None:
            return
        self.coordinator.api.state.desiredTemperature = temperature
        await self.coordinator.api.send()

    @property
    def target_temperature_step(self) -> float:
        """Return the supported step of target temperature."""
        return 1

    @property
    def min_temp(self) -> float:
        """Return the minimum temperature."""
        return 16

    @property
    def max_temp(self) -> float:
        """Return the maximum temperature."""
        return 31

    @property
    def hvac_mode(self) -> str:
        """Return current operation ie. heat, cool, idle."""
        if not self.coordinator.api.state.power:
            return HVAC_MODE_OFF

        mode = self.coordinator.api.state.mode
        return MODE_TO_HA_STATE_MAP[mode]

    async def async_set_hvac_mode(self, hvac_mode: str) -> None:
        """Set new target operation mode."""
        if hvac_mode == HVAC_MODE_OFF:
            self.coordinator.api.state.power = False
        else:
            self.coordinator.api.state.power = True
            self.coordinator.api.state.mode = HA_STATE_TO_MODE_MAP[hvac_mode]
        await self.coordinator.api.send()

    @property
    def hvac_modes(self):
        """Return the list of available operation modes."""
        return SUPPORT_HVAC

    @property
    def fan_mode(self) -> str:
        """Return the fan setting."""
        mode = int(self.coordinator.api.state.fanMode)
        return SUPPORT_FAN[mode]

    async def async_set_fan_mode(self, fan_mode: str) -> None:
        """Set fan mode."""
        index = SUPPORT_FAN.index(fan_mode)
        self.coordinator.api.state.fanMode = FanMode(index)
        await self.coordinator.api.send()

    @property
    def fan_modes(self) -> List[str]:
        """List of available fan modes."""
        return SUPPORT_FAN

    @property
    def swing_mode(self) -> str:
        """Return the swing setting."""
        for (key, value) in SWING_MODES.items():
            h, v = value
            if (
                h == self.coordinator.api.state.flowHorizontalMode
                and v == self.coordinator.api.state.flowVerticalMode
            ):
                return key
        return list(SWING_MODES.keys())[-1]

    @property
    def swing_modes(self) -> List[str]:
        """Return the list of available swing modes."""
        return list(SWING_MODES.keys())

    async def async_set_swing_mode(self, swing_mode: str) -> None:
        """Set new target swing operation."""
        h, v = SWING_MODES[swing_mode]
        self.coordinator.api.state.flowHorizontalMode = h
        self.coordinator.api.state.flowVerticalMode = v
        await self.coordinator.api.send()

    async def async_update(self) -> None:
        await self.coordinator.api.request_status_async()
