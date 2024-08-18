from flask import Flask, redirect, render_template, request, flash
from models import db, connect_db, User, Post
from flask_debugtoolbar import DebugToolbarExtension

app = Flask(__name__)

# Set a secret key for sessions
app.config['SECRET_KEY'] = 'frgtrhyjuj7grfr3gtghyt5h' 
app.debug = True

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///blogly'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True

# Initialize the database connection
connect_db(app)

# Create all tables within the application context
with app.app_context():
    db.create_all()

# Flask routes
@app.route('/')
def home():
    """Redirect to the list of users."""
    return redirect('/users')


@app.route('/users')
def list_users():
    """Show all users, ordered by last name and first name."""
    users = User.query.order_by(User.last_name, User.first_name).all()
    return render_template('user_list.html', users=users)


@app.route('/users/new', methods=["GET", "POST"])
def new_user():
    """Display a form to add a new user or handle the form submission."""
    if request.method == "POST":
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        image_url = request.form['image_url'] or None

        new_user = User(first_name=first_name, last_name=last_name, image_url=image_url)
        db.session.add(new_user)
        db.session.commit()

        return redirect('/users')
    return render_template('new_user_form.html')


@app.route('/users/<int:user_id>')
def show_user(user_id):
    """Show information about the given user."""
    user = User.query.get_or_404(user_id)
    return render_template('user_details.html', user=user)


@app.route('/users/<int:user_id>/edit', methods=["GET", "POST"])
def edit_user(user_id):
    """Show a form to edit a user or handle the form submission."""
    user = User.query.get_or_404(user_id)

    if request.method == "POST":
        user.first_name = request.form['first_name']
        user.last_name = request.form['last_name']
        user.image_url = request.form['image_url']
        db.session.commit()

        return redirect(f'/users/{user_id}')
    return render_template('edit_user_form.html', user=user)


@app.route('/users/<int:user_id>/delete', methods=["POST"])
def delete_user(user_id):
    """Handle the deletion of a user."""
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    return redirect('/users')


# Post routes
@app.route('/users/<int:user_id>/posts/new', methods=["GET", "POST"])
def new_post(user_id):
    """Show form to add a new post for a specific user and handle submission."""
    user = User.query.get_or_404(user_id)

    if request.method == "POST":
        title = request.form['title']
        content = request.form['content']

        new_post = Post(title=title, content=content, user_id=user_id)
        db.session.add(new_post)
        db.session.commit()

        flash(f'Post "{title}" added!')
        return redirect(f'/users/{user_id}')
    
    return render_template('new_post_form.html', user=user)


@app.route('/posts/<int:post_id>')
def show_post(post_id):
    """Show details for a specific post."""
    post = Post.query.get_or_404(post_id)
    return render_template('post_details.html', post=post)


@app.route('/posts/<int:post_id>/edit', methods=["GET", "POST"])
def edit_post(post_id):
    """Show form to edit post and handle submission."""
    post = Post.query.get_or_404(post_id)

    if request.method == "POST":
        post.title = request.form['title']
        post.content = request.form['content']
        db.session.commit()

        flash(f'Post "{post.title}" edited!')
        return redirect(f'/posts/{post.id}')
    
    return render_template('edit_post_form.html', post=post)


@app.route('/posts/<int:post_id>/delete', methods=["POST"])
def delete_post(post_id):
    """Handle deletion of a post."""
    post = Post.query.get_or_404(post_id)
    user_id = post.user_id
    db.session.delete(post)
    db.session.commit()

    flash(f'Post "{post.title}" deleted!')
    return redirect(f'/users/{user_id}')
