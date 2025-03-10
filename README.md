# Virtual Gas Meter for Home Assistant

## Overview

The **Virtual Gas Meter** is a Home Assistant integration designed to estimate gas consumption using an average gas usage rate. It provides a virtual sensor that mimics a real-life gas meter by calculating gas consumption based on boiler runtime. Additionally, users can manually update the sensor with real-life gas meter readings to improve accuracy over time.
## Features

- **Virtual Gas Meter Calculation**: Estimates gas consumption using time-based calculations.
- **Sensor Integration**: Creates Home Assistant sensors to track gas usage and historical updates.
- **Manual Data Entry**: Allows users to input real gas meter readings periodically.
- **Historical Data Analysis**: Uses Home Assistant's history stats to calculate active heating intervals.
- **Logging & Persistence**: Stores and retrieves gas meter data using a file-based system.
- **Provides configurable options** to customize gas calculation parameters.
- **Implements Home Assistant services** to trigger manual gas updates and read stored data.
- **Supports Home Assistant's UI-based configuration flow**.

## Installation

### Install via HACS (Recommended)
1. **Ensure HACS is installed** in your Home Assistant instance.
2. **Add the Custom Repository:**
   - Open HACS in Home Assistant.
   - Navigate to `Integrations` and click the three-dot menu.
   - Select `Custom Repositories`.
   - Add the repository URL: `https://github.com/Elbereth7/virtual_gas_meter`.
   - Choose `Integration` as the category and click `Add`.
3. **Install the Integration:**
   - Search for `Virtual Gas Meter` in HACS and install it.
   - Restart Home Assistant to apply changes.
   
### Manual Installation
1. Download the repository as a ZIP file and extract it.
2. Copy the `custom_components/gas_meter` folder into your Home Assistant `config/custom_components/` directory.
3. Restart Home Assistant.

## Configuration

### Adding the Integration
1. Navigate to **Settings** > **Devices & Services**.
2. Click **"Add Integration"** and search for `Virtual Gas Meter`.
3. Select your boiler switch (`switch.xxx`).
4. Optionally, enter an average gas consumption per hour (m³) and the latest gas meter state.
5. Click **"Submit"**.
   
### Services

#### `trigger_gas_update`
This service allows users to manually enter a real-life gas meter reading. This is crucial to keep the virtual gas meter accurate over time.

- **Why use this?**
  - The virtual gas meter **estimates** gas consumption using the average rate.
  - By entering real readings, the system **adjusts** the average gas consumption for better accuracy.
  - If no real readings are provided, the virtual gas meter relies on the initial average entered during installation (or a default value if none was provided).
  
- **Fields:**
  - `datetime`: Timestamp for the gas reading (format: `YYYY-MM-DD HH:MM`).
  - `consumed_gas`: Gas meter reading in cubic meters (`m³`).

- **Service Call Example (via Developer Tools > Services):**

  ```yaml
  service: gas_meter.trigger_gas_update
  data:
    datetime: "2025-02-12 15:51"
    consumed_gas: 4447.816
  ```

#### `read_gas_actualdata_file`
This service reads the stored gas meter data file.

- **Service Call Example (via Developer Tools > Services):**

```yaml
service: gas_meter.read_gas_actualdata_file
```
## Code Overview

The integration consists of the following files:

### `__init__.py`
- Handles the initialization and setup of the integration, including data persistence and service registration.

### `sensor.py`
- Implements:
  - `CustomTemplateSensor` for dynamic gas calculations.
  - `GasDataSensor` to track stored gas usage data.
  - `CustomHistoryStatsSensor` for boiler operation tracking.

### `config_flow.py`
- Manages Home Assistant’s UI-based configuration flow.

### `datetime_handler.py`
- Handles date-time parsing and conversion.

### `file_handler.py`
- Manages asynchronous file operations for gas consumption data.

### `gas_consume.py`
- Stores gas consumption records using a custom list-based class.

### `manifest.json`
- Defines integration metadata, dependencies, and requirements.

### `services.yaml`
- Documents the available Home Assistant services for interacting with the integration.

### `translations/en.json`
- Provides user-friendly descriptions for the configuration flow.


## Usage

1. **Monitor gas consumption** in Home Assistant's dashboard.
2. **Trigger gas updates manually** using `trigger_gas_update` if needed.
3. **Read stored data** with `read_gas_actualdata_file`.
4. **Customize calculations** by adjusting the boiler entity and average consumption settings.

## Support & Issues

For any issues or feature requests, please visit the [GitHub Issue Tracker](https://github.com/Elbereth7/virtual_gas_meter/issues).

## Contributing

Contributions are welcome! Feel free to submit pull requests or report issues in the GitHub repository.

## License

This project is licensed under the MIT License. See [LICENSE](https://github.com/Elbereth7/virtual_gas_meter/blob/main/LICENSE) for details.

## Conclusion

By installing and periodically updating the Virtual Gas Meter, users can maintain an accurate and useful gas consumption tracking system within Home Assistant. Keeping the gas meter updated with real-life readings ensures the highest accuracy in long-term tracking. 🚀
