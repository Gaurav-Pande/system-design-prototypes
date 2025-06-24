import time
class InventoryService:
    def __init__(self):
        self.inventory = {'burger':5, 'fries':10, 'drink':8, 'pizza':3}
        self.pending_transactions = {}

    def prepare(self, transaction_id, order_details):
        """
        Phase 1 (Prepare):
        Check if the requested item is available and reserve it for the transaction.
        No permanent change is made yet; the reservation is tracked in pending_transactions.
        """
        print(f"InventoryService: Preparing transaction {transaction_id} with order details: {order_details}")
        item = order_details.get('item')
        if item in self.inventory and self.inventory[item] > order_details.get('quantity', 0):
            # Reserve the item (atomic reservation, not yet committed)
            self.inventory[item] -= order_details.get('quantity', 0)
            self.pending_transactions[transaction_id] = {'item': item}
            print(f"InventoryService: Transaction {transaction_id} prepared successfully.")
            return True
        else:
            print(f"InventoryService: Transaction {transaction_id} failed: Item {item} not available.")
            return False

    def commit(self, transaction_id):
        """
        Phase 2 (Commit):
        Make the reservation permanent by removing the transaction from pending_transactions.
        """
        if transaction_id in self.pending_transactions:
            time.sleep(1)
            del self.pending_transactions[transaction_id]
            print(f"InventoryService: Transaction {transaction_id} committed successfully.")
        else:
            print(f"InventoryService: Transaction {transaction_id} not found for commit.")

    def abort(self, transaction_id):
        """
        Phase 2 (Abort):
        Roll back the reservation and restore the inventory if the transaction is aborted.
        """
        if transaction_id in self.pending_transactions:
            time.sleep(1)
            item = self.pending_transactions[transaction_id]['item']
            self.inventory[item] += 1
            del self.pending_transactions[transaction_id]
            print(f"InventoryService: Transaction {transaction_id} aborted successfully.")
        else:
            print(f"InventoryService: Transaction {transaction_id} not found for abort.")

    def get_inventory(self):
        return self.inventory.copy()
