import time

class IdGenerator:
    def __init__(self, worker_id):
        """
        Initializes the Snowflake ID generator.
        :param worker_id: A unique ID for this worker (0-31). This is crucial for ensuring
                          uniqueness across multiple generator instances without coordination.
        """
        # 41 bits for timestamp (in milliseconds) - gives us 69 years
        # 5 bits for worker ID - 32 workers
        # 12 bits for sequence number - 4096 IDs per millisecond per worker
        self.worker_id = worker_id
        self.last_timestamp = -1
        self.sequence = 0

        # Custom epoch (e.g., the first day of 2023)
        self.epoch = 1672531200000

        if not 0 <= self.worker_id < 32:
            raise ValueError("Worker ID must be between 0 and 31")

    def _current_timestamp(self):
        """Returns the current time in milliseconds since the epoch."""
        return int(time.time() * 1000) - self.epoch

    def generate_id(self):
        """
        Generates a new 64-bit Snowflake ID.
        The ID is time-sortable and globally unique across all workers.
        """
        timestamp = self._current_timestamp()

        if timestamp < self.last_timestamp:
            # This can happen if the system clock is set backwards.
            # In a real-world scenario, you might want to have a more robust handling
            # strategy, but for this prototype, we'll raise an exception.
            raise Exception("Clock moved backwards. Refusing to generate id.")

        if self.last_timestamp == timestamp:
            # We are in the same millisecond as the last ID generation.
            # Increment the sequence number.
            self.sequence = (self.sequence + 1) & 4095  # 12-bit mask
            if self.sequence == 0:
                # Sequence number has overflowed. We must wait for the next millisecond.
                while timestamp <= self.last_timestamp:
                    timestamp = self._current_timestamp()
        else:
            # We are in a new millisecond, so we can reset the sequence number.
            self.sequence = 0

        self.last_timestamp = timestamp

        # Assemble the final ID by bit-shifting the components into place.
        # The correct shifts should be 17 for the timestamp (5+12) and 12 for the worker ID.
        new_id = (timestamp << 17) | (self.worker_id << 12) | self.sequence
        return new_id