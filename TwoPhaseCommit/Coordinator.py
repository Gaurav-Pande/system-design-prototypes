import uuid


class Coordinator:
    def __init__(self, participants):
        self.participants = participants

    def execute_transaction(self, order_details):
        """
        Orchestrates a distributed transaction using the two-phase commit protocol.

        This method ensures that a transaction across multiple services (participants) is atomic:
        - Either all services commit the transaction, or all abort (no partial updates).
        - This is crucial for maintaining data consistency in distributed systems.
        """
        transaction_id = str(uuid.uuid4())
        print(f"Coordinator: Starting transaction {transaction_id} with order details: {order_details}")

        # --- Phase 1: Prepare ---
        # The coordinator asks each participant to prepare for the transaction.
        # Each participant checks if it can perform the requested operation and reserves resources.
        # No permanent changes are made yet (atomicity is preserved).
        prepared_participants = []
        can_commit = True
        for participant in self.participants:
            if participant.prepare(transaction_id, order_details):
                prepared_participants.append(participant)
            else:
                can_commit = False
                print(f"Coordinator: Participant {participant.__class__.__name__} failed to prepare transaction {transaction_id}. Aborting transaction.")
                break

        # --- Phase 2: Commit or Abort ---
        # If all participants are prepared, coordinator sends 'commit' to all (atomic commit).
        # If any participant failed, coordinator sends 'abort' to all that prepared (atomic abort).
        if can_commit:
            print(f"Coordinator: All participants prepared successfully for transaction {transaction_id}. Committing transaction.")
            for participant in prepared_participants:
                participant.commit(transaction_id)
            print(f"Coordinator: Transaction {transaction_id} committed successfully.")
            return True
        else:
            print(f"Coordinator: Aborting transaction {transaction_id}.")
            for participant in prepared_participants:
                participant.abort(transaction_id)
            print(f"Coordinator: Transaction {transaction_id} aborted successfully.")
            return False