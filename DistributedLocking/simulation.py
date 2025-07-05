import threading
import time
import random
from ticket_booking import TicketBookingSystem

def simulate_user(booking_system, event_id, user_id, num_attempts=3):
    """
    Simulate a user trying to book a random seat.
    
    Args:
        booking_system: The TicketBookingSystem instance
        event_id: ID of the event
        user_id: ID of the user
        num_attempts: Number of booking attempts to make
    """
    for attempt in range(num_attempts):
        # Choose a random seat (1-50)
        seat_id = random.randint(1, 50)
        
        print(f"User {user_id} is trying to book seat {seat_id} at event {event_id}")
        
        # Try to book the seat
        success = booking_system.try_reserve_seat(event_id, seat_id, user_id)
        
        if success:
            # 30% chance to cancel the booking
            if random.random() < 0.3:
                time.sleep(random.uniform(0.1, 1.0))
                booking_system.cancel_reservation(event_id, seat_id, user_id)
            break
        
        # Wait a bit before trying again
        time.sleep(random.uniform(0.2, 0.7))

def run_simulation(num_users=20, event_id="concert-2023"):
    """
    Run a simulation with multiple concurrent users trying to book seats.
    
    Args:
        num_users: Number of concurrent users
        event_id: ID of the event
    """
    # Create a ticket booking system
    # Note: This assumes Redis is running on localhost:6379
    booking_system = TicketBookingSystem()
    
    # Create and start user threads
    threads = []
    for i in range(num_users):
        user_id = f"user-{i+1}"
        thread = threading.Thread(target=simulate_user, 
                                 args=(booking_system, event_id, user_id))
        threads.append(thread)
        thread.start()
    
    # Wait for all threads to finish
    for thread in threads:
        thread.join()
    
    # Print final reservation status
    print("\n--- Final Reservations ---")
    reservations = booking_system.get_all_reservations(event_id)
    for seat_id, user_id in reservations.items():
        print(f"Seat {seat_id} is booked by {user_id}")
    
    print(f"\nTotal seats booked: {len(reservations)}")

if __name__ == "__main__":
    print("Starting ticket booking simulation...")
    run_simulation()
    print("Simulation complete!")
