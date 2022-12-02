"""Blogly application."""

from flask_debugtoolbar import DebugToolbarExtension
from flask import Flask,  request, render_template,  redirect, flash, session
from models import db, connect_db, User, Post

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///blogly'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['SQLALCHEMY_ECHO'] = True
app.config['SQLALCHEMY_RECORD_QUERIES'] = True

app.debug = True
app.config['SECRET_KEY'] = "SECRET!"
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
toolbar = DebugToolbarExtension(app)

with app.app_context():
    connect_db(app)
    db.create_all()


@app.route("/")
def home():
    """Show all Posts."""
    posts = Post.query.order_by(Post.created_at.desc()).limit(5).all()

    return render_template("home.html", posts=posts)


@app.route("/users")
def list_users():
    """List users and show add user form."""

    users = User.query.order_by(User.last_name, User.first_name).all()
    return render_template("list.html", users=users)


@app.route("/users/new")
def new_user_form():
    """Render form for creating a new user."""

    return render_template("add-user-form.html")


@app.route('/users/new', methods=["POST"])
def add_user():
    """Process the add form, adding a new user and going back to /users."""

    first_name = request.form["first-name"]
    last_name = request.form["last-name"]
    image_url = request.form["image-url"]

    if len(image_url) > 0:
        new_user = User(first_name=first_name,
                        last_name=last_name, image_url=image_url)
    else:
        new_user = User(first_name=first_name,
                        last_name=last_name)

    db.session.add(new_user)
    db.session.commit()
    db.session.close()

    return redirect(f'/users')


@app.route("/users/<int:user_id>")
def show_user(user_id):
    """Show info on a single user."""

    user = User.query.get_or_404(user_id)
    posts = Post.query.filter(Post.user_id == user_id)

    return render_template("detail.html", user=user, posts=posts)


@app.route("/users/<int:user_id>/edit")
def edit_user(user_id):
    """Show the edit page for a user."""

    user = User.query.get_or_404(user_id)

    return render_template("edit-user-form.html", user=user)


@app.route("/users/<int:user_id>/edit", methods=["POST"])
def commit_edit_user(user_id):
    """Process the edit form, returning the user to the /users page."""

    first_name = request.form["first-name"]
    last_name = request.form["last-name"]
    image_url = request.form["image-url"]

    user = User.query.get_or_404(user_id)
    user.first_name = first_name
    user.last_name = last_name

    if len(image_url) > 0:
        user.image_url = image_url

    db.session.add(user)
    db.session.commit()
    db.session.close()

    return redirect(f'/users')


@app.route("/users/<int:user_id>/delete", methods=["POST"])
def delete_user(user_id):
    """Delete the user."""
    user = User.query.get_or_404(user_id)

    db.session.delete(user)
    db.session.commit()
    db.session.close()

    return redirect(f'/users')


###################################################

@app.route("/users/<int:user_id>/posts/new")
def add_post(user_id):
    """Show form to add a post for that user."""
    user = User.query.get_or_404(user_id)

    return render_template("new-post-form.html", user=user)


@app.route("/users/<int:user_id>/posts/new", methods=["POST"])
def commit_new_post(user_id):
    """Handle add form; add post and redirect to the user detail page."""

    title = request.form["post-title"]
    content = request.form["post-content"]
    user = User.query.get_or_404(user_id)
    new_post = Post(title=title, content=content, usr=user)

    db.session.add(new_post)
    db.session.commit()

    return redirect(f'/users/{user.id}')


@app.route("/posts/<int:post_id>")
def show_post(post_id):
    """Show a post. Show buttons to edit and delete the post."""
    post = Post.query.get_or_404(post_id)

    return render_template("single-post.html", post=post)


@app.route("/posts/<int:post_id>/edit")
def edit_post(post_id):
    """Show form to edit a post, and to cancel (back to user page)."""

    post = Post.query.get_or_404(post_id)

    return render_template("edit-post-form.html", post=post)


@app.route("/posts/<int:post_id>/edit", methods=["POST"])
def commit_edit_post(post_id):
    """Handle editing of a post. Redirect back to the post view."""

    title = request.form["post-title"]
    content = request.form["post-content"]

    post = Post.query.get_or_404(post_id)
    post.title = title
    post.content = content

    db.session.add(post)
    db.session.commit()

    return redirect(f'/posts/{post.id}')


@app.route("/posts/<int:post_id>/delete", methods=["POST"])
def delete_post(post_id):
    """Delete the post."""
    post = Post.query.get_or_404(post_id)

    db.session.delete(post)
    db.session.commit()
    db.session.close()

    return redirect(f'/users/{post.user_id}')
