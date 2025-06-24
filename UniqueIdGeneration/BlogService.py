from IdGenerator import IdGenerator

class BlogService:
    def __init__(self, num_shards, id_generator):
        """
        Initializes the BlogService.
        :param num_shards: The number of database shards to simulate.
        :param id_generator: An instance of the IdGenerator to create unique post IDs.
        """
        self.num_shards = num_shards
        self.shards = [{} for _ in range(num_shards)]
        self.id_generator = id_generator

    def get_shard(self, user_id):
        """
        Determines which shard to use for a given user_id.
        This is a simple modulo-based sharding strategy.
        """
        shard_index = user_id % self.num_shards
        return self.shards[shard_index]

    def create_post(self, user_id, content):
        """
        Creates a new blog post.
        It uses the IdGenerator to get a unique ID and then places the post
        in the correct shard based on the user_id.
        """
        post_id = self.id_generator.generate_id()
        shard = self.get_shard(user_id)
        
        post = {
            'id': post_id,
            'user_id': user_id,
            'content': content
        }
        shard[post_id] = post
        print(f"Created post {post_id} for user {user_id} on shard {user_id % self.num_shards}")
        return post

    def get_post(self, user_id, post_id):
        """
        Retrieves a blog post.
        It first determines the correct shard from the user_id and then looks up the post.
        """
        shard = self.get_shard(user_id)
        return shard.get(post_id)