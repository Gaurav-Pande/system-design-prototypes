import threading
import time
import random
import uuid
from queue import Queue
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(threadName)s - %(message)s'
)

class InMemoryRedis:
    """
    A simple in-memory implementation of the Redis commands we need for distributed locking.
    This is used for demonstration purposes when a real Redis server isn't available.
    """
    def __init__(self):
        self._data = {}
        self._expiry = {}
        self._lock = threading.Lock()  # For thread safety
    
    def setnx(self, key, value):
        """Set key to value if key doesn't exist"""
        with self._lock:
            if key in self._data:
                return False
            self._data[key] = value
            return True
    
    def expire(self, key, seconds):
        """Set an expiration on key"""
        with self._lock:
            if key in self._data:
                expiry_time = time.time() + seconds
                self._expiry[key] = expiry_time
                return True
            return False
    
    def get(self, key):
        """Get the value of key"""
        with self._lock:
            self._check_expiry(key)
            return self._data.get(key)
    
    def delete(self, key):
        """Delete key"""
        with self._lock:
            if key in self._data:
                del self._data[key]
                if key in self._expiry:
                    del self._expiry[key]
                return 1
            return 0
    
    def _check_expiry(self, key):
        """Check if a key has expired and remove it if necessary"""
        if key in self._expiry and time.time() > self._expiry[key]:
            del self._data[key]
            del self._expiry[key]
    
    def keys(self, pattern):
        """Get keys matching pattern (simplified, just returns all keys)"""
        with self._lock:
            for key in list(self._data.keys()):
                self._check_expiry(key)
            return list(self._data.keys())
    
    def eval(self, script, num_keys, key, value):
        """Simplified implementation of Lua script eval for our release lock use case"""
        with self._lock:
            self._check_expiry(key)
            if key in self._data and self._data[key] == value:
                del self._data[key]
                if key in self._expiry:
                    del self._expiry[key]
                return 1
            return 0


class DistributedLock:
    """
    A distributed lock implementation using our in-memory Redis.
    """
    def __init__(self, redis_client, lock_name, expire_time=10):
        self.redis = redis_client
        self.lock_name = lock_name
        self.expire_time = expire_time
        self.lock_value = str(uuid.uuid4())  # Unique identifier for this lock instance
    
    def acquire(self, retry_times=3, retry_delay=0.2):
        for i in range(retry_times):
            if self.redis.setnx(self.lock_name, self.lock_value):
                self.redis.expire(self.lock_name, self.expire_time)
                return True
                
            if i < retry_times - 1:
                time.sleep(retry_delay * (random.random() + 0.5))  # Add jitter
                
        return False
    
    def release(self):
        # For our in-memory implementation, we simulate the Lua script
        return self.redis.eval("", 1, self.lock_name, self.lock_value) == 1


class TicketBookingSystem:
    """Ticket booking system with distributed locking."""
    
    def __init__(self, redis_client):
        self.redis = redis_client
        self.seat_key_prefix = "seat:"
        self.lock_key_prefix = "lock:"
        self.reservation_ttl = 300  # 5 minutes
    
    def _get_seat_key(self, event_id, seat_id):
        return f"{self.seat_key_prefix}{event_id}:{seat_id}"
    
    def _get_lock_key(self, event_id, seat_id):
        return f"{self.lock_key_prefix}{event_id}:{seat_id}"
    
    def is_seat_available(self, event_id, seat_id):
        seat_key = self._get_seat_key(event_id, seat_id)
        return self.redis.get(seat_key) is None
    
    def try_reserve_seat(self, event_id, seat_id, user_id, timeout=5):
        seat_key = self._get_seat_key(event_id, seat_id)
        lock_key = self._get_lock_key(event_id, seat_id)
        
        lock = DistributedLock(self.redis, lock_key, expire_time=timeout)
        
        try:
            if not lock.acquire(retry_times=3):
                logging.info(f"User {user_id} could not acquire lock for seat {seat_id}")
                return False
            
            if not self.is_seat_available(event_id, seat_id):
                logging.info(f"Seat {seat_id} is already booked")
                return False
            
            # Simulate processing time (e.g., payment processing)
            process_time = random.uniform(0.1, 0.3)
            time.sleep(process_time)
            
            # Book the seat
            self.redis.setnx(seat_key, user_id)
            self.redis.expire(seat_key, self.reservation_ttl)
            logging.info(f"User {user_id} successfully booked seat {seat_id}")
            return True
            
        finally:
            lock.release()
    
    def get_all_reservations(self, event_id):
        pattern = f"{self.seat_key_prefix}{event_id}:"
        keys = self.redis.keys(pattern)
        
        reservations = {}
        for key in keys:
            # Extract seat_id from the key
            seat_id = key.split(':')[-1]
            user_id = self.redis.get(key)
            if user_id:
                reservations[seat_id] = user_id
            
        return reservations


def simulate_user(booking_system, event_id, user_id, seat_id, results_queue):
    """Simulate a user trying to book a specific seat."""
    result = booking_system.try_reserve_seat(event_id, seat_id, user_id)
    results_queue.put((user_id, seat_id, result))


def run_simulation():
    """Run a simulation with multiple concurrent users trying to book the same seat."""
    # Create an in-memory Redis instance
    redis_client = InMemoryRedis()
    
    # Create a ticket booking system
    booking_system = TicketBookingSystem(redis_client)
    
    # Create a queue to collect results
    results_queue = Queue()
    
    # Create and start user threads all trying to book the same seat
    threads = []
    event_id = "concert-2023"
    seat_id = "A1"  # All users try to book the same seat
    
    logging.info("Starting simulation with 5 users trying to book the same seat")
    
    for i in range(5):
        user_id = f"user-{i+1}"
        thread = threading.Thread(
            target=simulate_user,
            args=(booking_system, event_id, user_id, seat_id, results_queue),
            name=f"User-{i+1}"
        )
        threads.append(thread)
        thread.start()
    
    # Wait for all threads to finish
    for thread in threads:
        thread.join()
    
    # Collect and display results
    successful_bookings = []
    while not results_queue.empty():
        user_id, seat_id, success = results_queue.get()
        if success:
            successful_bookings.append((user_id, seat_id))
    
    # Display the results
    logging.info("\n--- Simulation Results ---")
    
    if len(successful_bookings) == 1:
        user_id, seat_id = successful_bookings[0]
        logging.info(f"SUCCESS: Only user {user_id} was able to book seat {seat_id}.")
        logging.info("This demonstrates that the distributed lock prevented double bookings.")
    elif len(successful_bookings) == 0:
        logging.info("FAILURE: No user was able to book the seat.")
    else:
        logging.info(f"FAILURE: {len(successful_bookings)} users were able to book the same seat!")
        for user_id, seat_id in successful_bookings:
            logging.info(f"  - User {user_id} booked seat {seat_id}")
        logging.info("This indicates the distributed lock failed to prevent double bookings.")
    
    # Show final reservations
    reservations = booking_system.get_all_reservations(event_id)
    logging.info("\n--- Final Reservations ---")
    for seat, user in reservations.items():
        logging.info(f"Seat {seat} is booked by {user}")


if __name__ == "__main__":
    run_simulation()
