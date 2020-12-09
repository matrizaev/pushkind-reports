from flask_login import current_user
from app.models import User, UserRoles
from flask import render_template, flash, jsonify
from functools import wraps

'''
################################################################################
Consts
################################################################################
'''
DATE_TIME_FORMAT = '%Y-%m-%d %H:%M:%S %z'
DATE_FORMAT = '%Y-%m-%d'

'''
################################################################################
Utilities
################################################################################
'''

def role_required(roles_list):
	def decorator(function):
		@wraps(function)
		def wrapper(*args, **kwargs):
			if current_user.role not in roles_list:
				return render_template('errors/403.html'),403
			else:
				return function(*args, **kwargs)
		return wrapper
	return decorator
	
def role_forbidden(roles_list):
	def decorator(function):
		@wraps(function)
		def wrapper(*args, **kwargs):
			if current_user.role in roles_list:
				return render_template('errors/403.html'),403
			else:
				return function(*args, **kwargs)
		return wrapper
	return decorator
	
def role_required_ajax(roles_list):
	def decorator(function):
		@wraps(function)
		def wrapper(*args, **kwargs):
			if current_user.role not in roles_list:
				return jsonify({'status':False, 'flash':['У вас нет соответствующих полномочий.']}),403
			else:
				return function(*args, **kwargs)
		return wrapper
	return decorator
	
def role_forbidden_ajax(roles_list):
	def decorator(function):
		@wraps(function)
		def wrapper(*args, **kwargs):
			if current_user.role in roles_list:
				return jsonify({'status':False, 'flash':['У вас нет соответствующих полномочий.']}),403
			else:
				return function(*args, **kwargs)
		return wrapper
	return decorator