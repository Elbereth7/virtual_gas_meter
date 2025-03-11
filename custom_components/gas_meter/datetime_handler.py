from datetime import datetime, timedelta, date

def string_to_datetime(datetime_string):
    try:
        gas_datetime = datetime.strptime(datetime_string, '%Y-%m-%d %H:%M:%S.%f%z')
    except ValueError:
        try:
            gas_datetime = datetime.strptime(datetime_string, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            gas_datetime = datetime.strptime(datetime_string, "%Y-%m-%d %H:%M")
    return gas_datetime
