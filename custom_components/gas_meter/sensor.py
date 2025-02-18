import logging
from datetime import datetime, timedelta
from homeassistant.core import HomeAssistant
from homeassistant.components.sensor import SensorEntity
from homeassistant.components.history_stats.sensor import HistoryStatsSensor
from homeassistant.components.history_stats.coordinator import HistoryStatsUpdateCoordinator, HistoryStats
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.entity_registry import async_get as async_get_entity_registry
from homeassistant.util.dt import parse_datetime, now
from homeassistant.helpers.template import Template

_LOGGER = logging.getLogger(__name__)


class CustomTemplateSensor(SensorEntity):
    """Custom Template Sensor for Home Assistant."""

    def __init__(self, hass, friendly_name, unique_id, state_template, unit_of_measurement=None, device_class=None, icon=None):
        """Initialize the sensor."""
        self.hass = hass
        self._attr_name = friendly_name  # Set the friendly name
        self._attr_unique_id = unique_id  # Set the unique ID
        self._state_template = state_template
        self._attr_unit_of_measurement = unit_of_measurement
        self._attr_device_class = device_class
        self._attr_icon = icon
        self._state = None

    @property
    def state(self):
        """Return the sensor's state."""
        return self._state

    async def async_update(self):
        """Update the sensor by rendering the template."""
        try:
            # Render the template asynchronously
            self._state = await self.hass.async_add_executor_job(
                self._render_template
            )
        except Exception as e:
            _LOGGER.error("Template rendering failed for %s: %s", self._attr_unique_id, str(e))
            self._state = "error"

    def _render_template(self):
        """Render the template synchronously."""
        template = Template(self._state_template, self.hass)
        return template.async_render()


async def async_setup_entry(hass: HomeAssistant, config_entry, async_add_entities: AddEntitiesCallback):
    """Set up the sensor platform and add the entities."""
    
    # Fetch the last update time from the gas meter sensor
    gas_meter_update = hass.states.get("sensor.gas_meter_latest_update")

    if not gas_meter_update or gas_meter_update.state in [None, "unknown", "unavailable"]:
        _LOGGER.warning("Sensor 'sensor.gas_meter_latest_update' is unavailable. Using fallback start time.")
        start_time = Template("{{ now()}}", hass)  # Template object
    else:
        try:
            parsed_time = parse_datetime(gas_meter_update.state)
            if parsed_time is None:
                raise ValueError("Invalid datetime format")
            start_time = Template("{{ states('sensor.gas_meter_latest_update') }}", hass)  # Template object
        except ValueError:
            _LOGGER.error("Invalid datetime format for 'sensor.gas_meter_latest_update': %s", gas_meter_update.state)
            return

    # Create HistoryStats instance for tracking heating interval
    history_stats = HistoryStats(
        hass=hass,
        entity_id="switch.kociol_l1",
        entity_states="on",
        start=start_time,  # Template object
        end=Template("{{ now() }}", hass),  # Template object
        duration=None
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
            friendly_name="Consumed gas",
            unique_id="consumed_gas",  # Unique ID for the entity
            state_template="{{ (states('gas_meter.latest_gas_data') | float(0) + (states('sensor.heating_interval') | float(0) * states('gas_meter.average_m3_per_min') | float(0.010692178587454502)) | round(3)) }}",
            unit_of_measurement="m³",
            device_class="gas",
            icon="mdi:gas-cylinder",
        ),
        CustomTemplateSensor(
            hass=hass,
            friendly_name="Gas meter latest update",
            unique_id="gas_meter_latest_update",  # Unique ID for the entity
            state_template="{{ states('gas_meter.latest_gas_update') }}",
            icon="mdi:clock",
        ),
    ]
    async_add_entities(sensors, update_before_add=True)

    # Update state_class for 'sensor.consumed_gas' if it exists
    registry = async_get_entity_registry(hass)
    entity_id = "sensor.consumed_gas"
    
    if entity_id in registry.entities:
        registry.async_update_entity(entity_id, state_class="total")
    else:
        _LOGGER.warning("Entity %s not found in the registry, skipping state_class update.", entity_id)
