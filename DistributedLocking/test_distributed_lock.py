import unittest
from unittest.mock import MagicMock, patch
import redis
import threading
import time
from distributed_lock import DistributedLock
from ticket_booking import TicketBookingSystem

class TestDistributedLock(unittest.TestCase):
    """
    Tests for the DistributedLock class to ensure it correctly handles
    concurrent access to shared resources.
    """
    
    def setUp(self):
        # Mock Redis for testing
        self.redis_mock = MagicMock(spec=redis.Redis)
        self.lock_name = "test-lock"
        self.lock = DistributedLock(self.redis_mock, self.lock_name)
    
    def test_acquire_success(self):
        # Setup Redis mock to simulate successful lock acquisition
        self.redis_mock.setnx.return_value = True
        
        # Attempt to acquire the lock
        result = self.lock.acquire()
        
        # Verify the result and Redis calls
        self.assertTrue(result)
        self.redis_mock.setnx.assert_called_once_with(self.lock_name, self.lock.lock_value)
        self.redis_mock.expire.assert_called_once_with(self.lock_name, self.lock.expire_time)
    
    def test_acquire_failure(self):
        # Setup Redis mock to simulate failed lock acquisition
        self.redis_mock.setnx.return_value = False
        
        # Attempt to acquire the lock
        result = self.lock.acquire(retry_times=1)
        
        # Verify the result and Redis calls
        self.assertFalse(result)
        self.redis_mock.setnx.assert_called_once_with(self.lock_name, self.lock.lock_value)
    
    def test_release_success(self):
        # Setup Redis mock to simulate successful lock release
        self.redis_mock.eval.return_value = 1
        
        # Attempt to release the lock
        result = self.lock.release()
        
        # Verify the result
        self.assertTrue(result)
        self.redis_mock.eval.assert_called_once()
    
    def test_release_failure(self):
        # Setup Redis mock to simulate failed lock release
        self.redis_mock.eval.return_value = 0
        
        # Attempt to release the lock
        result = self.lock.release()
        
        # Verify the result
        self.assertFalse(result)
        self.redis_mock.eval.assert_called_once()

class TestTicketBookingSystem(unittest.TestCase):
    """
    Tests for the TicketBookingSystem class to verify correct handling of
    concurrent seat reservations.
    """
    
    @patch('ticket_booking.redis.Redis')
    def test_concurrent_booking(self, mock_redis_class):
        # Setup mock Redis client
        mock_redis = MagicMock()
        mock_redis_class.return_value = mock_redis
        
        # Configure mock Redis to simulate seat availability
        def side_effect_exists(key):
            # Key doesn't exist initially, but after setex is called, it exists
            return key in self.reserved_seats
            
        def side_effect_setex(key, ttl, value):
            # Record that the seat has been reserved
            self.reserved_seats.add(key)
            
        self.reserved_seats = set()
        mock_redis.exists.side_effect = side_effect_exists
        mock_redis.setex.side_effect = side_effect_setex
        
        # Configure setnx to allow only one lock acquisition per seat
        self.locked_seats = set()
        
        def side_effect_setnx(key, value):
            if key in self.locked_seats:
                return False
            self.locked_seats.add(key)
            return True
            
        mock_redis.setnx.side_effect = side_effect_setnx
        
        # Create a ticket booking system
        booking_system = TicketBookingSystem()
        
        # Number of concurrent users trying to book the same seat
        num_users = 5
        event_id = "test-event"
        seat_id = "A1"
        
        # Track which user was successful
        successful_user = [None]
        
        def try_book_seat(user_id):
            result = booking_system.try_reserve_seat(event_id, seat_id, user_id)
            if result:
                successful_user[0] = user_id
        
        # Create and start threads for concurrent booking attempts
        threads = []
        for i in range(num_users):
            user_id = f"user-{i+1}"
            thread = threading.Thread(target=try_book_seat, args=(user_id,))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to finish
        for thread in threads:
            thread.join()
        
        # Verify that exactly one user was successful
        self.assertIsNotNone(successful_user[0], "No user was able to book the seat")
        
        # Release the lock to simulate lock expiration
        self.locked_seats.clear()
        
        # Verify that a second user can book after the first booking is cancelled
        another_user = "another-user"
        booking_system.cancel_reservation(event_id, seat_id, successful_user[0])
        self.reserved_seats.clear()  # Simulate cancellation
        
        result = booking_system.try_reserve_seat(event_id, seat_id, another_user)
        self.assertTrue(result, "Second user should be able to book after cancellation")

if __name__ == "__main__":
    unittest.main()
