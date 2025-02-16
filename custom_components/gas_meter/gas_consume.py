from collections import UserList

# Class for storing and managing records.
class GasConsume(UserList):

    # Add record to self.data
    def add_record(self, datetime, consumed_gas):
        self.data.append(
            {
                "datetime": datetime,
                "consumed_gas": float(consumed_gas)
            }
        )