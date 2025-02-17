import logging
from datetime import datetime
from homeassistant.core import HomeAssistant
from homeassistant.components.sensor import SensorEntity
from homeassistant.components.history_stats.sensor import HistoryStatsSensor
from homeassistant.components.history_stats.coordinator import HistoryStatsUpdateCoordinator, HistoryStats
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.entity_registry import async_get as async_get_entity_registry
from homeassistant.util.dt import parse_datetime, now

_LOGGER = logging.getLogger(__name__)

class CustomTemplateSensor(SensorEntity):
    """Custom Template Sensor for Home Assistant."""

    def __init__(self, hass, unique_id, state_template, unit_of_measurement=None, device_class=None, icon=None):
        """Initialize the sensor."""
        self.hass = hass
        self._unique_id = unique_id
        self._state_template = state_template
        self._unit_of_measurement = unit_of_measurement
        self._device_class = device_class
        self._icon = icon

    @property
    def state(self):
        """Return the sensor's state after rendering the template."""
        try:
            return self.hass.helpers.template.Template(self._state_template).async_render()
        except Exception as e:
            _LOGGER.error("Template rendering failed for %s: %s", self._unique_id, e)
            return "error"

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement."""
        return self._unit_of_measurement

    @property
    def device_class(self):
        """Return the device class."""
        return self._device_class

    @property
    def icon(self):
        """Return the icon."""
        return self._icon

    async def async_update(self):
        """Update the sensor (if needed for future logic)."""
        pass


async def async_setup_entry(hass: HomeAssistant, config_entry, async_add_entities: AddEntitiesCallback):
    """Set up the sensor platform and add the entities."""
    
    # Fetch the last update time from the gas meter sensor
    gas_meter_update = hass.states.get("sensor.gas_meter_latest_update")

    if not gas_meter_update or gas_meter_update.state in [None, "unknown", "unavailable"]:
        _LOGGER.error("Sensor 'sensor.gas_meter_latest_update' has an invalid state.")
        return

    try:
        start_time = parse_datetime(gas_meter_update.state)
        if not start_time:
            raise ValueError("Invalid datetime format")
    except ValueError:
        _LOGGER.error("Invalid datetime format for 'sensor.gas_meter_latest_update': %s", gas_meter_update.state)
        return

    # Create HistoryStats instance for tracking heating interval
    history_stats = HistoryStats(
        hass=hass,
        entity_id="switch.kociol_l1",
        entity_states="on",
        start=start_time,
        end=now(),  # Set the current time as the end
        duration=None  # Explicitly passing duration as None
    )

    # Initialize HistoryStatsUpdateCoordinator
    coordinator = HistoryStatsUpdateCoordinator(
        hass=hass,
        history_stats=history_stats,
        config_entry=config_entry,
        name="Heating Interval"
    )

    # Create HistoryStatsSensor
    history_stats_sensor = HistoryStatsSensor(
        hass=hass,
        name="Heating Interval",
        source_entity_id="switch.kociol_l1",
        sensor_type="time",
        unique_id="heating_interval",
        coordinator=coordinator
    )

    # Add sensors to Home Assistant
    async_add_entities([history_stats_sensor], update_before_add=True)

    _LOGGER.info("Heating Interval sensor added successfully.")

    # Define custom template sensors
    sensors = [
        CustomTemplateSensor(
            hass=hass,
            unique_id="consumed_gas",
            state_template="{{ (states('gas_meter.latest_gas_data') | float(0) + (states('sensor.heating_interval') | float(0) * states('gas_meter.average_m3_per_min') | float(0.010692178587454502)) | round(3)) }}",
            unit_of_measurement="m³",
            device_class="gas",
            icon="mdi:gas-cylinder",
        ),
        CustomTemplateSensor(
            hass=hass,
            unique_id="gas_meter_latest_update",
            state_template="{{ states('gas_meter.latest_gas_update') }}",
            icon="mdi:clock",
        ),
    ]
    async_add_entities(sensors, update_before_add=True)

    # Update state_class for 'sensor.consumed_gas' if it exists
    registry = await async_get_entity_registry(hass)
    entity_id = "sensor.consumed_gas"
    
    if entity_id in registry.entities:
        registry.async_update_entity(entity_id, state_class="total")
    else:
        _LOGGER.warning(f"Entity {entity_id} not found in the registry.")
