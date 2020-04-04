from datetime import datetime
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from Dissekted import db, login_manager, app
from flask_login import UserMixin

# Getting the user from the user ID stored in a session
# Decoration added so the login_manager extension knows how to get a user
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# Database setup
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    # Length based on the fact that they'll be hashed so it's longer than user's intention
    username = db.Column(db.String(20), unique = True, nullable = False)
    email = db.Column(db.String(120), unique = True, nullable = False)
    password = db.Column(db.String(60), nullable= False)
    posts = db.relationship("Post", backref = "author", lazy = True)

    # reset
    def get_reset_token(self, expires_sec = 600):
        s = Serializer(app.config['SECRET_KEY'], expires_sec)
        return s.dumps({'user_id': self.id})

    @staticmethod
    def verify_reset_token(token):
        s = Serializer(app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token)['user_id']
        except:
            return None
        return User.query.get(user_id)

    # How to display our user info
    def __repr__(self):
        return f"User('{self.username}','{self.email}')"

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    # How to display a short description of a post
    def __repr__(self):
        return f"Post('{self.title}','{self.date_posted}')"
