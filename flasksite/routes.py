import os
import secrets
import pickle
import numpy as np
import sys
import matplotlib.pyplot as plt
import mpld3


import random
from PIL import Image
from flask import Flask, render_template, url_for, flash, redirect, request, abort
from flasksite import app, db, bcrypt
from flasksite.functions import generate_boxes, putbox, create_container_instance
from flasksite.forms import RegistrationForm, LoginForm, UpdateAccountForm, BoxForm, PostForm, PackingForm, ContainerForm
from flasksite.models import User, Post, Container, Packing, Box, ContainerInstance, BoxInstance
from flask_login import login_user, current_user, logout_user, login_required
from sqlalchemy import desc


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

#def new_container_instance(container_id):
    #instance=0
    #return instance


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
        flash('Your post has been created!', 'success')
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
            up=form.up.data, down=form.down.data, weight=form.weight.data, quantity=form.quantity.data, packing=packing) #fix this, add db box
        db.session.add(box)
        db.session.commit()
        flash('Box added', 'success')
        return redirect(url_for('packings'))
    return render_template('create_box.html', title='New Box', form=form)





@app.route('/packing1/<int:packing_id>/container/<int:container_id>/')
def container(container_id, packing_id):
    container = Container.query.get_or_404(container_id)
    packing_id=container.packing_id
    #containers = Container.query.filter_by(packing_id= packing_id).all()
    #posts = Post.query.all()
    #return render_template('home.html', posts=posts)

    return render_template('container.html', container = container, packing_id=packing_id)

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

def results(packing_id):
    container_instances = ContainerInstance.query.all(packing_id).all()
    containers_used = len(container_instances)


@app.route("/packing1/<int:packing_id>/plan")
def generate_plan(packing_id):
    packing = Packing.query.get_or_404(packing_id)
    container = Container.query.filter_by(packing_id=packing_id).first()
    boxes = Box.query.filter_by(packing_id=packing_id).all()
    #full_weight = 0
    #for box in boxes:
        #full_weight += box.weight
    container_type = container.id
    packing_id = packing_id
    x = container.x
    y = container.y
    z = container.z
    name = container.name
    container_instance_id = 0 #ezt kell növelni új konténernél
    array_boxes = np.zeros((int(x/10), int(y/10), int(z/10)), dtype='int')
    #id = random.randint(1, 20000)
    filename = "instance" + str(container_instance_id) + ".pkl"
    directory = 'containers/containers_' + str(packing_id)
    if not os.path.exists(directory):
        os.makedirs(directory)
    container_instance_id +=1 #for the next instance

    #boxes_in = [] #integer array of the box_ids
    boxes_file = "boxids.pkl"
    #path_box = directory + "/" + boxes_file #lehet ezt hozzá kéne adni a boxhoz?
    path = directory + "/" + filename
    pickle.dump(array_boxes, open(path, "wb"))#létrejön példányoításkor, címeiket valahol tárolni kéne
    #pickle.dump(boxes_in, open(path_box, "wb"))

    #box_p = pickle.load(open(path_box), "rb")
    data_p = pickle.load(open(path, "rb"))
    full_weight = data_p[1][1][1]

    box_instances = BoxInstance.query.filter_by(packing_id=packing_id).all()
    #ha masnak is lehet ilyen packing id, akkor lehet baj
    #if box_instances.author != current_user:
        #abort(403)  # forbidden route
    for b in box_instances:
        db.session.delete(b)
        db.session.commit()
    generate_boxes(packing_id)
    containers_ordered = ContainerInstance.query.filter_by(packing_id=packing_id).order_by(
        ContainerInstance.weight_remaining).all()
    for c in containers_ordered:
        db.session.delete(c)
        db.session.commit()
    #acking = Packing.query.filter_by(id=packing_id).all()
    container_instance_path = create_container_instance(packing_id)
    box_instances_ordered = BoxInstance.query.filter_by(packing_id=packing_id).order_by(desc(BoxInstance.x*BoxInstance.y*BoxInstance.z)).all()#order_by(desc(BoxInstance.weight)).
    #box_instances_ordered.sort(key=weight, reverse=True)
    #.order_by(BoxInstance.weight.desc())
    #box_instances_by_size = BoxInstance.query.order_by()

    #v = containers_ordered[0].get('x')
    #containers are neot ordered yet
    #b = box_instances_ordered[0]
    #c = containers_ordered[0]
    id_i = 1
    box_locations = []
    #a_l = {"a": 11111, 'b': 2}
    create_container_instance(packing_id)
    for b in box_instances_ordered:
        a = False
        i = 0
        containers_ordered = ContainerInstance.query.filter_by(packing_id=packing_id).order_by(ContainerInstance.weight_remaining).all()
        print(containers_ordered[0].instance_id, file=sys.stderr)
        print(len(containers_ordered), file=sys.stderr)
        while a==False:
            #ujra is kell rendezni mindig a konténerelket
            if len(containers_ordered) > i:
                c = containers_ordered[i]
                filename = 'instance' + str(c.instance_id) + ".pkl"
                directory = 'containers/containers_' + str(packing_id)
                container_instance_path = directory + "/" + filename
            else:
                print('Hello world!', file=sys.stderr)
                container_instance_path = create_container_instance(packing_id)
                containers_ordered = ContainerInstance.query.filter_by(packing_id=packing_id).order_by(ContainerInstance.weight_remaining).all()
                c = containers_ordered[i]
            a = putbox(c, b, container_instance_path, box_locations, id_i, a)
            print(a, file=sys.stderr)
            i += 1
    l = len(box_locations)
    #for b in box_instances_ordered:
        #global a
        #a = False
        #space = b.x*b.y*b.z
        #for co in containers_ordered:
        #c = containers_ordered[0]
            #if co.space_remaining>=space and co.weight_remaining>=b.weight:
                #filename = "instance" + str(co.container_instance_id) + ".pkl"
                #directory = 'containers/containers_' + str(packing_id)
                #path = directory + "/" + filename
                #container instance path needs to be redefined if there is a new instance fix this
                #global a
                #putbox(co, b, path,box_locations, id_i, a)
                #if a :
                    #break
        #if not a :
            #path = create_container_instance(packing_id)
            #putbox(co, b, path, box_locations, id_i, a)

    #box_locations.append(a_l)
    a = box_locations[0].get('x_start')
    b = box_locations[0].get('x_end')
    dict = {
        "name" : "Fs",
        "x" : 3,
        "y" : b,
        'z' : a
    }
    #dict_2 = {
        #"name": "Fs",
        #"x": 3,
        #"y": 2,
        #'z': 1
    #}
    #dictlist = []
    #dictlist.append(dict)
    #dictlist.append(dict_2)
    #plt.plot([3, 1, 4, 1, 5], 'ks-', mec='w', mew=5, ms=20)
    #mpld3.show()

    #boxes_plt = []
    # for a in box3d:
    # a = box_location[0]
    # print(a)
    # print(a.get('x_start'))
    #for a in box_locations:
        #cube_1 = (x >= a.get('x_start')) & (x < a.get('x_end')) & (y >= a.get('y_start')) & (y < a.get('y_end')) & (
        #z >= a.get('z_start')) & (z < a.get('z_end'))
        #boxes_plt.append(cube_1)

    #voxels = boxes_plt[0]
    #for i in range(1, len(boxes_plt)):
        #voxels |= boxes_plt[i]
    #colors = np.empty(voxels.shape, dtype=object)
    #colors_list = ['red', 'green', 'blue', 'purple', 'cyan', 'violet', 'springgreen']
    #for i in boxes_plt:
        #colors[i] = random.choice(colors_list)

    #x, y, z = np.indices((8, 8, 8))

    # draw cuboids in the top left and bottom right corners, and a link between them
    #cube1 = (x < 3) & (y < 3) & (z < 3)
    #cube2 = (x >= 5) & (y >= 5) & (z >= 5)
    #link = abs(x - y) + abs(y - z) + abs(z - x) <= 2

    # combine the objects into a single boolean array
    #voxels = cube1 | cube2 | link

    # set the colors of each object
    #colors = np.empty(voxels.shape, dtype=object)
    #colors[link] = 'red'
    #colors[cube1] = 'blue'
    #colors[cube2] = 'green'

    # and plot everything
    #fig = plt.figure()
    #ax = fig.gca(projection='3d')
    #ax.voxels(voxels, facecolors=colors, edgecolor='k')
    #fig = plt.figure()
    #ax = fig.gca(projection='3d')
    #ax.voxels(voxels, facecolors=colors, edgecolor='k')

    #mpld3.show()
    #pd.Series(fig).to_json(orient='values')
    #json_dump = json.dumps(fig, cls=NumpyEncoder)
    #html_graph = mpld3.fig_to_html(fig)
    #for i in range(box_instances_ordered):
     #   b = box_instances_ordered[i]
      #  a = 0
       # c = containers_ordered[a]
        #while(not b.packed):



        #maybe filename for the path of the matrix
        #


    #thing_to_save = cPickle.load(open("filename.pkl", "rb"))
    #container_instance = ContainerInstance(name=name, container_type=container_type, packing_id=packing_id, x=x, y=y, z=z, array_boxes=array_boxes)
    #post = Post(name=form.title.data, content=form.content.data, author=current_user)
    #db.session.add(container_instance)
    #db.session.commit()
    #lehetne space remaining a konténer adatbázisban, meg weight remaining, database modellhez mehet ez,
    #  utána id alapján megkeresi a pickleök között a mátrixát, amit frissít a pakolásakor,
    #  ekkor frissül a weigh és space remaining és a dobozok pickle és a dobozok ide vonatkozó részei
    #a dobozokat meg szintén hozzádaja a picklökhöz, így vissza lehet hívni az adatot a riporthoz

    #tehát beindul a pakolés, újabb és újabb instanceek lesznek a konténerekből, ezek mappákban lesznek,
    #a doboz instanceket valahogy át kell adni a pakolófüggvénynek
    #az id-nak megfelelő mappában a modell, így azt a pakoló átadás nélkül eléri
    container_instance = containers_ordered[0]

    return render_template('plan.html', full_weight=full_weight, box_locations=box_locations, box_instances_ordered=box_instances_ordered, containers_ordered=containers_ordered, l=l, container_instance=container_instance)

