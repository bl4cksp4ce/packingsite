from datetime import datetime
from flasksite import db, login_manager
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
    #testin fix this when ready
    packings = db.relationship('Packing', backref='author', lazy=True)

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

class Packing(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    date_created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    containers = db.relationship('Container', backref='packing', lazy=True)


    def __repr__(self):
        return f"Packing('{self.name}', '{self.date_created}', id: '{self.id}')"