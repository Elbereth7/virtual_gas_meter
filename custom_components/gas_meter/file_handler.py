from pathlib import Path
from custom_components.gas_meter.datetime_handler import string_to_datetime
import pickle
from custom_components.gas_meter.gas_consume import GasConsume
import aiofiles

def get_gas_actualdata_path(hass):
    """Returns the path to the gas consumption data file."""
    return Path(hass.config.path("custom_components/gas_meter/gas_actualdata.pkl"))

async def save_gas_actualdata(gas_consume, hass):
    """Saves the gas consumption data to a file asynchronously."""
    filename = get_gas_actualdata_path(hass)
    async with aiofiles.open(filename, "wb") as file:
        await file.write(pickle.dumps(gas_consume))

async def load_gas_actualdata(hass):
    """
    Loads gas consumption data from a file asynchronously.
    If the file does not exist, returns a new GasConsume object.
    """
    filename = get_gas_actualdata_path(hass)
    try:
        async with aiofiles.open(filename, "rb") as file:
            data = await file.read()
            return pickle.loads(data)
    except FileNotFoundError:
        gas_consume = GasConsume()
        return gas_consume
