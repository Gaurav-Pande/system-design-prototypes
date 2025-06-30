import hashlib
import bisect

class ConsistentHashRing:
    """
    ConsistentHashRing implements consistent hashing with virtual nodes for sharding.

    Pseudocode/Algorithm:
    ---------------------
    - __init__(num_replicas):
        Initialize the ring, sorted list, and server set. num_replicas is the number of virtual nodes per server.
    - _hash(key):
        Hash the key using MD5 and return as integer.
    - add_server(server_id):
        For each virtual node, hash its key, add to ring and sorted list.
    - remove_server(server_id):
        For each virtual node, remove from ring and sorted list.
    - get_server(key):
        Hash the key, use bisect to find the next node clockwise in sorted_keys. Wrap around if needed. Return the server.
    - distribute_keys(keys):
        For each key, find its server and group keys by server.

        PSEUDOCODE:
        Class ConsistentHashRing:
            Method __init__(num_replicas = 3):
                Set self.num_replicas = num_replicas
                Set self.ring = empty dictionary  // maps hash value to server id
                Set self.sorted_keys = empty list // sorted list of all hash values (positions on the ring)
                Set self.servers = empty set      // set of server ids

            Method _hash(key):
                Convert key to string and encode as utf-8
                Compute MD5 hash of the encoded key
                Convert the hash to an integer and return it

            Method add_server(server_id):
                Add server_id to self.servers
                For i from 0 to self.num_replicas - 1:
                    virtual_node_key = server_id + "#" + str(i)
                    h = self._hash(virtual_node_key)
                    Set self.ring[h] = server_id
                    Insert h into self.sorted_keys, keeping it sorted

            Method remove_server(server_id):
                Remove server_id from self.servers
                For i from 0 to self.num_replicas - 1:
                    virtual_node_key = server_id + "#" + str(i)
                    h = self._hash(virtual_node_key)
                    If h in self.ring:
                        Delete self.ring[h]
                        Remove h from self.sorted_keys

            Method get_server(key):
                If self.ring is empty:
                    Return None
                h = self._hash(key)
                idx = index in self.sorted_keys where h would fit (using bisect)
                If idx == length of self.sorted_keys:
                    idx = 0  // wrap around the ring
                Return self.ring[self.sorted_keys[idx]]

            Method distribute_keys(keys):
                mapping = dictionary mapping each server in self.servers to an empty list
                For each key in keys:
                    server = self.get_server(key)
                    Append key to mapping[server]
                Return mapping
    This approach ensures minimal data movement when adding/removing servers and balances load using virtual nodes.
    """
    def __init__(self, num_replicas=3):
        """
        num_replicas: Number of virtual nodes per server (for better distribution)
        """
        self.num_replicas = num_replicas
        self.ring = dict()  # hash value -> server id
        self.sorted_keys = []  # sorted list of hash values
        self.servers = set()

    def _hash(self, key):
        """Return a hash value for a given key (as int)."""
        h = hashlib.md5(str(key).encode('utf-8')).hexdigest()
        return int(h, 16)

    def add_server(self, server_id):
        """Add a server and its virtual nodes to the ring."""
        self.servers.add(server_id)
        for i in range(self.num_replicas):
            virtual_node_key = f"{server_id}#{i}"
            h = self._hash(virtual_node_key)
            self.ring[h] = server_id
            bisect.insort(self.sorted_keys, h)

    def remove_server(self, server_id):
        """Remove a server and its virtual nodes from the ring."""
        self.servers.discard(server_id)
        for i in range(self.num_replicas):
            virtual_node_key = f"{server_id}#{i}"
            h = self._hash(virtual_node_key)
            if h in self.ring:
                del self.ring[h]
                self.sorted_keys.remove(h)

    def get_server(self, key):
        """Get the server responsible for a given key."""
        if not self.ring:
            return None
        h = self._hash(key)
        idx = bisect.bisect(self.sorted_keys, h) % len(self.sorted_keys)
        return self.ring[self.sorted_keys[idx]]

    def distribute_keys(self, keys):
        """Return a mapping of server_id -> list of keys assigned to it."""
        mapping = {s: [] for s in self.servers}
        for key in keys:
            server = self.get_server(key)
            mapping[server].append(key)
        return mapping
