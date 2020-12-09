from app import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import login
from hashlib import md5
import json
import jwt
import enum
from datetime import date, timezone
from sqlalchemy.sql import func


class UserRoles(enum.IntEnum):
	default = 0
	admin = 1
	employee = 2
	manager = 3
	
	def __str__(self):
		pretty = ['Без роли', 'Администратор', 'Сотрудник', 'Начальник']
		return pretty[self.value]

@login.user_loader
def load_user(id):
	return User.query.get(int(id))
	
class User(UserMixin, db.Model):
	id  = db.Column(db.Integer, primary_key = True)
	email	= db.Column(db.String(128), index = True, unique = True, nullable=False)
	password = db.Column(db.String(128), nullable=False)
	name = db.Column(db.String(128))
	role = db.Column(db.Enum(UserRoles), index=True, nullable=False, default=UserRoles.default)
	dep_id = db.Column(db.Integer, db.ForeignKey('department.id'))
	department = db.relationship('Department')
	reports = db.relationship('Report', lazy='dynamic')
	
	def __hash__(self):
		return self.id
		
	def __eq__(self, another):
		return isinstance(another, User) and self.id == another.id
	
	def __repr__(self):
		return json.dumps(self.to_dict())
	
	def SetPassword(self, password):
		self.password = generate_password_hash(password)
		
	def CheckPassword(self, password):
		return check_password_hash(self.password, password)
		
	def GetAvatar(self, size):
		digest = md5(self.email.lower().encode('utf-8')).hexdigest()
		return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(digest, size)
		
	def to_dict(self):
		data = {'id':self.id, 'email':self.email}
		return data
		
	def GetPasswordResetToken(self, expires_in=600):
		return jwt.encode(
			{'reset_password': self.id, 'exp': time() + expires_in},
			current_app.config['SECRET_KEY'],
			algorithm='HS256').decode('utf-8')

	@staticmethod
	def VerifyPasswordResetToken(token):
		try:
			id = jwt.decode(token, current_app.config['SECRET_KEY'],
							algorithms=['HS256'])['reset_password']
		except:
			return
		return User.query.get(id)
		
class Department(db.Model):
	id  = db.Column(db.Integer, primary_key = True)
	name = db.Column(db.String(128), index = True, unique = True, nullable=False)
	users = db.relationship('User')
	tasks = db.relationship('Task')
	
class Task(db.Model):
	id  = db.Column(db.Integer, primary_key = True)
	name = db.Column(db.String(128), index = True, nullable=False)
	metric = db.Column(db.String(128))
	dep_id = db.Column(db.Integer, db.ForeignKey('department.id'))
	department = db.relationship('Department')
	
class Report(db.Model):
	id  = db.Column(db.Integer, primary_key = True)
	date = db.Column(db.Date, index=True, nullable=False, default=date.today(), server_default=func.date('now'))
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
	user = db.relationship('User')
	tasks = db.relationship("ReportTask", back_populates="report")
	
class ReportTask(db.Model):
	id  = db.Column(db.Integer, primary_key = True)
	name = db.Column(db.String(128), nullable=False)
	metric = db.Column(db.String(128))
	measurement = db.Column(db.Float)
	completed = db.Column(db.Boolean, nullable=False, default=True)
	comment = db.Column(db.Text)	
	rep_id = db.Column(db.Integer, db.ForeignKey('report.id'), nullable=False)
	report = db.relationship("Report", back_populates="tasks")

