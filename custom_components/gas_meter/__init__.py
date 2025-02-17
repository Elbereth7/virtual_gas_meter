import logging
import inspect
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.components.recorder.history import get_significant_states
from homeassistant.util import dt as dt_util
from homeassistant.helpers.discovery import async_load_platform
from homeassistant.components.history_stats.coordinator import HistoryStatsUpdateCoordinator, HistoryStats
from homeassistant.config_entries import ConfigEntry
import custom_components.gas_meter.file_handler as fh

DOMAIN = "gas_meter"
_LOGGER = logging.getLogger(__name__)

async def _register_services(hass: HomeAssistant):
    """Register services shared between legacy and UI setups."""
    async def handle_trigger_service(call: ServiceCall):
        """Handle the service call to update gas meter data."""
        try:
            gas_consume = await fh.load_gas_actualdata(hass)
            gas_new_datetime = fh.string_to_datetime(call.data["datetime"])
            gas_new_data = float(call.data["consumed_gas"])
            gas_consume.add_record(gas_new_datetime, gas_new_data)

            if len(gas_consume) > 1:
                gas_prev_datetime = gas_consume[-2]["datetime"]
                gas_prev_data = gas_consume[-2]["consumed_gas"]

                # Get the state history of the switch between the two timestamps
                start_time = dt_util.as_utc(gas_prev_datetime)
                end_time = dt_util.as_utc(gas_new_datetime)
                entity_id = "switch.kociol_l1"
                history_list = await hass.async_add_executor_job(
                    get_significant_states, hass, start_time, end_time, [entity_id]
                )

                # Calculate the total time the switch was "on"
                total_on_time = 0
                previous_state = None
                previous_time = start_time
                for state in history_list.get(entity_id, []):
                    current_time = state.last_changed

                    if previous_state == "on":
                        total_on_time += (current_time - previous_time).total_seconds()

                    previous_state = state.state
                    previous_time = current_time

                # Handle the last segment
                if previous_state == "on":
                    total_on_time += (end_time - previous_time).total_seconds()

                total_min = total_on_time / 60  # Total time in minutes

                # Count m3/min for the current interval ("m3/min for interval")
                gas_data_diff = gas_new_data - gas_prev_data
                if total_min:
                    gas_consume[-1]["m3/min for interval"] = gas_data_diff / total_min
                
                # Count how much gas was consumed from the first data till the last data ("consumed_gas_cumulated")
                consumed_gas_cumulated = gas_new_data - gas_consume[0]["consumed_gas"]
                gas_consume[-1]["consumed_gas_cumulated"] = consumed_gas_cumulated

                # Count how many minutes the boiler was working starting from the first data till the last data ("min_cumulated")
                if len(gas_consume) == 2:
                    min_cumulated = total_min
                elif len(gas_consume) > 2:
                    min_cumulated = total_min + gas_consume[-2]["min_cumulated"]
                gas_consume[-1]["min_cumulated"] = min_cumulated

                # Count m3/min for the whole period between the first data till the last data ("average m3/min")
                if min_cumulated:
                    av_min = consumed_gas_cumulated / min_cumulated
                    gas_consume[-1]["average m3/min"] = av_min

                    hass.states.async_set(f"{DOMAIN}.average_m3_per_min", av_min)
                    
            hass.states.async_set(f"{DOMAIN}.latest_gas_update", gas_new_datetime)
            hass.states.async_set(f"{DOMAIN}.latest_gas_data", gas_new_data)

            # Save updated gas consumption
            await fh.save_gas_actualdata(gas_consume, hass)

        except Exception as e:
            _LOGGER.error("Error in handle_trigger_service: %s", str(e))
            raise
            
    async def read_gas_actualdata_file(call: ServiceCall):
        """Read and log gas meter data."""
        try:
            gas_consume = await fh.load_gas_actualdata(hass)
            for record in gas_consume:
                _LOGGER.info("Gas record: %s", record)
        except Exception as e:
            _LOGGER.error("Error in read_gas_actualdata_file: %s", str(e))
            raise

    def inspect_class(cls):
        # Print the class name
        _LOGGER.info(f"Class: {cls.__name__}")
        
        # Print the docstring for the class
        _LOGGER.info(f"Docstring: {cls.__doc__}")
        
        # Print the __init__ method signature and docstring
        if hasattr(cls, '__init__'):
            _LOGGER.info("\n__init__ method:")
            _LOGGER.info(f"Signature: {cls.__init__.__annotations__}")
            _LOGGER.info(f"Docstring: {cls.__init__.__doc__}")
        
        # Print other methods and their docstrings
        _LOGGER.info("\nMethods:")
        for name, method in cls.__dict__.items():
            if callable(method):
                _LOGGER.info(f"{name}:")
                _LOGGER.info(f"  Docstring: {method.__doc__}")
        
        # Print attributes
        _LOGGER.info("\nAttributes:")
        for name, value in cls.__dict__.items():
            if not callable(value):
                _LOGGER.info(f"{name}: {value}")

    async def debug_history_stats_sensor(hass: HomeAssistant):
        """Debug and log valid parameters for HistoryStatsUpdateCoordinator."""
        try:
            constructor_signature = inspect.signature(HistoryStatsUpdateCoordinator)

            _LOGGER.info("Valid Parameters for HistoryStatsUpdateCoordinator:")
            for param_name, param in constructor_signature.parameters.items():
                _LOGGER.info(f"- {param_name}: {param.annotation} (Default: {param.default})")
            
            inspect_class(HistoryStatsUpdateCoordinator)

        except ImportError as e:
            _LOGGER.error(f"Error importing HistoryStatsUpdateCoordinator: {e}")
            
    # Register the services
    hass.services.async_register(
        DOMAIN, "trigger_gas_update", handle_trigger_service
    )
    hass.services.async_register(
        DOMAIN, "read_gas_actualdata_file", read_gas_actualdata_file
    )
    hass.services.async_register(
        DOMAIN, "debug_history_stats_sensor", debug_history_stats_sensor
    )

async def async_setup(hass: HomeAssistant, config: dict):
    """Set up the virtual gas meter integration (legacy YAML setup)."""
    _LOGGER.info("Loading Virtual Gas Meter integration...")
    await _register_services(hass)
    await async_load_platform(hass, "sensor", DOMAIN, {}, config)
    return True

async def async_setup_entry(hass: HomeAssistant, config_entry: ConfigEntry):
    """Set up the integration from a config entry (UI setup)."""
    await _register_services(hass)
    await hass.config_entries.async_forward_entry_setups(config_entry, ["sensor"])
    return True

async def async_unload_entry(hass: HomeAssistant, config_entry: ConfigEntry):
    """Unload the integration."""
    # Forward the unloading to the sensor platform
    await hass.config_entries.async_forward_entry_unload(config_entry, "sensor")
    return True
