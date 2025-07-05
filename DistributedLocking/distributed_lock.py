import redis
import time
import uuid
import random

class DistributedLock:
    """
    A distributed lock implementation using Redis.
    
    This class provides a way to acquire exclusive access to a resource across 
    multiple processes or servers. It uses Redis as the centralized lock manager.
    """
    
    def __init__(self, redis_client, lock_name, expire_time=10):
        """
        Initialize the distributed lock.
        
        Args:
            redis_client: A Redis client instance
            lock_name: A unique name for the lock
            expire_time: Time in seconds after which the lock will automatically expire
        """
        self.redis = redis_client
        self.lock_name = lock_name
        self.expire_time = expire_time
        self.lock_value = str(uuid.uuid4())  # Unique identifier for this lock instance
    
    def acquire(self, retry_times=3, retry_delay=0.2):
        """
        Attempt to acquire the lock.
        
        Args:
            retry_times: Number of times to retry if lock acquisition fails
            retry_delay: Delay between retries in seconds
            
        Returns:
            bool: True if the lock was acquired, False otherwise
        """
        for i in range(retry_times):
            # Use SETNX (SET if Not eXists) to ensure atomicity
            if self.redis.setnx(self.lock_name, self.lock_value):
                # Set expiration to prevent deadlocks if the client crashes
                self.redis.expire(self.lock_name, self.expire_time)
                return True
                
            # If we couldn't acquire the lock, wait and retry
            if i < retry_times - 1:
                time.sleep(retry_delay * (random.random() + 0.5))  # Add jitter to avoid thundering herd
                
        return False
    
    def release(self):
        """
        Release the lock.
        
        This will only release the lock if it's currently held by this instance.
        This prevents accidentally releasing a lock acquired by another process
        after the current lock expired.
        
        Returns:
            bool: True if the lock was released, False otherwise
        """
        # Use a Lua script to ensure atomicity of the check-and-delete operation
        script = """
        if redis.call('get', KEYS[1]) == ARGV[1] then
            return redis.call('del', KEYS[1])
        else
            return 0
        end
        """
        result = self.redis.eval(script, 1, self.lock_name, self.lock_value)
        return result == 1
    
    def __enter__(self):
        """Support for using the lock as a context manager with 'with' statement."""
        acquired = self.acquire()
        if not acquired:
            raise TimeoutError(f"Could not acquire lock on {self.lock_name}")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Release the lock when exiting the context manager."""
        self.release()
