from app import app
from fake_data.posts import post_data

# Define a route
@app.route("/")
def index():
    first_name = 'Brian'
    age = 55
    return 'Hello ' + first_name + ' who is ' + str(age) + ' years old'


# Post endpoints

# get all posts
@app.route('/posts')
def get_posts():
    # get the posts from storage (fake data -> tomorrow will be db)
    posts = post_data
    return posts

# Get a single post by ID
@app.route('/posts/<int:post_id>')
def get_post(post_id):
    # get the posts from storage
    posts = post_data
    # for each dictionary in the list of post dictionaries
    for post in posts:
        #if the key of 'id' matches the post_id from the url
        if post['id'] == post_id:
            #return that post dictionary
            return post
    # If we loop throuigh all of thge posts without reeturning, the post with that ID does not exist
    return {'error': f"Post with an ID of {post_id} does not exist"}, 404