from flask import request, render_template
from app import app, db
from .models import User, Post


# Will set up db later, for now we will store all Users in this users list
users = []


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



# Post endpoints

# get all posts
@app.route('/posts')
def get_posts():
    # get the posts from storage (fake data -> tomorrow will be db)
    posts = db.session.execute(db.select(Post)).scalars().all()
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

    # Create a new post dictionary with data
    new_post = {
        'id': len(post_data) + 1,
        'title': title,
        'body': body,
        'userId': 1,
        'dateCreated': '2024-03-25T15:21:35',
        'likes': 0
    }

     # Create a new Post instance with data (and hard-code user_id for time being)
    new_post = Post(title=title, body=body, user_id=2)
    
    # Return the newly created post dictionary with a 201 Created Status Code
    return new_post.to_dict(), 201
