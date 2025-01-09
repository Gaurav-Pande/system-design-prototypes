# Simple prototyp to show threading in a queue.

import argparse
import threading
import time
import random
class NonThreadSafeQueue:
    def __init__(self):
        self.queue = []

    def enqueue(self, item):   
        time.sleep(random.uniform(0, 0.001))
        self.queue.append(item)
    
    def dequeue(self):
        if self.queue:
            return self.queue.pop(0)
        return None
    
class ThreadSafeQueue:
    def __init__(self):
        self.queue = []
        self.lock = threading.Lock()    
        
    def threadSafeEnqueue(self, item):
        with self.lock:
            self.queue.append(item)
    
    def threadSafeDequeue(self):
        with self.lock:
            if self.queue:
                return self.queue.pop(0)
        return None



def main():
    # from command line get the args 
    parser = argparse.ArgumentParser(description="Simple thread safety prototype")
    parser.add_argument('-t', '--threadSafe', type=bool, default=False,
                        help='Flag to turn on/off the thread safety (default: False)')
    # Choose queue type based on argument
    args = parser.parse_args()
    queue_class = ThreadSafeQueue if args.threadSafe else NonThreadSafeQueue
    q = queue_class()

    threads = []
    for i in range(100000):
        thread = threading.Thread(target=q.enqueue, args=(i,))
        thread.start()
        threads.append(thread)

    # Wait for all threads to complete
    for thread in threads:
        thread.join()

    print(f"Queue size: {len(q.queue)}")
    print(f"Queue type: {'Thread-Safe' if args.threadSafe else 'Non-Thread-Safe'}")


if __name__ == "__main__":
    main()