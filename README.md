# System Design Prototypes

A collection of hands-on prototypes designed to build a strong intuition for key system design concepts. Each section provides a technical overview, discusses the motivation and trade-offs, and includes a practical prototype to demonstrate the principles in action.

---

## Table of Contents
- [Multi-Threading](#multi-threading)
- [Blocking Queues](#blocking-queues)
- [WebSockets](#websockets)
- [Real-Time Chat](#real-time-chat)
- [Two-Phase Commit (2PC) for Distributed Transactions](#two-phase-commit-2pc-for-distributed-transactions)
- [Unique ID Generation in Distributed Systems](#unique-id-generation-in-distributed-systems)
- [Content Delivery Network (CDN)](#content-delivery-network-cdn)
- [Consistent Hashing for Sharding](#consistent-hashing-for-sharding)

---

## Multi-Threading

**Concept:**
Multi-threading is a model of execution that allows a single process to manage multiple independent threads of execution concurrently. Each thread shares the process's resources (like memory space) but runs on its own execution path. This is essential for improving the throughput and responsiveness of applications, especially for I/O-bound or parallelizable CPU-bound tasks.

**Motivation:**
- **Concurrency:** To perform multiple operations at the same time, such as handling multiple client requests simultaneously in a web server.
- **Responsiveness:** To keep an application responsive to user input while performing long-running tasks in the background (e.g., a UI thread remains active while a worker thread processes data).
- **Performance:** To leverage multi-core processors by splitting a task into parallel sub-tasks that can be executed simultaneously.

**Prototype:**
The `Threading/` directory contains scripts demonstrating both `MultiThreading` and `MultiProcessing` in Python. The prototype code illustrates how to spawn threads/processes and manage their execution, providing a clear comparison of their use cases and performance characteristics.

---

## Blocking Queues

**Concept:**
A blocking queue is a thread-safe data structure that enforces limits on its capacity. It is a fundamental building block for concurrent programming, particularly for solving producer-consumer problems.
- If a **producer** thread tries to add an item to a full queue, it is blocked (paused) until a consumer removes an item.
- If a **consumer** thread tries to remove an item from an empty queue, it is blocked until a producer adds an item.

**Motivation:**
- **Resource Management:** Prevents producers from overwhelming consumers and exhausting memory by creating a bounded buffer for tasks.
- **Synchronization:** Simplifies coordination between different threads or stages in a pipeline, as the queue itself handles the waiting and notification logic.
- **Backpressure:** Naturally creates backpressure, signaling to the producing system to slow down when the consuming system cannot keep up.

**Prototype:**
The `BlockingQueue.py` script implements a simple blocking queue. The prototype demonstrates how `put` and `get` operations can be synchronized to safely manage task distribution between producer and consumer threads.

---

## WebSockets

**Concept:**
The WebSocket protocol (RFC 6455) provides a **full-duplex communication channel** over a single, long-lived TCP connection. Unlike the traditional HTTP request-response model, WebSockets allow the server and client to send messages to each other independently and at any time after an initial handshake.

**Motivation:**
- **Real-Time Communication:** Essential for applications requiring low-latency, bidirectional updates, such as live financial dashboards, multiplayer games, and collaborative editing tools.
- **Efficiency:** Reduces the overhead of establishing new HTTP connections for frequent updates. The persistent connection eliminates the need for repeated TCP handshakes and HTTP headers, saving bandwidth and reducing latency.

**Prototype:**
The `WebSockets/` directory contains a `Server.py` and `Client.py`. The prototype establishes a WebSocket connection and demonstrates the real-time, two-way message flow between the server and client.

---

## Real-Time Chat

**Concept:**
A real-time chat application is a classic use case for WebSockets. It enables multiple users to join a chat room and exchange messages instantly, with the server broadcasting incoming messages to all connected clients.

**Motivation:**
This prototype serves as a practical, multi-user application of the WebSocket protocol, demonstrating how a central server can manage connections from numerous clients and facilitate real-time data broadcasting.

**Prototype:**
The `RealTimeChat/` directory contains a simple chat application built with Flask. It showcases how to manage multiple client connections and broadcast messages to create an interactive, multi-user experience.

---

## Two-Phase Commit (2PC) for Distributed Transactions

**Concept:**
Two-Phase Commit is a distributed algorithm that ensures **atomicity** for transactions spanning multiple independent services or databases. It guarantees that all participants in a transaction either all commit their changes or all abort, preventing data inconsistencies in a distributed system.

**Motivation:**
In microservices architectures, a single business operation (e.g., placing an order) may require state changes in multiple services (e.g., `InventoryService` and `DeliveryService`). If one service fails after another has already committed its change, the system is left in an inconsistent state. 2PC solves this by coordinating the transaction in two phases.

**Phases & Diagram:**
1.  **Phase 1: Prepare Phase:** The `Coordinator` asks all `Participants` if they are ready to commit. Each participant checks its resources, locks the necessary records, and votes "Yes" or "No."
2.  **Phase 2: Commit/Abort Phase:**
    *   If all participants vote "Yes," the Coordinator instructs them all to `commit`.
    *   If any participant votes "No" or fails to respond, the Coordinator instructs them all to `abort` (roll back).

```
+-----------+        +-------------------+        +-------------------+
|  Client   |<-----> |   Coordinator     |<-----> |  Participants     |
+-----------+        +-------------------+        +-------------------+
     |                      |                           |
     | 1. Start Txn         |                           |
     |--------------------->|                           |
     |                      | 2. Prepare?               |
     |                      |-------------------------->|
     |                      |<--------------------------|
     |                      | 3. All Ready? (Vote)      |
     |                      | 4. Commit/Abort           |
     |                      |-------------------------->|
     |                      |<--------------------------|
     | 5. Result            |                           |
     |<---------------------|                           |
```

**Prototype:**
The `TwoPhaseCommit/` prototype simulates a food delivery transaction involving an `InventoryService` and a `DeliveryService`, orchestrated by a `Coordinator`.

**Testing:**
The test demonstrates that the overall transaction succeeds only if both services can successfully prepare and commit their local transactions. If either service fails, the entire operation is aborted.

---

## Unique ID Generation in Distributed Systems

**Concept:**
In a distributed system with multiple database shards or worker nodes, using traditional auto-incrementing primary keys is not feasible, as it would lead to ID collisions. A distributed ID generation scheme is required to produce unique, sortable identifiers across the entire system.

**Motivation:**
- **Uniqueness:** IDs must be unique across all nodes to serve as primary keys.
- **Sortability:** Time-sortable IDs (like Twitter's Snowflake) are highly desirable because they improve database index performance. New records are inserted sequentially, which is much more efficient for B-Tree indexes than inserting random UUIDs that cause page splits and fragmentation.

**Snowflake ID Architecture:**
A Snowflake ID is a 64-bit integer composed of:
- **Timestamp (41 bits):** Milliseconds since a custom epoch. Ensures IDs are roughly time-sortable.
- **Worker ID (5 bits):** Uniquely identifies the node that generated the ID (allowing for 2^5 = 32 nodes).
- **Sequence (12 bits):** A counter that increments for each ID generated within the same millisecond on the same node (allowing for 2^12 = 4096 IDs per ms per node).

```
[63, ..., 58] [57, ..., 17]   [16, ..., 12]    [11, ..., 0]
+-------------+-----------------+------------------+-----------------+
| Unused (6)  |  Timestamp (41) |  Worker ID (5)   |  Sequence (12)  |
+-------------+-----------------+------------------+-----------------+
```

**Prototype:**
The `UniqueIdGeneration/` prototype implements a `IdGenerator` based on the Snowflake design. A `BlogService` uses this generator to create unique IDs for new posts, simulating a sharded application.

---

## Content Delivery Network (CDN)

**Concept:**
A Content Delivery Network (CDN) is a geographically distributed network of proxy servers designed to provide high availability and performance by caching content closer to end-users. When a user requests content, the request is routed to the nearest CDN server (or "edge location"), which can serve the content directly from its cache if available.

**Motivation:**
- **Reduced Latency:** Serving content from a nearby edge server is significantly faster than fetching it from a distant origin server.
- **Reduced Origin Load:** By handling requests at the edge, CDNs reduce the traffic and processing load on the origin server, improving its scalability and availability.
- **High Availability:** The distributed nature of a CDN provides resilience against network congestion and server outages.

**Request Flow:**
```
+--------+        +-----------------+        +---------------+
|  User  | <----> | CDN Edge Server | <----> | Origin Server |
+--------+        +-----------------+        +---------------+
     |                |                    |
     | 1. Request     |                    |
     |--------------->|                    |
     |                | 2. Cache Hit?      |
     |                |    (If not, go to 3)|
     | 2a. Serve from Cache |              |
     |<---------------|                    |
     |                | 3. Cache Miss ->   |
     |                |    Forward Request |
     |                |------------------->|
     |                | 4. Fetch & Cache   |
     |                |<-------------------|
     | 5. Serve to User|                    |
     |<---------------|                    |
```

**Prototype:**
The `SimpleCDN/` prototype is a basic caching proxy server. It sits between the user and an origin server (`arpitbhayani.me`). It demonstrates the core caching logic: serving from its local cache on a "hit" and fetching from the origin on a "miss."

---

## Consistent Hashing for Sharding

**Concept:**
Consistent hashing is a special kind of hashing that minimizes the number of keys that need to be remapped when the number of hash buckets (e.g., servers or shards) changes. It maps both servers and data keys onto a circular hash space (a "ring"). A key is assigned to the first server found by moving clockwise from the key's position on the ring.

**Motivation:**
In large-scale distributed systems, servers are frequently added or removed.
- **Problem with Modulo Hashing:** Using a simple `hash(key) % N` formula for sharding is brittle. If `N` (the number of servers) changes, nearly all keys will map to a new server, triggering a massive, system-wide data reshuffle that can be catastrophic for performance and availability.
- **Consistent Hashing Solution:** When a server is added or removed, only the keys that immediately precede it on the ring are affected. This ensures that only a small fraction of data (`1/N`) needs to be moved, making scaling operations smooth and efficient.

**Visualizing the Distribution**
To demonstrate its effectiveness, a simulation was run with 1,000 shards and 10,000 keys. The `test_consistent_hashing.py` script measures the impact of adding and removing shards.

1.  **Initial Distribution**: The keys are distributed across the 1,000 shards. Due to the nature of hashing, the distribution is not perfectly uniform but is statistically balanced.

    ![Initial Distribution](ConsistentHashing/images/initial_distribution_of_10000_keys_across_1000_shards.png)

2.  **Removing 50 Shards**: When 50 shards (5% of the total) are removed, only **4.95%** of the keys need to be remapped. This is a stark contrast to a modulo-based approach, which would have required nearly 100% of keys to be moved.

    ![Distribution After Removing Shards](ConsistentHashing/images/distribution_after_removing_50_shards.png)

3.  **Adding 50 New Shards**: Similarly, when 50 new shards are added, only **4.55%** of the keys are moved to populate the new shards.

    ![Distribution After Adding Shards](ConsistentHashing/images/distribution_after_adding_50_new_shards.png)

**Conclusion:**
The results clearly validate the primary benefit of consistent hashing: it provides a stable and scalable method for distributing data in a dynamic environment, minimizing disruption during scaling events.

