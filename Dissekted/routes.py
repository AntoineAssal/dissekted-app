import os
from flask import redirect, request, url_for, render_template, flash, abort
from flask_login import login_user, logout_user, current_user, login_required
from flask_mail import Message
from Dissekted import app, db, bcrypt, mail
from Dissekted.forms import RegistrationForm, LoginForm, PostingForm, RequestPWResetForm, ResetPassword
from Dissekted.models import User, Post


# Endpoints setup for displaying the HTML files
@app.route('/')
def index():
    # slides = os.listdir("static/carousel")
    return render_template('index.html')


@app.route('/media')
def media():
    pics = os.listdir("Dissekted/static/images/")
    return render_template("media.html", title='Media', pics=pics)


@app.route('/login', methods=['GET', 'POST'])
def login():
    # Send to homepage if already logged in and trying to access this page
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        # Logic for login: query database if user exists, check against database for password, if it matches login
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('posts'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template("login.html", title="Log In", form=form)


@app.route('/register', methods=['GET', 'POST'])
def register():
    # Send to homepage if already logged in and trying to access this page
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        # Default salt value of 12 is used since I'm not specifying it
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash(f'Account created successfully! Welcome {form.username.data}! You can now login', 'success')
        return redirect(url_for('login'))
    return render_template("signup.html", title="Sign up", form=form)


@app.route('/subscribe')
def subscribe():
    return render_template("subscribe.html", title="Subscribe Now!")


@app.route('/posts')
@login_required
def posts():
    posts = Post.query.all()
    return render_template('posts.html', title='posts', posts=posts)


@app.route('/posts/new', methods=['GET', 'POST'])
@login_required
def new_post():
    form = PostingForm()
    if form.validate_on_submit():
        post = Post(title=form.title.data, content=form.content.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash("Your post has been created!", "success")
        return redirect(url_for('posts'))
    return render_template('create_post.html', title='New post', form=form, header="Create new post")


@app.route("/posts/<int:post_id>")
def post(post_id):
    post = Post.query.get_or_404(post_id)
    return render_template('post.html', title=post.title, post=post)


@app.route("/posts/<int:post_id>/edit", methods=['GET', 'POST'])
@login_required
def edit(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    form = PostingForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        db.session.commit()
        flash("Your post has been updated!", 'success')
        return redirect(url_for('post', post_id=post.id))
    elif request.method == "GET":
        form.title.data = post.title
        form.content.data = post.content
    return render_template('create_post.html', title='Edit post', form=form, header="Edit post")


@app.route("/posts/<int:post_id>/delete", methods=['GET', 'POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    db.session.delete(post)
    db.session.commit()
    flash("Your post has been deleted!", 'success')
    return redirect(url_for("posts"))


def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message('Password Reset Request',
                  sender='noreply@demo.com',
                  recipients=[user.email])
    msg.body = f'''To reset your password, visit the following link:
{url_for('reset_token', token=token, _external=True)}
\nIf you did not make this request then simply ignore this email and no changes will be made.
'''
    mail.send(msg)


@app.route('/reset_password', methods=['GET', 'POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RequestPWResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash('An email has been sent with instructions to reset your password', 'info')
        return redirect(url_for('login'))
    return render_template('reset_request.html', title='Reset Password', form=form)


@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    user = User.verify_reset_token(token)
    if user is None:
        flash("That is an invalid or expired token", 'warning')
        return redirect(url_for(reset_request))
    form = ResetPassword()
    if form.validate_on_submit():
        # Default salt value of 12 is used since I'm not specifying it
        hashed_password = bcrypt.generate_password_hash(form.password.data)
        user.password = hashed_password
        db.session.commit()
        flash('You have changed your password! You can now login', 'success')
        return redirect(url_for('login'))
    return render_template('reset_token.html', title='Reset Password', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))
