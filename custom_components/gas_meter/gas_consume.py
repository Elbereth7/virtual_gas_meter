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

    # Convert entire object to list of dictionaries (JSON serializable)
    def to_list(self):
        return self.data

    # Optional: Automatically return JSON-compatible list when serialized
    def __iter__(self):
        """Ensure the class behaves like a list during iteration."""
        return iter(self.to_list())

    # Optional: Automatic JSON serialization (if you want to use json.dumps directly)
    def __repr__(self):
        return str(self.to_list())
