from pathlib import Path
from functools import wraps
import csv
from custom_components.gas_meter.datetime_handler import string_to_datetime
import pickle
from custom_components.gas_meter.gas_consume import GasConsume
import aiofiles

# Function to get the correct file path dynamically
def get_gas_actualdata_path(hass):
    return Path(hass.config.path("custom_components/gas_meter/gas_actualdata.pkl"))

# Function to save gas actual data in a file
async def save_gas_actualdata(gas_consume, hass):
    filename = get_gas_actualdata_path(hass)
    async with aiofiles.open(filename, "wb") as file:
        await file.write(pickle.dumps(gas_consume))

# Function to load gas actual data from a file when opening the app
async def load_gas_actualdata(hass):
    filename = get_gas_actualdata_path(hass)
    try:
        async with aiofiles.open(filename, "rb") as file:
            data = await file.read()
            return pickle.loads(data)
    except FileNotFoundError:
        gas_consume = GasConsume()
        return gas_consume
