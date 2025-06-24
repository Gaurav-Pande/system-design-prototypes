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


## Unique ID Generation in Distributed Systems
In a distributed system with sharded databases, generating unique primary keys is a critical challenge. Traditional auto-incrementing IDs from a single database are no longer viable, as each shard would generate overlapping sequences, leading to ID collisions.

### The Challenge: Monotonically Increasing IDs vs. High Throughput
It is practically impossible to generate strictly, mathematically, monotonically increasing IDs (e.g., 1, 2, 3, 4...) with high throughput in a distributed system. This is because:
-   **Single Point of Failure**: A single service generating IDs becomes a bottleneck and a single point of failure.
-   **Coordination Overhead**: Multiple ID generator instances would need to coordinate to avoid collisions, and this coordination (e.g., using locks or gossip protocols) kills performance and throughput.

### The "Snowflake" Approach
A common solution is to use a method inspired by Twitter's Snowflake algorithm, which generates roughly time-sortable, globally unique IDs without requiring coordination between generator instances.

The ID is a 64-bit number composed of:
1.  **Timestamp (41 bits)**: The number of milliseconds since a custom epoch. Placing this in the most significant bits makes the IDs sortable by time, which is excellent for database indexing.
2.  **Worker ID (5 bits)**: A unique ID for each generator instance. This allows up to 32 different generator nodes to operate independently, ensuring uniqueness without coordination.
3.  **Sequence Number (12 bits)**: An intra-millisecond counter. This allows a single worker to generate up to 4096 unique IDs within the same millisecond, preventing collisions during high-traffic bursts.

#### ID Composition (Bitwise Operations)
The final ID is assembled using bitwise operations to pack the three components into a single 64-bit integer. This is done with the following logic:

`new_id = (timestamp << 17) | (worker_id << 12) | sequence`

-   `<<` (Bitwise Left Shift): This operator moves the bits of a number to the left, making space for the other components.
-   `|` (Bitwise OR): This operator combines the shifted components into the final ID.

Here is the visual layout of the 64-bit ID:

```
[63, ..., 58] [57, ..., 17]   [16, ..., 12]    [11, ..., 0]
+-------------+-----------------+------------------+-----------------+
| Unused (6)  |  Timestamp (41) |  Worker ID (5)   |  Sequence (12)  |
+-------------+-----------------+------------------+-----------------+
```

-   **Sequence (Bits 0-11)**: Occupies the first 12 bits.
-   **Worker ID (Bits 12-16)**: Shifted left by 12 to be placed next to the sequence.
-   **Timestamp (Bits 17-57)**: Shifted left by 17 (12 + 5) to be placed next to the worker ID.

### Snowflake IDs vs. UUIDs for Database Performance
| Feature | UUID (v4) | Snowflake-style ID |
| :--- | :--- | :--- |
| **Uniqueness** | Excellent | Excellent |
| **Size** | 128 bits (16 bytes) | 64 bits (8 bytes) |
| **Ordering** | Random | Time-sortable |
| **DB Performance** | **Poor**. Random nature causes severe index fragmentation and slow writes. | **Excellent**. Sequential nature leads to fast appends and efficient indexing. |

UUIDs are a poor choice for primary keys in high-throughput databases with B+ tree indexes (like MySQL's InnoDB) because their random nature leads to constant, expensive page splits and index bloat. Time-sortable Snowflake IDs are inserted sequentially, which is much more efficient.

### Prototype
A simple blogging application that demonstrates how to generate unique IDs in a sharded environment.
-   **IdGenerator**: A service that generates unique, 64-bit, time-sortable IDs.
-   **BlogService**: Simulates a sharded database where blog posts are stored based on `user_id`. It uses the `IdGenerator` to assign a unique ID to each new post.

