import os
import secrets
from PIL import Image
from flask import Flask, render_template, url_for, flash, redirect, request, abort
from flasksite import app, db, bcrypt
from flasksite.forms import RegistrationForm, LoginForm, UpdateAccountForm, BoxForm, PostForm, PackingForm
from flasksite.models import User, Post, Container, Packing
from flask_login import login_user, current_user, logout_user, login_required


@app.route('/') #decorator
@app.route("/home")
def home():
    posts = Post.query.all()
    return render_template('home.html', posts=posts)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! Your are able to log in!', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='register', form=form)

@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please Check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))

def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_fn)
    #image resizing with Pillow
    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)

    i.save(picture_path)
    return picture_fn

@app.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit() :
        if form.picture.data :
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Your account has benn updated!', 'success')
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    return render_template('account.html', title='Account',
                           image_file=image_file, form=form)

@app.route("/post/new", methods=['GET', 'POST'])
@login_required
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(title=form.title.data, content = form.content.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash('Your post has been freated!', 'success')
        return redirect(url_for('home'))
    return render_template('create_post.html', title='New Post',
                           form=form, legend='New Post')


@app.route("/post/<int:post_id>")
def post(post_id) :
    post = Post.query.get_or_404(post_id)
    return render_template('post.html', title=post.title, post=post)

@app.route("/post/<int:post_id>/update", methods=['GET', 'POST'])
@login_required
def update_post(post_id) :
    post = Post.query.get_or_404(post_id)
    if post.author != current_user :
        abort(403) #forbidden route
    form = PostForm()
    if form.validate_on_submit() :
        post.title = form.title.data
        post.content = form.content.data
        db.session.commit() #update db here, no need to add, bc it exists
        flash('Your post has been updated!', 'success')
        return redirect(url_for('post', post_id=post.id))
    elif request.method == 'GET' :
        form.title.data = post.title
        form.content.data = post.content
    return render_template('create_post.html', title='Update Post',
                           form=form, legend='Update Post')

@app.route("/post/<int:post_id>/delete", methods=['POST'])
@login_required
def delete_post(post_id) :
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)  # forbidden route
    db.session.delete(post)
    db.session.commit()
    flash('Your post has been deleted!', 'success')
    return redirect(url_for('home'))

@app.route("/container/new", methods=['GET', 'POST'])
@login_required
def new_container():
    form = ContainerForm()
    if form.validate_on_submit():
        container = Container(name=form.name.data, x=form.x.data, y=form.y.data,
                              z=form.z.data, max_weight=form.max_weight.data, user_id=current_user.id)
        db.session.add(container)
        db.session.commit()
        flash('Container created', 'success')
        return redirect(url_for('home'))
    return render_template('create_container.html', title='New Container', form=form)

@app.route("/packing/new", methods=['GET', 'POST'])
@login_required
def new_packing():
    form = PackingForm()
    if form.validate_on_submit():
        packing = Packing(name=form.name.data, user_id=current_user.id)
        db.session.add(packing)
        db.session.commit()
        flash('Packing created', 'success')
        return redirect(url_for('home'))
    return render_template('create_packing.html', title='New Packing', form=form)

@app.route("/packings/")
def packings() :
    packings = Packing.query.filter_by(user_id=current_user.id).all()
    return render_template('packings.html', packings=packings)

@app.route("/box/new", methods=['GET', 'POST'])
@login_required
def new_box():
    form = BoxForm()
    if form.validate_on_submit():
        #container = Container(name=form.name.data, x=form.x.data, y=form.y.data,
        #                      z=form.z.data, max_weight=form.max_weight.data, user_id=current_user.id)
        #db.session.add(container)
        #db.session.commit()
        flash('Box added', 'success')
        return redirect(url_for('home'))
    return render_template('create_box.html', title='New Box', form=form)
