# Virtual Gas Meter for Home Assistant

## Overview

The **Virtual Gas Meter** is a Home Assistant integration that estimates gas consumption (in cubic meters) based on the operating time of a boiler. It calculates gas usage using Home Assistant's historical data and user-provided manual readings.

## Features

- **Virtual Gas Meter Calculation**: Estimates gas consumption using time-based calculations.
- **Sensor Integration**: Creates Home Assistant sensors to track gas usage and historical updates.
- **Manual Data Entry**: Allows users to input real gas meter readings periodically.
- **Historical Data Analysis**: Uses Home Assistant's history to determine boiler runtime.
- **Logging & Persistence**: Stores and retrieves gas meter data using a file-based system.

## Installation

### 1. Clone the Repository

```sh
git clone https://github.com/Elbereth7/virtual_gas_meter
```

### 2. Copy Files to Home Assistant

Copy the `gas_meter` folder into your Home Assistant `custom_components` directory:

```sh
cp -r virtual_gas_meter/custom_components/gas_meter /config/custom_components/
```

### 3. Restart Home Assistant

Restart Home Assistant for the integration to load.

## Configuration

Add the following to your `configuration.yaml`:

```yaml
sensor:
  - platform: template
    sensors:
      consumed_gas:
        friendly_name: "Consumed Gas"
        value_template: "{{ (states('gas_meter.latest_gas_data') | float(0) + (states('sensor.heating_interval') | float(0) * states('gas_meter.average_m3_per_min') | float(0.010692178587454502)))  | round(3) }}"
        unique_id: '2452716740004'
        unit_of_measurement: m³
        device_class: gas
      gas_meter_latest_update:
        friendly_name: "Gas Meter Start Time"
        value_template: "{{ states('gas_meter.latest_gas_update') }}"
        unique_id: 'gas_meter_latest_update'
  
  - platform: history_stats
    name: Heating interval
    entity_id: switch.kociol_l1
    state: 'on'
    type: time
    start: "{{ states('sensor.gas_meter_latest_update') }}"
    end: "{{ now() }}"
    unique_id: "heating_interval"
```

## Services

This integration provides two custom Home Assistant services:

### `trigger_gas_update`

- **Description**: Enter actual gas meter readings.
- **Fields**:
  - `datetime`: The timestamp of the reading (format: `YYYY-MM-DD HH:MM`).
  - `consumed_gas`: The measured gas consumption in cubic meters.
- **Example Call**:

```yaml
service: gas_meter.trigger_gas_update
data:
  datetime: "2025-01-12 15:51"
  consumed_gas: 4247.816
```

### `read_gas_actualdata_file`

- **Description**: Read historical gas meter data from logs.
- **Example Call**:

```yaml
service: gas_meter.read_gas_actualdata_file
```

## Code Overview

The integration consists of the following files:

### `__init__.py`

Handles the initialization and setup of the integration, including data persistence and service registration.

### `datetime_handler.py`

Handles date-time parsing and conversion for the integration.

### `file_handler.py`

Manages file operations for saving and retrieving gas meter data.

### `gas_consume.py`

Defines the `GasConsume` class for managing gas meter records.

### `manifest.json`

Defines the metadata for the integration, including dependencies and versioning.

### `services.yaml`

Describes the available Home Assistant services for the integration.

## Usage

1. **Start tracking gas consumption**: The integration automatically calculates virtual gas meter readings based on boiler runtime.
2. **Manually update the gas meter**: Use the `trigger_gas_update` service to enter real gas readings.
3. **Check historical data**: Use `read_gas_actualdata_file` to retrieve past records from logs.

## Contributing

Contributions are welcome! Feel free to submit pull requests or report issues in the GitHub repository.

## License

This project is licensed under the MIT License. See `LICENSE` for details.

