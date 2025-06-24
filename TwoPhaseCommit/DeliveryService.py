import time
class DeliveryService:
    def __init__(self):
        self.delivery_person= {'John': 'Available',
                               'Jane': 'Available',
                               }
        self.pending_transactions = {}

    def prepare(self, transaction_id, order_details):
        """
        Phase 1 (Prepare):
        Check if a delivery person is available and reserve them for the transaction.
        No permanent change is made yet; the reservation is tracked in pending_transactions.
        """
        print(f"DeliveryService: Preparing delivery for transaction {transaction_id} with order details: {order_details}")
        delivery_person = None
        for person, status in self.delivery_person.items():
            if status == 'Available':
                delivery_person = person
                break

        if delivery_person:
            time.sleep(1)
            # Reserve the delivery person (atomic reservation, not yet committed)
            self.delivery_person[delivery_person] = 'Busy'
            self.pending_transactions[transaction_id] = {'delivery_person': delivery_person}
            print(f"DeliveryService: Transaction {transaction_id} prepared successfully with delivery person {delivery_person}.")
            return True
        else:
            print(f"DeliveryService: Transaction {transaction_id} failed: No available delivery person.")
            return False

    def commit(self, transaction_id):
        """
        Phase 2 (Commit):
        Make the reservation permanent by removing the transaction from pending_transactions.
        """
        if transaction_id in self.pending_transactions:
            time.sleep(1)
            delivery_person = self.pending_transactions[transaction_id]['delivery_person']
            self.delivery_person[delivery_person] = 'Busy'
            del self.pending_transactions[transaction_id]
            print(f"DeliveryService: Transaction {transaction_id} committed successfully with delivery person {delivery_person}.")
        else:
            print(f"DeliveryService: Transaction {transaction_id} not found for commit.")

    def abort(self, transaction_id):
        """
        Phase 2 (Abort):
        Roll back the reservation and make the delivery person available again if the transaction is aborted.
        """
        if transaction_id in self.pending_transactions:
            time.sleep(1)
            delivery_person = self.pending_transactions[transaction_id]['delivery_person']
            self.delivery_person[delivery_person] = 'Available'
            del self.pending_transactions[transaction_id]
            print(f"DeliveryService: Transaction {transaction_id} aborted successfully, delivery person {delivery_person} is now available.")
        else:
            print(f"DeliveryService: Transaction {transaction_id} not found for abort.")