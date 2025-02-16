"""Vitual gas meter"""
import logging
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.components.recorder.history import get_significant_states
from homeassistant.util import dt as dt_util
from homeassistant.helpers.discovery import async_load_platform
from homeassistant.helpers.typing import ConfigType
import custom_components.gas_meter.file_handler as fh
DOMAIN = "gas_meter"
_LOGGER = logging.getLogger(__name__)

async def async_setup(hass: HomeAssistant, config: dict):
    """Set up the virtual gas meter integration."""
    _LOGGER.info("Loading Virtual Gas Meter integration...")
    # Register a custom service to trigger actions
    async def handle_trigger_service(call: ServiceCall):
        """Handle the custom service to run gas meter logic."""
        _LOGGER.debug("Service call received: %s", call.data)
        # Custom logic
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

                # Directly pass hass to get_significant_states, without needing to call get_instance
                history_list = await hass.async_add_executor_job(
                    get_significant_states, hass, start_time, end_time, [entity_id]
                )

                # Calculate the total time the switch was "on"
                total_on_time = 0
                previous_state = None
                previous_time = start_time
                for state in history_list.get(entity_id, []):
                    _LOGGER.info("History list record last_changed: %s", state.last_changed)
                    _LOGGER.info("History list record state: %s", state.state)
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


            # Save updated gas consumption latest_gas_update
            await fh.save_gas_actualdata(gas_consume, hass)

        except Exception as e:
            _LOGGER.error("Error in handle_trigger_service: %s", str(e))
            raise
    async def read_gas_actualdata_file(call: ServiceCall):
        """Handle the custom service to run gas meter logic."""
        _LOGGER.debug("Service call received: %s", call.data)
        # Custom logic here
        try:
            gas_consume = await fh.load_gas_actualdata(hass)
            for record in gas_consume:
                _LOGGER.info("Gas record: %s", record)
        except Exception as e:
            _LOGGER.error("Error in read_gas_actualdata_file: %s", str(e))
            raise
            
    # Register the service in Home Assistant
    hass.services.async_register(
        DOMAIN, "trigger_gas_update", handle_trigger_service
    )
    hass.services.async_register(
        DOMAIN, "read_gas_actualdata_file", read_gas_actualdata_file
    )
    # Load the sensor platform
    await async_load_platform(hass, "sensor", DOMAIN, {}, config)
    return True