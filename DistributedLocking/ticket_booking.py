import redis
import time
import random
from distributed_lock import DistributedLock

class TicketBookingSystem:
    """
    A ticket booking system that uses distributed locking to prevent double bookings.
    
    This class demonstrates how to use distributed locks to handle concurrent 
    ticket reservation requests in a distributed environment.
    """
    
    def __init__(self, redis_host='localhost', redis_port=6379, redis_db=0):
        """
        Initialize the ticket booking system.
        
        Args:
            redis_host: Redis server hostname
            redis_port: Redis server port
            redis_db: Redis database number
        """
        self.redis = redis.Redis(host=redis_host, port=redis_port, db=redis_db, decode_responses=True)
        
        # Prefix for our keys in Redis
        self.seat_key_prefix = "seat:"
        self.lock_key_prefix = "lock:"
        self.reservation_ttl = 300  # 5 minutes in seconds
    
    def _get_seat_key(self, event_id, seat_id):
        """Generate the Redis key for a seat."""
        return f"{self.seat_key_prefix}{event_id}:{seat_id}"
    
    def _get_lock_key(self, event_id, seat_id):
        """Generate the Redis key for a seat lock."""
        return f"{self.lock_key_prefix}{event_id}:{seat_id}"
    
    def is_seat_available(self, event_id, seat_id):
        """
        Check if a seat is available.
        
        Args:
            event_id: ID of the event
            seat_id: ID of the seat
            
        Returns:
            bool: True if the seat is available, False otherwise
        """
        seat_key = self._get_seat_key(event_id, seat_id)
        return not self.redis.exists(seat_key)
    
    def try_reserve_seat(self, event_id, seat_id, user_id, timeout=5):
        """
        Try to reserve a seat for a user using distributed locking.
        
        Args:
            event_id: ID of the event
            seat_id: ID of the seat
            user_id: ID of the user trying to book the seat
            timeout: How long to try acquiring the lock in seconds
            
        Returns:
            bool: True if the seat was successfully reserved, False otherwise
        """
        seat_key = self._get_seat_key(event_id, seat_id)
        lock_key = self._get_lock_key(event_id, seat_id)
        
        # Create a distributed lock for this seat
        lock = DistributedLock(self.redis, lock_key, expire_time=timeout)
        
        try:
            # Try to acquire the lock
            if not lock.acquire(retry_times=5):
                print(f"User {user_id} could not acquire lock for seat {seat_id} at event {event_id}")
                return False
            
            # Check if the seat is still available
            if not self.is_seat_available(event_id, seat_id):
                print(f"Seat {seat_id} at event {event_id} is already booked")
                return False
            
            # Simulate some processing time (e.g., payment processing)
            process_time = random.uniform(0.1, 0.5)
            time.sleep(process_time)
            
            # Book the seat
            self.redis.setex(seat_key, self.reservation_ttl, user_id)
            print(f"User {user_id} successfully booked seat {seat_id} at event {event_id}")
            return True
            
        finally:
            # Always release the lock when done
            lock.release()
    
    def cancel_reservation(self, event_id, seat_id, user_id):
        """
        Cancel a seat reservation.
        
        Args:
            event_id: ID of the event
            seat_id: ID of the seat
            user_id: ID of the user who booked the seat
            
        Returns:
            bool: True if the reservation was cancelled, False otherwise
        """
        seat_key = self._get_seat_key(event_id, seat_id)
        lock_key = self._get_lock_key(event_id, seat_id)
        
        # Create a distributed lock for this seat
        lock = DistributedLock(self.redis, lock_key)
        
        try:
            # Try to acquire the lock
            if not lock.acquire():
                print(f"User {user_id} could not acquire lock to cancel reservation")
                return False
            
            # Check if the seat is booked by this user
            current_user = self.redis.get(seat_key)
            if current_user != str(user_id):
                print(f"Seat {seat_id} at event {event_id} is not booked by user {user_id}")
                return False
            
            # Cancel the reservation
            self.redis.delete(seat_key)
            print(f"User {user_id} cancelled reservation for seat {seat_id} at event {event_id}")
            return True
            
        finally:
            # Always release the lock when done
            lock.release()
    
    def get_all_reservations(self, event_id):
        """
        Get all reservations for an event.
        
        Args:
            event_id: ID of the event
            
        Returns:
            dict: A dictionary mapping seat IDs to user IDs
        """
        pattern = f"{self.seat_key_prefix}{event_id}:*"
        keys = self.redis.keys(pattern)
        
        reservations = {}
        for key in keys:
            # Extract seat_id from the key
            seat_id = key.split(':')[-1]
            user_id = self.redis.get(key)
            reservations[seat_id] = user_id
            
        return reservations
