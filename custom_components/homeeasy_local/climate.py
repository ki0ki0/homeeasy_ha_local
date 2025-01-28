"""Climate platform for Home Easy HVAC Local."""

from __future__ import annotations

from typing import Any, Final, TypeVar

from homeassistant.components.climate import (
    FAN_AUTO,
    FAN_HIGH,
    FAN_LOW,
    FAN_MEDIUM,
    SWING_BOTH,
    SWING_HORIZONTAL,
    SWING_OFF,
    SWING_VERTICAL,
    ClimateEntity,
    ClimateEntityFeature,
    HVACAction,
    HVACMode,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import ATTR_TEMPERATURE, Platform, UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeeasy.DeviceState import FanMode, HorizontalFlowMode, Mode, VerticalFlowMode
from homeeasy.HomeEasyLib import DeviceState, HomeEasyLib

from .const import CLIMATE, DOMAIN, ICON
from .coordinator import UpdateCoordinator
from .entity import Entity

CoordinatorT = TypeVar("CoordinatorT", bound="UpdateCoordinator")

SUPPORT_FAN: Final = [
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

SUPPORT_HVAC: Final = [
    HVACMode.OFF,
    HVACMode.AUTO,
    HVACMode.COOL,
    HVACMode.DRY,
    HVACMode.FAN_ONLY,
    HVACMode.HEAT,
]

HA_STATE_TO_MODE_MAP: Final = {
    HVACMode.AUTO: Mode.Auto,
    HVACMode.COOL: Mode.Cool,
    HVACMode.DRY: Mode.Dry,
    HVACMode.FAN_ONLY: Mode.Fan,
    HVACMode.HEAT: Mode.Heat,
}

MODE_TO_HA_STATE_MAP: Final = {
    value: key for key, value in HA_STATE_TO_MODE_MAP.items()
}

SWING_MODES: Final = {
    SWING_OFF: (HorizontalFlowMode.Stop, VerticalFlowMode.Stop),
    SWING_HORIZONTAL: (HorizontalFlowMode.Swing, VerticalFlowMode.Stop),
    SWING_VERTICAL: (HorizontalFlowMode.Stop, VerticalFlowMode.Swing),
    SWING_BOTH: (HorizontalFlowMode.Swing, VerticalFlowMode.Swing),
}


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up climate platform."""
    coordinator: UpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([HomeEasyHvacLocal(coordinator, entry)])


class HomeEasyHvacLocal(Entity, ClimateEntity):
    """Home Easy Local climate class."""

    _attr_has_entity_name = True
    _enable_turn_on_off_backwards_compatibility = False
    _attr_target_temperature_step = 1
    _attr_min_temp = 16
    _attr_max_temp = 31

    def __init__(self, coordinator: CoordinatorT, config_entry: ConfigEntry) -> None:
        """Initialize the climate device."""
        super().__init__(coordinator, config_entry)
        self._attr_supported_features = (
            ClimateEntityFeature.TARGET_TEMPERATURE
            | ClimateEntityFeature.FAN_MODE
            | ClimateEntityFeature.SWING_MODE
            | ClimateEntityFeature.TURN_ON
            | ClimateEntityFeature.TURN_OFF
        )
        self._attr_hvac_modes = SUPPORT_HVAC
        self._attr_fan_modes = list(SUPPORT_FAN)
        self._attr_swing_modes = list(SWING_MODES.keys())
        self._attr_temperature_unit = UnitOfTemperature.CELSIUS

    @property
    def _state(self) -> DeviceState | None:
        """Return coordinator state with proper typing."""
        return self.coordinator.state

    @property
    def should_poll(self) -> bool:
        """Return True if entity has to be polled for state."""
        return True

    @property
    def name(self) -> str:
        """Return the name of the thermostat."""
        return f"{super().name}_{CLIMATE}"

    @property
    def temperature_unit(self) -> str:
        """Return the unit of measurement."""
        state = self._state
        if state is None or not state.temperatureScale:
            return UnitOfTemperature.CELSIUS
        return UnitOfTemperature.FAHRENHEIT

    @property
    def hvac_action(self) -> HVACAction | None:
        """Return the current HVAC action."""
        state = self._state
        if state is None or not state.power:
            return HVACAction.OFF

        mode = state.mode
        current_temp = self.current_temperature
        target_temp = self.target_temperature

        if current_temp is None or target_temp is None:
            return HVACAction.IDLE

        if mode == Mode.Heat and current_temp < target_temp:
            return HVACAction.HEATING
        if mode == Mode.Cool and current_temp > target_temp:
            return HVACAction.COOLING
        if mode == Mode.Dry:
            return HVACAction.DRYING
        if mode == Mode.Fan:
            return HVACAction.FAN

        return HVACAction.IDLE

    @property
    def current_temperature(self) -> float | None:
        """Return the current temperature."""
        state = self._state
        if state is None:
            return None
        return state.indoorTemperature

    @property
    def target_temperature(self) -> float | None:
        """Return the temperature we try to reach."""
        state = self._state
        if state is None:
            return None
        return state.desiredTemperature

    async def async_set_temperature(self, **kwargs: Any) -> None:
        """Set new target temperature."""
        state = self._state
        if state is None:
            return

        temperature = kwargs.get(ATTR_TEMPERATURE)
        if temperature is None:
            return

        state.desiredTemperature = temperature
        await self.coordinator.send(state)

    @property
    def hvac_mode(self) -> HVACMode:
        """Return current operation ie. heat, cool, idle."""
        state = self._state
        if state is None or not state.power:
            return HVACMode.OFF

        return MODE_TO_HA_STATE_MAP[state.mode]

    async def async_set_hvac_mode(self, hvac_mode: HVACMode) -> None:
        """Set new target operation mode."""
        state = self._state
        if state is None:
            return

        if hvac_mode == HVACMode.OFF:
            state.power = False
        else:
            state.power = True
            state.mode = HA_STATE_TO_MODE_MAP[hvac_mode]

        await self.coordinator.send(state)

    async def async_turn_on(self) -> None:
        """Turn the entity on."""
        state = self._state
        if state is None:
            return

        state.power = True
        await self.coordinator.send(state)

    async def async_turn_off(self) -> None:
        """Turn the entity off."""
        state = self._state
        if state is None:
            return

        state.power = False
        await self.coordinator.send(state)

    @property
    def fan_mode(self) -> str | None:
        """Return the fan setting."""
        state = self._state
        if state is None:
            return None

        mode = int(state.fanMode)
        return SUPPORT_FAN[mode]

    async def async_set_fan_mode(self, fan_mode: str) -> None:
        """Set fan mode."""
        state = self._state
        if state is None:
            return

        index = SUPPORT_FAN.index(fan_mode)
        state.fanMode = FanMode(index)
        await self.coordinator.send(state)

    @property
    def swing_mode(self) -> str:
        """Return the swing setting."""
        state = self._state
        if state is None:
            return SWING_OFF

        current_h = state.flowHorizontalMode
        current_v = state.flowVerticalMode

        for mode, (h, v) in SWING_MODES.items():
            if h == current_h and v == current_v:
                return mode
        return SWING_OFF

    async def async_set_swing_mode(self, swing_mode: str) -> None:
        """Set new target swing operation."""
        state = self._state
        if state is None or swing_mode not in SWING_MODES:
            return

        h, v = SWING_MODES[swing_mode]
        state.flowHorizontalMode = h
        state.flowVerticalMode = v
        await self.coordinator.send(state)
