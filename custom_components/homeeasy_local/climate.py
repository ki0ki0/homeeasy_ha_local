"""Climate platform for Home Easy HVAC Local."""
from typing import List

from homeeasy.DeviceState import Mode, FanMode, HorizontalFlowMode, VerticalFlowMode
from homeeasy.HomeEasyLib import HomeEasyLib, DeviceState

from homeassistant.components.climate import ClimateEntity
from homeassistant.components.climate.const import (
    HVACMode,
    ClimateEntityFeature,
)
from homeassistant.const import ATTR_TEMPERATURE, UnitOfTemperature 

from .const import DOMAIN, ICON, CLIMATE
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
    HVACMode.OFF,
    HVACMode.AUTO,
    HVACMode.COOL,
    HVACMode.DRY,
    HVACMode.FAN_ONLY,
    HVACMode.HEAT,
]

HA_STATE_TO_MODE_MAP = {
    HVACMode.AUTO: Mode.Auto,
    HVACMode.COOL: Mode.Cool,
    HVACMode.DRY: Mode.Dry,
    HVACMode.FAN_ONLY: Mode.Fan,
    HVACMode.HEAT: Mode.Heat,
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
        return ClimateEntityFeature.TARGET_TEMPERATURE | ClimateEntityFeature.FAN_MODE | ClimateEntityFeature.SWING_MODE

    @property
    def name(self) -> str:
        """Return the name of the thermostat, if any."""
        return f"{super().name}_{CLIMATE}"

    @property
    def temperature_unit(self) -> str:
        """Return the unit of measurement."""
        if (
            self.coordinator.state == None
            or not self.coordinator.state.temperatureScale
        ):
            return UnitOfTemperature.CELSIUS 
        return UnitOfTemperature.FAHRENHEIT 

    @property
    def current_temperature(self) -> float:
        """Return the current temperature."""
        return self.coordinator.state.indoorTemperature

    @property
    def target_temperature(self) -> float:
        """Return the temperature we try to reach."""
        return self.coordinator.state.desiredTemperature

    async def async_set_temperature(self, **kwargs) -> None:
        """Set new target temperature."""
        temperature = kwargs.get(ATTR_TEMPERATURE)
        if temperature is None:
            return
        state = self.coordinator.state
        state.desiredTemperature = temperature
        await self.coordinator.send(state)

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
        if not self.coordinator.state.power:
            return HVACMode.OFF

        mode = self.coordinator.state.mode
        return MODE_TO_HA_STATE_MAP[mode]

    async def async_set_hvac_mode(self, hvac_mode: str) -> None:
        """Set new target operation mode."""
        state = self.coordinator.state
        if hvac_mode == HVACMode.OFF:
            state.power = False
        else:
            state.power = True
            state.mode = HA_STATE_TO_MODE_MAP[hvac_mode]
        await self.coordinator.send(state)

    @property
    def hvac_modes(self):
        """Return the list of available operation modes."""
        return SUPPORT_HVAC

    @property
    def fan_mode(self) -> str:
        """Return the fan setting."""
        mode = int(self.coordinator.state.fanMode)
        return SUPPORT_FAN[mode]

    async def async_set_fan_mode(self, fan_mode: str) -> None:
        """Set fan mode."""
        index = SUPPORT_FAN.index(fan_mode)
        state = self.coordinator.state
        state.fanMode = FanMode(index)
        await self.coordinator.send(state)

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
                h == self.coordinator.state.flowHorizontalMode
                and v == self.coordinator.state.flowVerticalMode
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
        state = self.coordinator.state
        state.flowHorizontalMode = h
        state.flowVerticalMode = v
        await self.coordinator.send(state)
