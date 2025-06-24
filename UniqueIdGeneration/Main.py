from IdGenerator import IdGenerator
from BlogService import BlogService
import time

class Main:
    def __init__(self):
        # Initialize the ID generator with a worker ID (0-31)
        self.id_generator = IdGenerator(worker_id=1)
        
        # Initialize the blog service with 4 shards
        self.blog_service = BlogService(num_shards=4, id_generator=self.id_generator)

    def run(self):
        # Create some blog posts
        user_id = 12345
        post1 = self.blog_service.create_post(user_id, "Hello, this is my first blog post!")
        time.sleep(0.1)  # Simulate some delay
        post2 = self.blog_service.create_post(user_id, "This is my second blog post!")

        # Retrieve the posts
        self.blog_service.get_post(user_id, post1['post_id'])
        self.blog_service.get_post(user_id, post2['post_id'])

        # user on the same shard
        user_id2 = 12349  # This user will be on the same shard as user_id 12345
        post3 = self.blog_service.create_post(user_id2, "User 12349's first blog post!")
        self.blog_service.get_post(user_id2, post3['post_id'])

        print("--- Final Shard States ---")
        for i, shard in enumerate(self.blog_service.shards):
            print(f"Shard {i}: {shard}")

if __name__ == "__main__":
    main = Main()
    main.run()