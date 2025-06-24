from Coordinator import Coordinator
from DeliveryService import DeliveryService
from InventoryService import InventoryService

def main():
    # Initialize services
    inventory_service = InventoryService()
    delivery_service = DeliveryService()

    # Create coordinator with the services as participants
    coordinator = Coordinator([inventory_service, delivery_service])

    # Example order details
    order_details = {
        'item': 'burger',
        'quantity': 1,
        'delivery_address': '123 Main St'
    }

    # Execute successful transaction
    print("Executing successful transaction...")
    coordinator.execute_transaction(order_details)
    print("\nCurrent Inventory:", inventory_service.get_inventory())
    print("Current Delivery Status:", delivery_service.delivery_person)
    print("\n")

    # Example order details for a failed transaction
    order_details_failed = {
        'item': 'pizza',  
        'quantity': 5, # we only have 3 pizzas in stock
        'delivery_address': '456 Elm St'
    }

    # Execute failed transaction
    print("Executing failed transaction...\n")
    coordinator.execute_transaction(order_details_failed)
    print("\nCurrent Inventory:", inventory_service.get_inventory())
    
    print("Current Delivery Status:", delivery_service.delivery_person)
    print("\n")

    # example successful transaction with available delivery person
    order_details_successful = {
        'item': 'drink',
        'quantity': 2,
        'delivery_address': '321 Pine St'
    }
    print("Executing successful transaction with available delivery person...\n")
    coordinator.execute_transaction(order_details_successful)
    print("\nCurrent Inventory:", inventory_service.get_inventory())
    print("Current Delivery Status:", delivery_service.delivery_person)
    print("\n") 

    # Example order details when no delivery person is available
    order_details_no_delivery = {
        'item': 'fries',
        'quantity': 2,
        'delivery_address': '789 Oak St'
    }

    # Execute transaction with no delivery person available
    print("Executing transaction with no delivery person available...\n")
    coordinator.execute_transaction(order_details_no_delivery)
    print("\nCurrent Inventory:", inventory_service.get_inventory())
    print("Current Delivery Status:", delivery_service.delivery_person)
    print("\n")

if __name__ == "__main__":
    main()
# This code simulates a two-phase commit protocol with an inventory service and a delivery service.