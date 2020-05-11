import os
import secrets
import pickle
import numpy as np
import sys
import matplotlib.pyplot as plt
import mpld3


import random
from PIL import Image
from flask import Flask, render_template, url_for, flash, redirect, request, abort, jsonify
from flasksite import app, db, bcrypt, mail
from flasksite.functions import generate_boxes, putbox, create_container_instance
from flasksite.forms import (RegistrationForm, LoginForm, UpdateAccountForm, BoxForm,
                             PostForm, PackingForm, ContainerForm, RequestResetForm,
                             ResetPasswordForm)
from flasksite.models import User, Post, Container, Packing, Box, ContainerInstance, BoxInstance
from flask_login import login_user, current_user, logout_user, login_required
from sqlalchemy import desc
from flask_mail import Message
from openpyxl import load_workbook, Workbook


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
        flash('Your account has been updated!', 'success')
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    return render_template('account.html', title='Account',
                           image_file=image_file, form=form)


@app.route("/packing/<int:packing_id>/container/new", methods=['GET', 'POST'])
@login_required
def new_container(packing_id):
    form = ContainerForm()
    packing = Packing.query.get_or_404(packing_id)
    if form.validate_on_submit():
        container = Container(name=form.name.data, x=form.x.data, y=form.y.data, z=form.z.data, max_weight=form.max_weight.data, packing=packing) # user id itt kell vagy nem?
        db.session.add(container)
        db.session.commit()
        flash('Container created', 'success')
        return redirect(url_for('new_box', packing_id=packing_id))
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
        return redirect(url_for('packing', packing_id=packing.id))
    return render_template('create_packing.html', title='New Packing', form=form)

@app.route("/packings/")
def packings():
    packings = Packing.query.filter_by(user_id=current_user.id).all()
    return render_template('packings.html', packings=packings)



@app.route("/packing/<int:packing_id>/box/new", methods=['GET', 'POST'])
@login_required
def new_box(packing_id):
    form = BoxForm()
    packing = Packing.query.get_or_404(packing_id)
    if form.validate_on_submit():
        box = Box(name=form.name.data, x=form.x.data, y=form.y.data,z=form.z.data, r_x=form.r_x.data, r_y=form.r_y.data, r_z=form.r_z.data,
        weight=form.weight.data, quantity=form.quantity.data, packing=packing) #fix this, add db box
        db.session.add(box)
        db.session.commit()
        flash('Box added', 'success')
        return redirect(url_for('packing', packing_id=packing_id))
    return render_template('create_box.html', title='New Box', form=form)





@app.route('/packing1/<int:packing_id>/container/<int:container_id>/')
def container(container_id, packing_id):
    container = Container.query.get_or_404(container_id)
    packing_id=container.packing_id
    containers = Container.query.filter_by(packing_id= packing_id).all()
    c = len(containers)
    print("c =" + str(c), file=sys.stderr)
        #checking if there is any container

    return render_template('container.html', container = container, packing_id=packing_id, c=c)

@app.route('/packing1/<int:packing_id>/box/<int:box_id>/')
def box(box_id, packing_id):
    box = Box.query.get_or_404(box_id)
    packing_id=box.packing_id
    #containers = Container.query.filter_by(packing_id= packing_id).all()
    #posts = Post.query.all()
    #return render_template('home.html', posts=posts)

    return render_template('box.html', box = box, packing_id=packing_id)



@app.route("/packing1/<int:packing_id>/box/<int:box_id>/delete", methods=['POST'])
@login_required
def delete_box(box_id, packing_id):
    box = Box.query.get_or_404(box_id)
    packing = Packing.query.filter_by(id=packing_id).all()
    #print(packing)
    user_id = packing[0].user_id
    user = User.query.filter_by(id=user_id).first()
    if  user != current_user:#fixthis: need to access author/user from box, maybe data model change needed maybe accessible with query
        abort(403)  # forbidden route
    db.session.delete(box)
    db.session.commit()
    flash('Your box has been deleted!', 'success')
    return redirect(url_for('packings'))

@app.route("/packing1/<int:packing_id>/container/<int:container_id>/delete", methods=['POST'])
@login_required
def delete_container(container_id, packing_id) :
    container = Container.query.get_or_404(container_id)
    packing = Packing.query.filter_by(id=packing_id).all()
    user_id = packing[0].user_id
    user = User.query.filter_by(id=user_id).first()
    if  user != current_user:
        abort(403)  # forbidden route
    db.session.delete(container)
    db.session.commit()
    flash('Your box has been deleted!', 'success')
    return redirect(url_for('packings'))




@app.route("/packing1/<int:packing_id>")
def packing(packing_id):
    packing = Packing.query.get_or_404(packing_id)
    containers = Container.query.filter_by(packing_id= packing_id).all()
    #posts = Post.query.all()
    #return render_template('home.html', posts=posts)

    return render_template('packing1.html', name=packing.name, packing=packing, containers = containers)


@app.route("/packing1/<int:packing_id>/results")
def results(packing_id):
    #packing = Packing.query.get_or_404(packing_id)
    container = Container.query.filter_by(packing_id=packing_id).first()
    #boxes = Box.query.filter_by(packing_id=packing_id).all()

    #container_type = container.id
    packing_id = packing_id
    x = container.x
    y = container.y
    z = container.z
    #name = container.name
    container_instance_id = 0  # ezt kell növelni új konténernél
    array_boxes = np.zeros((int(x / 10), int(y / 10), int(z / 10)), dtype='int')
    # id = random.randint(1, 20000)
    filename = "instance" + str(container_instance_id) + ".pkl"
    directory = 'containers/containers_' + str(packing_id)
    if not os.path.exists(directory):
        os.makedirs(directory)
    container_instance_id += 1  # for the next instance


    path = directory + "/" + filename
    pickle.dump(array_boxes, open(path, "wb"))  # létrejön példányoításkor, címeiket valahol tárolni kéne

    #data_p = pickle.load(open(path, "rb"))
    #full_weight = data_p[1][1][1]

    box_instances = BoxInstance.query.filter_by(packing_id=packing_id).all()
    # ha masnak is lehet ilyen packing id, akkor lehet baj
    # if box_instances.author != current_user:
    # abort(403)  # forbidden route
    for b in box_instances:
        db.session.delete(b)
        db.session.commit()
    generate_boxes(packing_id)
    containers_ordered = ContainerInstance.query.filter_by(packing_id=packing_id).order_by(
        ContainerInstance.space_remaining).all()
    for c in containers_ordered:
        db.session.delete(c)
        db.session.commit()
    # acking = Packing.query.filter_by(id=packing_id).all()
    container_instance_path = create_container_instance(packing_id)
    box_instances_ordered = BoxInstance.query.filter_by(packing_id=packing_id).order_by(
        desc(BoxInstance.x * BoxInstance.y * BoxInstance.z)).all()  # order_by(desc(BoxInstance.weight)).

    #box_locations = []
    #create_container_instance(packing_id)
    for b in box_instances_ordered:
        a = False
        i = 0
        containers_ordered = ContainerInstance.query.filter_by(packing_id=packing_id).order_by(
            ContainerInstance.weight_remaining).all()
        print(containers_ordered[0].instance_id, file=sys.stderr)
        print(len(containers_ordered), file=sys.stderr)
        while a == False:
            # ujra is kell rendezni mindig a konténerelket
            if len(containers_ordered) > i:
                c = containers_ordered[i]
                filename = 'instance' + str(c.instance_id) + ".pkl"
                directory = 'containers/containers_' + str(packing_id)
                container_instance_path = directory + "/" + filename
            else:
                print('Hello world!', file=sys.stderr)
                container_instance_path = create_container_instance(packing_id)
                containers_ordered = ContainerInstance.query.filter_by(packing_id=packing_id).order_by(
                    ContainerInstance.space_remaining).all()
                c = containers_ordered[i]
            a = putbox(c, b, container_instance_path, c.instance_id)
            print(a, file=sys.stderr)
            i += 1
    #l = len(box_locations)




    #container_instance = containers_ordered[0]

    #box_locations_1 = [box for box in box_locations if box['id'] == containers_ordered[0].instance_id]

    #return render_template('plan.html', packing=packing, full_weight=full_weight, box_locations=box_locations_1,
                           #box_instances_ordered=box_instances_ordered, containers_ordered=containers_ordered, l=l,
                           #container_instance=container_instance)

    container_instances = ContainerInstance.query.filter_by(packing_id=packing_id).all()

    containers_used = len(container_instances)
    box_instances = BoxInstance.query.filter_by(packing_id=packing_id).all()
    boxes_packed = len(box_instances)
    total_weight = 0
    total_space = 0
    for c in containers_ordered: total_space += c.space_remaining;
    for b in box_instances:
        total_weight += b.weight
    average_weight = total_weight/containers_used
    average_box_n = boxes_packed/containers_used
    average_space = total_space/containers_used

    containers_ordered = ContainerInstance.query.filter_by(packing_id=packing_id).order_by(
        ContainerInstance.weight_remaining).all()
    all_weight = 0
    for c in containers_ordered: all_weight += c.weight_remaining

    min_space_c = ContainerInstance.query.filter_by(packing_id=packing_id).order_by(ContainerInstance.space_remaining).first()
    max_space_c = ContainerInstance.query.filter_by(packing_id=packing_id).order_by(desc(ContainerInstance.space_remaining)).first()
    min_space = min_space_c.space_remaining/(container.x*container.y*container.z)*100
    max_space = max_space_c.space_remaining/(container.x*container.y*container.z)*100
    min_weight_c = ContainerInstance.query.filter_by(packing_id=packing_id).order_by(ContainerInstance.weight_remaining).first()
    max_weight_c = ContainerInstance.query.filter_by(packing_id=packing_id).order_by(desc(ContainerInstance.weight_remaining)).first()

    min_weight = min_weight_c.weight_remaining
    max_weight = max_weight_c.weight_remaining



    return render_template('results.html', container_instances=container_instances, containers_used=containers_used,
                           box_instances=box_instances, boxes_packed=boxes_packed, total_weight=total_weight,
                           average_weight=average_weight, average_box_n=average_box_n, packing_id=packing_id,
                           containers_ordered=containers_ordered, min_space=min_space,
                           max_space=max_space, max_weight=max_weight, min_weight=min_weight, average_space=average_space)

@app.route("/packing/<int:packing_id>/container_instance/<int:instance_id>")
def see_instance(packing_id, instance_id):
    container_instance = ContainerInstance.query.filter_by(instance_id=instance_id).first()
    #print(container_instance.x, file=sys.stderr)
    box_instances = BoxInstance.query.filter_by(container_instance_id=instance_id).all()
    print(box_instances, file=sys.stderr)
    number_of_boxes = len(box_instances)
    #print(box_instances[0].x_end)
    #box_locations_1 = [box for box in box_locations if box['id'] == instance_id]
    box_locations = [dict() for x in range(len(box_instances))]
    #location = {"x_start": 0,
    #            "x_end": 0,
    #            "y_start": 0,
    #            "y_end": 0,
    #            "z_start": 0,
    #            "z_end": 0,
    #            "id": 0}
    box_ids = []
    for i in range(len(box_instances)):
        box_locations[i] = {
            "x_start": box_instances[i].x_start,
            "x_end": box_instances[i].x_end,
            "y_start": box_instances[i].y_start,
            "y_end": box_instances[i].y_end,
            "z_start": box_instances[i].z_start,
            "z_end": box_instances[i].z_end,
            "id": box_instances[i].container_instance_id,
            "box_id": box_instances[i].box_id
        }
        box_ids.append(box_instances[i].box_id)
        #print("hello", file=sys.stderr)
        #location["x_start"] = box_instances[i].x_start
        #print(location["x_start"], file=sys.stderr)
        #location['x_end'] = box_instances[i].x_end
        #print(location["x_end"], file=sys.stderr)
        #location['y_start'] = box_instances[i].y_start
        #print(location["y_start"], file=sys.stderr)
        #location['y_end'] = box_instances[i].y_end
        #location['z_start'] = box_instances[i].z_start
        #print(location["z_start"], file=sys.stderr)

    #weight_pc = 10*1-(container_instance.weight_remaining/container_instance.max_weight)
    box_ids = list(dict.fromkeys(box_ids))
    boxes = []
    count = []
    for b in box_ids:
        d = len(BoxInstance.query.filter_by(box_id=b).filter_by(container_instance_id=instance_id).all())
        a = Box.query.filter_by(id=b).first()
        print("d=" + str(d), file=sys.stderr)
        #a.toarray()
        count.append(d)
        boxes.append(a)
    boxes_2 = [dict() for x in range(len(boxes))]
    for i in range(len(boxes)):
        boxes_2[i] = {
            "x": boxes[i].x,
            "y": boxes[i].y,
            "z": boxes[i].z,
            "weight": boxes[i].weight,
            "number": count[i],
            #"z_end": box_instances[i].z_end,
            "id": boxes[i].id,
            #"box_id": box_instances[i].box_id
        }
        #box_ids.append(box_instances[i].box_id)
    box_colors = [dict() for x in range(len(box_ids))]
    for b_id in range(len(box_ids)):
        color = "%06x" % random.randint(0, 0xFFFFFF)
        s_color = "#" + str(color)
        print(color, file=sys.stderr)
        box_colors[b_id] = {"id": box_ids[b_id],
                            "color:": s_color
                            }
    weight_remaining = container_instance.weight_remaining
    space_remaining = container_instance.space_remaining/(container_instance.x*container_instance.y*container_instance.z)*100
    print(container_instance.x, file=sys.stderr)


    return render_template('container_instance_original.html',box_locations=box_locations, container_instance=container_instance,
                           number_of_boxes=number_of_boxes, instance_id=instance_id, weight_remaining=weight_remaining,
                           space_remaining=space_remaining, boxes_2=boxes_2)


def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message('Password Reset Request', sender='brutalistbp@gmail.com',
                  recipients=['giantoctopus216@gmail.com'])#[user.email])
    msg.body = f''' To reset your password, visit the following link:
{url_for('reset_token', token=token, _external=True)}

If xou did not make this request then ignore this email and no changes will be made
'''
    mail.send(msg)

@app.route("/reset_password", methods=['GET', 'POST'])
def reset_request():
    from flasksite import mail
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash('Email with reset link sent.', 'info')
        return redirect(url_for('login'))
    return render_template('reset_request.html', title='Reset Password', form=form)

@app.route("/reset_password/<token>", methods=['GET', 'POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    user = User.verify_reset_token(token)
    if not user:
        flash('That is an invalid or expired token!', 'warning')
        return redirect(url_for('reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_password
        db.session.commit()
        flash('Your password has been updated! Your are able to log in!', 'success')
        return redirect(url_for('login'))
    return render_template('reset_token.html', title='Reset Password', form=form)


