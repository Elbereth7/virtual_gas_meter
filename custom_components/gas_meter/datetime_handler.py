from datetime import datetime, timedelta, date

# 2025-01-12T14:50:00.000Z
def string_to_datetime(datetime_string):
    try:
        gas_datetime = datetime.strptime(datetime_string, '%Y-%m-%d %H:%M:%S.%f%z')
    except ValueError:
        gas_datetime = datetime.strptime(datetime_string, "%Y-%m-%d %H:%M")
    return gas_datetime
