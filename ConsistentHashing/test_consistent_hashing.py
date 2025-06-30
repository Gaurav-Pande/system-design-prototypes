import matplotlib
matplotlib.use('Agg')
from ConsistentHashRing import ConsistentHashRing
import random
import matplotlib.pyplot as plt
import numpy as np

def plot_distribution(mapping, title):
    """Generates and saves a histogram of key distribution across shards."""
    shard_loads = [len(keys) for keys in mapping.values()]
    
    plt.figure(figsize=(12, 6))
    plt.hist(shard_loads, bins=50, edgecolor='black')
    plt.title(title)
    plt.xlabel("Number of Keys on a Shard")
    plt.ylabel("Number of Shards")
    
    mean_load = np.mean(shard_loads)
    std_dev = np.std(shard_loads)
    plt.axvline(mean_load, color='r', linestyle='dashed', linewidth=2, label=f'Mean: {mean_load:.2f}')
    
    plt.legend()
    plt.grid(True)
    
    filename = title.replace(" ", "_").lower() + ".png"
    plt.savefig(filename)
    print(f"Saved distribution plot to {filename}")
    print(f"Distribution Stats -> Mean: {mean_load:.2f}, Std Dev: {std_dev:.2f}, Min: {np.min(shard_loads)}, Max: {np.max(shard_loads)}\n")

if __name__ == "__main__":
    NUM_SHARDS = 1000
    NUM_REPLICAS = 3 # Virtual nodes per shard
    NUM_KEYS = 10000

    # --- Initial State ---
    ring = ConsistentHashRing(num_replicas=NUM_REPLICAS)
    for i in range(NUM_SHARDS):
        ring.add_server(f"shard-{i}")

    keys = [f"key-{i}" for i in range(NUM_KEYS)]
    initial_mapping = ring.distribute_keys(keys)
    print(f"--- Initial Distribution with {NUM_SHARDS} Shards ---")
    plot_distribution(initial_mapping, f"Initial Distribution of {NUM_KEYS} Keys Across {NUM_SHARDS} Shards")

    # --- After Removing Shards ---
    shards_to_remove = random.sample(list(ring.servers), 50)
    for shard_id in shards_to_remove:
        ring.remove_server(shard_id)
    
    mapping_after_removal = ring.distribute_keys(keys)
    print(f"--- Distribution After Removing {len(shards_to_remove)} Shards ---")
    plot_distribution(mapping_after_removal, f"Distribution After Removing {len(shards_to_remove)} Shards")

    # --- After Adding New Shards ---
    for i in range(NUM_SHARDS, NUM_SHARDS + 50):
        ring.add_server(f"shard-{i}")

    mapping_after_add = ring.distribute_keys(keys)
    print(f"--- Distribution After Adding 50 New Shards ---")
    plot_distribution(mapping_after_add, f"Distribution After Adding 50 New Shards")

    # --- Analyze Key Movement ---
    def get_key_to_shard_map(mapping):
        key_map = {}
        for shard, key_list in mapping.items():
            for key in key_list:
                key_map[key] = shard
        return key_map

    initial_key_map = get_key_to_shard_map(initial_mapping)
    removal_key_map = get_key_to_shard_map(mapping_after_removal)
    add_key_map = get_key_to_shard_map(mapping_after_add)

    moved_on_removal = sum(1 for k in keys if initial_key_map.get(k) != removal_key_map.get(k))
    moved_on_add = sum(1 for k in keys if removal_key_map.get(k) != add_key_map.get(k))

    print("--- Key Movement Analysis ---")
    print(f"Keys moved after removing 50 shards: {moved_on_removal} / {NUM_KEYS} ({moved_on_removal/NUM_KEYS:.2%})")
    print(f"Keys moved after adding 50 new shards: {moved_on_add} / {NUM_KEYS} ({moved_on_add/NUM_KEYS:.2%})")