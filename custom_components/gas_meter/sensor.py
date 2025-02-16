from homeassistant.components.template.template_entity import TemplateSensor
from homeassistant.components.history_stats.sensor import HistoryStatsSensor
from homeassistant.helpers.entity_registry import async_get as async_get_entity_registry
import logging

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up the integration from a config entry."""
    # Create template sensors
    sensors = [
        TemplateSensor(
            hass,
            {
                "name": "Consumed Gas",
                "state": "{{ (states('gas_meter.latest_gas_data') | float(0) + (states('sensor.heating_interval') | float(0) * states('gas_meter.average_m3_per_min') | float(0.010692178587454502)))  | round(3) }}",
                "unique_id": "2452716740004",
                "unit_of_measurement": "m³",
                "device_class": "gas",
            },
        ),
        TemplateSensor(
            hass,
            {
                "name": "Gas Meter Start Time",
                "state": "{{ states('gas_meter.latest_gas_update') }}",
                "unique_id": "gas_meter_latest_update",
            },
        ),
    ]
    
    # Add the template sensors to Home Assistant
    async_add_entities(sensors, update_before_add=True)

    # Create history stats sensor
    history_stats_sensor = HistoryStatsSensor(
        hass,
        {
            "name": "Heating Interval",
            "entity_id": "switch.kociol_l1",
            "state": "on",
            "type": "time",
            "start_template": "{{ states('sensor.gas_meter_latest_update') }}",
            "end_template": "{{ now() }}",
            "unique_id": "heating_interval",
        },
    )
    async_add_entities([history_stats_sensor], update_before_add=True)

    # Set state_class for the consumed_gas sensor
    registry = await async_get_entity_registry(hass)
    entity_id = "sensor.consumed_gas"
    if entity_id in registry.entities:
        registry.async_update_entity(
            entity_id,
            state_class="total",
        )
    else:
        _LOGGER.warning(f"Entity {entity_id} not found in the registry.")
