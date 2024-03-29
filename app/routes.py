from flask import request, render_template
from app import app, db
from .models import Comment, User, Post
from .auth import basic_auth, token_auth


# Define a route
@app.route("/")
def index():
    return render_template('index.html')

#User endpoints

#create a  new user

@app.route('/users', methods=['POST'])
def create_user():
    #Check to make sure that the request body is JSON
    if not request.is_json:
        return {'error': 'Your content-type must be application/json'}, 400
    # GET the data from the request body
    data = request.json

    #Validate that the data has all the required fields
    required_fields = ['firstName', 'lastName', 'username', 'email', 'password']
    missing_fields = []
    for field in required_fields:
        if field not in data:
            missing_fields.append(field)
    if missing_fields:
        return {'error': f"{', '.join(missing_fields)} must be in the request body"}, 400
    
    # Pull the individual data from the body
    first_name = data.get('firstName')
    last_name = data.get('lastName')
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    
   # Check to see if any current users already have that username and/or email
    check_users = db.session.execute(db.select(User).where( (User.username == username) | (User.email == email) )).scalars().all()
    if check_users:
        return {'error': "A user with that username and/or email already exists"}, 400 
        
    # Create a new instance of user with the data from the request
    new_user = User(first_name=first_name, last_name=last_name, email=email, password=password, username=username)
    
    return new_user.to_dict(), 201

@app.route('/token')
@basic_auth.login_required
def get_token():
    user = basic_auth.current_user()
    return user.get_token()

# Post endpoints

# get all posts
@app.route('/posts')
def get_posts():
    select_stmt = db.select(Post)
    search = request.args.get('search')
    if search:
        select_stmt = select_stmt.where(Post.title.ilike(f"%{search}%"))
    # get the posts from database
    posts = db.session.execute(select_stmt).scalars().all()
    return [p.to_dict() for p in posts]


# Get a Single Post By ID
@app.route('/posts/<int:post_id>')
def get_post(post_id):
    # Get the post from the database by ID
    post = db.session.get(Post, post_id)
    if post:
        return post.to_dict()
    else:
        return {'error': f"Post with an ID of {post_id} does not exist"}, 404

# Create a Post
@app.route('/posts', methods=['POST'])
@token_auth.login_required
def create_post():
    # Check to see if the request body is JSON
    if not request.is_json:
        return {'error': 'Your content-type must be application/json'}, 400
    # Get the data from the request body
    data = request.json
    # Validate the incoming data
    required_fields = ['title', 'body']
    missing_fields = []
    # For each of the required fields
    for field in required_fields:
        # If the field is not in the request body dictionary
        if field not in data:
            # Add that field to the list of missing fields
            missing_fields.append(field)
    # If there are any missing fields, return 400 status code with the missing fields listed
    if missing_fields:
        return {'error': f"{', '.join(missing_fields)} must be in the request body"}, 400

    # Get data values
    title = data.get('title')
    body = data.get('body')

    current_user = token_auth.current_user()

    # Create a new Post instance with data (and get the id from the token authenticated user)
    new_post = Post(title=title, body=body, user_id=current_user.id)
    
    # Return the newly created post dictionary with a 201 Created Status Code
    return new_post.to_dict(), 201


# Update Post Endpoint
@app.route('/posts/<int:post_id>', methods=['PUT'])
@token_auth.login_required
def edit_post(post_id):
    # Check to see that they have a JSON body
    if not request.is_json:
        return {'error': 'You content-type must be application/json'}, 400
    # Let's the find post in the db
    post = db.session.get(Post, post_id)
    if post is None:
        return {'error': f"Post with ID #{post_id} does not exist"}, 404
    # Get the current user based on the token
    current_user = token_auth.current_user()
    # Check if the current user is the author of the post
    if current_user is not post.author:
        return {'error': "This is not your post. You do not have permission to edit"}, 403
    
    # Get the data from the request
    data = request.json
    # Pass that data into the post's update method
    post.update(**data)
    return post.to_dict()

# Delete a Post
@app.route('/posts/<int:post_id>', methods=['DELETE'])
@token_auth.login_required
def delete_post(post_id):
    # based on the post_id parameter check to see Post exists
    post = db.session.get(Post, post_id)
    
    if post is None:
        return {'error': f'Post with {post_id} does not exist. Please try again'}, 404
    
    #Make sure user trying to delete post is the user whom created it
    current_user = token_auth.current_user()
    if post.author is not current_user:
        return {'error': 'You do not have permission to delete this post'}, 403
    
    #delete the post
    post.delete()
    return {'success': f"{post.title} was successfully deleted"}, 200

# COMMENT ENDPOINTS

# Create a comment
@app.route('/posts/<int:post_id>/comments', methods=['POST'])
@token_auth.login_required
def create_comment(post_id):
    
    #make sure the request has a body
    if not request.is_json:
        return {'error': 'Your content-type must be application/json'}, 400
    #grab the correct post
    post = db.session.get(Post, post_id)
    if post is None:
        return {'error': f"Post {post_id} does not exist"}, 404
    
    data = request.json
    
    required_fields = ['body']
    missing_fields = []
    for field in required_fields:
        if field not in data:
            missing_fields.append(field)
    
    if missing_fields:
        return {'error': f"{", ".join(missing_fields)} must be present in the request body"}, 400
    
    body = data.get('body')
    current_user = token_auth.current_user()
    new_comment = Comment(body=body,user_id=current_user.id, post_id=post.id)
    return new_comment.to_dict(), 201

# Delete a comment
@app.route('/posts/<int:post_id>/comments/<int:comment_id>', methods=['DELETE'])
@token_auth.login_required
def delete_comment(post_id, comment_id):
    
    #grab our post by id 
    post = db.session.get(Post, post_id)
    
    if post is None:
        return {'error': f"Post {post_id} does not exist"}, 404
    
    comment = db.session.get(Comment, comment_id)
    
    if comment is None:
        return {'error': f"Comment {comment_id} does not exist"}, 404
    
    current_user = token_auth.current_user()
    
    if comment.user != current_user:
        return {'error': 'You do not have permission to delete this comment'}, 403
    
    comment.delete()
    return {'success': "Comment has been successfully deleted"}, 200


