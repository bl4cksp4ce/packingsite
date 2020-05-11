from datetime import datetime
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flasksite import db, login_manager, app
from flask_login import UserMixin


@login_manager.user_loader #decorator
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    password = db.Column(db.String(60), nullable=False)
    posts = db.relationship('Post', backref='author', lazy=True)
    packings = db.relationship('Packing', backref='author', lazy=True)

    def get_reset_token(self, expires_sec=1800):
        s = Serializer(app.config['SECRET_KEY'], expires_sec)
        return s.dumps({'user_id':self.id}).decode('utf_8')

    @staticmethod
    def verify_reset_token(token):
        s = Serializer(app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token)['user_id']
        except:
            return None
        return User.query.get(user_id)
    #testin fix this when ready


    def __repr__(self):
        return f"User('{self.username}','{self.email}', '{self.image_file}')"

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f"Post('{self.title}', '{self.date_posted}')"

class Container(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    x = db.Column(db.Integer, nullable=False)
    y = db.Column(db.Integer, nullable=False)
    z = db.Column(db.Integer, nullable=False)
    max_weight = db.Column(db.Integer, nullable=False)
    packing_id = db.Column(db.Integer, db.ForeignKey('packing.id'), nullable=False)

    def __repr__(self):
        return f"Container('{self.name}', x='{self.x}', y='{self.y}')," \
               f"z='{self.z}', max weight='{self.max_weight}', packing_id='{self.packing_id}', id='{self.id}'"

class ContainerInstance(db.Model):

    packing_id = db.Column(db.Integer)
    container_id = db.Column(db.Integer, db.ForeignKey('container.id'), nullable=False)
    instance_id = db.Column(db.Integer, primary_key=True)
    x = db.Column(db.Integer, nullable=False)
    y = db.Column(db.Integer, nullable=False)
    z = db.Column(db.Integer, nullable=False)
    weight_remaining = db.Column(db.Integer, nullable=False)
    space_remaining = db.Column(db.Integer, nullable=False)
    max_weight = db.Column(db.Integer, nullable=False)#returnbe is

    def __repr__(self):
        return f"Container instance('container={self.container_id}', x='{self.x}', y='{self.y}')," \
               f"z='{self.z}', weight remaining='{self.weight_remaining}', instance_id='{self.instance_id}'," \
               f" space_remaining='{self.space_remaining}' packing id= '{self.packing_id}', max_weight='{self.max_weight}'"


class BoxInstance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    box_id = db.Column(db.Integer)
    name = db.Column(db.String(100), nullable=False)
    x = db.Column(db.Integer, nullable=False)
    y = db.Column(db.Integer, nullable=False)
    z = db.Column(db.Integer, nullable=False)
    weight = db.Column(db.Integer, nullable=False)
    packing_id = db.Column(db.Integer, db.ForeignKey('packing.id'), nullable=False)
    container_instance_id = db.Column(db.Integer)
    x_start = db.Column(db.Integer)
    x_end = db.Column(db.Integer)
    y_start = db.Column(db.Integer)
    y_end = db.Column(db.Integer)
    z_start = db.Column(db.Integer)
    z_end = db.Column(db.Integer)
    packed = db.Column(db.Integer)#inicializálás nullával
    r_x = db.Column(db.Boolean, default=False, nullable=False)
    r_y = db.Column(db.Boolean, default=False, nullable=False)
    r_z = db.Column(db.Boolean, default=False, nullable=False)

    def __repr__(self):
        return f"Box instance('name={self.container_instance_id}','name={self.container_instance_id}'," \
               f"'id={self.id}', x='{self.x}', y='{self.y}')," \
               f"z='{self.z}', weight='{self.weight}', box_id='{self.box_id}', x rotation='{self.r_x}', y rotation='{self.r_y}'," \
               f" x rotation='{self.r_x}', packed='{self.packed}' packing id= '{self.packing_id}', box_id='{self.box_id}'," \
               f" x_start='{self.x_start}', y_start='{self.y_start}'), z_start='{self.z_start}'," \
               f" x_end='{self.x_end}'), y_end='{self.y_end}', z_end='{self.z_end}'),"

class Box(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    x = db.Column(db.Integer, nullable=False)
    y = db.Column(db.Integer, nullable=False)
    z = db.Column(db.Integer, nullable=False)
    r_x = db.Column(db.Boolean, default=False, nullable=False)
    r_y = db.Column(db.Boolean, default=False, nullable=False)
    r_z = db.Column(db.Boolean, default=False, nullable=False)
    weight = db.Column(db.Integer, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    packing_id = db.Column(db.Integer, db.ForeignKey('packing.id'), nullable=False)

    def __repr__(self):
        return f"Box('{self.name}', x='{self.x}', y='{self.y}')," \
               f"z='{self.z}', x rotation='{self.r_x}', y rotation='{self.r_y}'," \
               f" z rotation='{self.r_z}'," \
               f" weight='{self.weight}', packing_id='{self.packing_id}', id='{self.id}', quantity='{self.quantity}')" #, user_id='{self.user_id}')"

class Packing(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    date_created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    containers = db.relationship('Container', backref='packing', lazy=True)
    boxes = db.relationship('Box', backref='packing', lazy=True)


    def __repr__(self):
        return f"Packing('{self.name}', '{self.date_created}', id: '{self.id}')"