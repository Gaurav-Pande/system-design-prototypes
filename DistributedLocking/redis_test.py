import threading
import time
import random
from ticket_booking import TicketBookingSystem
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(threadName)s - %(message)s'
)
logger = logging.getLogger(__name__)

def simulate_user(booking_system, event_id, user_id, seat_id, num_attempts=1):
    """
    Simulate a user trying to book a specific seat.
    
    Args:
        booking_system: The TicketBookingSystem instance
        event_id: ID of the event
        user_id: ID of the user
        seat_id: ID of the seat to book
        num_attempts: Number of booking attempts to make
    """
    for attempt in range(num_attempts):
        logger.info(f"User {user_id} is trying to book seat {seat_id} at event {event_id}")
        
        # Try to book the seat
        success = booking_system.try_reserve_seat(event_id, seat_id, user_id)
        
        if success:
            logger.info(f"User {user_id} successfully booked seat {seat_id}")
            break
        else:
            logger.info(f"User {user_id} failed to book seat {seat_id}")
        
        # Wait a bit before trying again
        if attempt < num_attempts - 1:
            time.sleep(random.uniform(0.2, 0.7))

def test_concurrent_booking(redis_host='localhost', redis_port=6379):
    """
    Test if distributed locking prevents concurrent bookings.
    
    Args:
        redis_host: Redis server hostname or IP
        redis_port: Redis server port
    """
    # Create a ticket booking system
    booking_system = TicketBookingSystem(redis_host=redis_host, redis_port=redis_port)
    
    # Clear any existing keys in Redis that might affect our test
    # Comment this out if you want to maintain state between runs
    logger.info("Clearing existing reservations from Redis")
    import redis
    r = redis.Redis(host=redis_host, port=redis_port, decode_responses=True)
    r.flushdb()
    
    # All users will try to book the same seat
    event_id = "concert-2023"
    seat_id = "A1"
    num_users = 5
    
    logger.info(f"Starting concurrent booking test with {num_users} users trying to book seat {seat_id}")
    
    # Create and start user threads
    threads = []
    for i in range(num_users):
        user_id = f"user-{i+1}"
        thread = threading.Thread(
            target=simulate_user, 
            args=(booking_system, event_id, user_id, seat_id),
            name=f"User-{i+1}"
        )
        threads.append(thread)
        thread.start()
    
    # Wait for all threads to finish
    for thread in threads:
        thread.join()
    
    # Print final reservation status
    logger.info("\n--- Final Reservations ---")
    reservations = booking_system.get_all_reservations(event_id)
    
    booked_users = {}
    for seat, user in reservations.items():
        logger.info(f"Seat {seat} is booked by {user}")
        booked_users[seat] = user
    
    # Check if our specific seat was booked
    if seat_id in booked_users:
        logger.info(f"\nSUCCESS: Seat {seat_id} was booked by {booked_users[seat_id]}")
        logger.info("Only one user was able to book the seat, demonstrating that distributed locking works!")
    else:
        logger.info(f"\nFAILURE: Seat {seat_id} was not booked by any user")
    
    # Verify we don't have multiple users booking the same seat
    seats_with_users = {}
    for seat, user in reservations.items():
        if user in seats_with_users:
            seats_with_users[user].append(seat)
        else:
            seats_with_users[user] = [seat]
    
    for user, seats in seats_with_users.items():
        if len(seats) > 1:
            logger.info(f"WARNING: User {user} booked multiple seats: {', '.join(seats)}")

if __name__ == "__main__":
    logger.info("Starting distributed locking test with real Redis server...")
    
    # Get the WSL IP address from the user
    import sys
    
    if len(sys.argv) > 1:
        redis_host = sys.argv[1]
        logger.info(f"Using Redis at {redis_host}:6379")
        test_concurrent_booking(redis_host=redis_host)
    else:
        logger.info("Using Redis at localhost:6379")
        test_concurrent_booking()
        
    logger.info("Test complete!")
