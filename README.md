NOTE- Under developement

# system-design-prototypes
Some fun prototypes while learning system design

## Multi Threading

## BlockingQueues

## WebSockets
### Using Client/Server
### Send a request to websocket over TCP connection from powershell

```
$tcpClient = New-Object System.Net.Sockets.TcpClient("localhost", 3000)
$networkStream = $tcpClient.GetStream()
```

Send headers directly

```
$headers = [System.Text.Encoding]::ASCII.GetBytes(@"
GET / HTTP/1.1
Host: localhost:3000
Upgrade: websocket
Connection: Upgrade
WebSocket-Key: dGhlIHNhbXBsZSBub25jZQ==
WebSocket-Version: 13
"@)

$networkStream.Write($headers, 0, $headers.Length)
$networkStream.Flush()
```


## RealTimeChats


## Two-Phase Commit
A distributed transaction protocol that ensures all participating services either commit or abort a transaction, providing atomicity.

**Why is it needed?**
In a distributed system, a single business transaction might require updating data across multiple services or databases. For example, an e-commerce order might need to update the inventory service, the payment service, and the shipping service. If one of these updates fails, we need a way to roll back the changes in the other services to maintain data consistency. Without a protocol like 2PC, the system could be left in an inconsistent state (e.g., payment taken, but inventory not updated).

**When to use it?**
Two-phase commit is used when you need to guarantee atomicity for a transaction that spans multiple resource managers (like databases or services). It's essential in systems where data integrity is paramount, such as financial systems, e-commerce platforms, and booking systems. However, 2PC is a blocking protocol, which means it can hold locks on resources while waiting for all participants to be ready. This can impact system performance and availability. Therefore, it should be used in situations where the need for strong consistency outweighs the potential performance overhead. Alternatives like Sagas are often considered for less critical transactions or when higher availability is required.

### Prototype
A food delivery system prototype demonstrating the two-phase commit protocol. The system consists of an `InventoryService`, a `DeliveryService`, and a `Coordinator`.

**How it works:**
The `Coordinator` orchestrates the transaction across the `InventoryService` and `DeliveryService`. When an order is placed, the `Coordinator` initiates the two-phase commit protocol:
1.  **Phase 1: Prepare**: The `Coordinator` asks both the `InventoryService` and `DeliveryService` to prepare for the transaction.
    *   The `InventoryService` checks if the food item is available and reserves it.
    *   The `DeliveryService` checks if a delivery person is available and reserves them.
    *   If both services can prepare successfully, they are in a "prepared" state, ready to commit.
2.  **Phase 2: Commit or Abort**:
    *   If both services are prepared, the `Coordinator` sends a "commit" message to both. The services then make their changes permanent.
    *   If either service fails to prepare, the `Coordinator` sends an "abort" message to both. The services then roll back any changes they made during the prepare phase.

This ensures that the order is either fully processed (food and delivery secured) or not at all, maintaining consistency across the system.

-   **InventoryService**: Manages the availability of food items.
-   **DeliveryService**: Manages the availability of delivery personnel.
-   **Coordinator**: Orchestrates the two-phase commit across the `InventoryService` and `DeliveryService`.

The prototype simulates successful and failed transactions to illustrate how the two-phase commit protocol maintains data consistency across distributed services.

