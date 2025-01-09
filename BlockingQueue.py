import threading
import sys
import argparse
import time

class ExampleBlockingQueue:
    def __init__(self, max_size):
        # define a mutex for locking.
        # define condition for a way to block the thread.
        # define the max capacity.
        self.max_size = max_size
        self.queue = []
        self.condition = threading.Condition()

    def enqueue(self, item):
        # Thread enters the condition.
        with self.condition:
            # block a thread if the queue is full
            while len(self.queue) == self.max_size:
                print(f"Queue is full, waiting..")
                self.condition.wait()
            
            # add element
            self.queue.append(item)
            print(f"Enqueued item to the queue: {item}")

            # notify all waiting threads
            self.condition.notify_all()


    def dequeue(self):
        with self.condition:
            if (len(self.queue)) == 0:
                print(f"Queue is full, waiting..")
                self.condition.wait()
            
            item = self.queue.pop(0)
            print(f"Dequeued item from the queue: {item}")

            self.condition.notify_all()

            return item

    def size(self):
        with self.condition:
            return len(self.queue)
        


class BlockingQueueCli:
    def __init__(self, size):
        self.queue = ExampleBlockingQueue(size)
        self.commands = {
            'enqueue': self.enqueue_cmd,
            'dequeue': self.dequeue_cmd,
            'size': self.size_cmd,
            'peek': self.peek_cmd,
            'exit': self.exit_cmd
        }

    def enqueue_cmd(self, args):
        if not args:
            print(f"Please input the item to add to the queue")

        item = args[0]

        # using thread to not block the queue
        threading.Thread(target=self.queue.enqueue, args=(item,)).start()

    def dequeue_cmd(self, args):
        # Use a thread to perform dequeue to demonstrate non-blocking behavior
        threading.Thread(target=self.queue.dequeue).start()

    def size_cmd(self, args):
        print(f"Current queue size: {self.queue.size()}")

    def peek_cmd(self, args):
        item = self.queue.peek()
        print(f"First item in queue: {item}")

    def exit_cmd(self, args):
        print("Exiting application...")
        sys.exit(0)


    def run(self):
        print("Blocking Queue CLI")
        print("Available commands: enqueue, dequeue, size, peek, exit")
        
        while True:
            try:
                # Get input and split into command and arguments
                user_input = input(">>> ").strip().split()
                
                if not user_input:
                    continue
                
                command = user_input[0].lower()
                args = user_input[1:]

                # Execute command if exists
                if command in self.commands:
                    self.commands[command](args)
                else:
                    print(f"Unknown command: {command}")
                
                # Small delay to allow thread operations to complete
                time.sleep(0.1)

            except KeyboardInterrupt:
                print("\nExiting application...")
                break
            except Exception as e:
                print(f"An error occurred: {e}")

def main():
    parser = argparse.ArgumentParser(description="Blocking Queue CLI")
    parser.add_argument('-s', '--size', type=int, default=5, 
                        help='Maximum size of the blocking queue (default: 5)')
    
    args = parser.parse_args()
    
    cli = BlockingQueueCli(args.size)
    cli.run()

if __name__ == "__main__":
    main()