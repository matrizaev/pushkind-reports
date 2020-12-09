from app import db
from flask_login import current_user, login_required
from app.main import bp
from app.models import User, UserRoles, Task, Report, Department
from flask import render_template, redirect, url_for, flash, request
from app.main.forms import DepartmentForm, UserForm
from app.main.utils import role_required, role_forbidden

@bp.route('/users')
@login_required
@role_forbidden([UserRoles.default])
def ShowUsers():
	if current_user.role == UserRoles.admin:
		users = User.query.filter(User.dep_id == None).all()
		departments = Department.query.all()
		department_form = DepartmentForm()
		user_form = UserForm()
		departments_list = [(d.id, d.name) for d in departments]
		departments_list.append((0, 'Без отдела'))
		user_form.department.choices = departments_list
		return render_template('users.html', users=users, departments=departments, department_form=department_form, user_form = user_form)
	else:
		user_form = UserForm()
		user_form.department.choices = [(current_user.dep_id, current_user.department.name)]
		return render_template('users.html', user_form = user_form)


@bp.route('/user/<int:user_id>/modify', methods=['POST'])
@login_required
@role_forbidden([UserRoles.default])
def ModifyUser(user_id):
	if current_user.role == UserRoles.admin:
		user = User.query.filter(User.id == user_id).first()
		if user:
			form = UserForm()
			departments = Department.query.all()
			departments_list = [(d.id, d.name) for d in departments]
			departments_list.append((0, 'Без отдела'))
			form.department.choices = departments_list
			if form.validate_on_submit():
				user.name = form.full_name.data.strip()
				user.role = UserRoles(form.role.data)
				if form.department.data != 0:
					user.dep_id = form.department.data
				else:
					user.dep_id = None
				db.session.commit()
				flash('Пользователь успешно обновлён.')
			else:
				for error in form.full_name.errors + form.role.errors + form.department.errors:
					flash(error)
		else:
			flash('Такого пользователя не существует.')
	elif user_id == current_user.id:
		form = UserForm()
		form.department.choices = [(current_user.dep_id, current_user.department.name)]
		if form.validate_on_submit():
			current_user.name = form.full_name.data.strip()
			db.session.commit()
			flash('Пользователь успешно обновлён.')
		else:
			for error in form.full_name.errors + form.role.errors + form.department.errors:
				flash(error)
	else:
		return render_template('errors/403.html'),403
	return redirect(url_for('main.ShowUsers'))

@bp.route('/user/<int:user_id>/delete', methods=['GET'])
@login_required
@role_forbidden([UserRoles.default])
def DeleteUser(user_id):
	if current_user.role == UserRoles.admin or current_user.id == user_id:
		user = User.query.filter(User.id == user_id).first()
		if user:
			db.session.delete(user)
			db.session.commit()
			flash('Пользователь успешно удалён.')
		else:
			flash('Такого пользователя не существует.')
	else:
		return render_template('errors/403.html'),403
	return redirect(url_for('main.ShowUsers'))


@bp.route('/department/', defaults={'dep_id': None}, methods=['POST'])
@bp.route('/department/<int:dep_id>', methods=['POST'])
@login_required
@role_required([UserRoles.admin])
def ModifyDepartment(dep_id):
	form = DepartmentForm()
	if form.validate_on_submit():
		department_name = form.department_name.data.strip()
		if dep_id is None:
			department = Department.query.filter(Department.name == department_name).first()
			if form.create.data is True:
				if department is not None:
					flash('Отдел с таким названием уже существует.')
				else:
					department = Department(name = department_name)
					db.session.add(department)
					db.session.commit()
					flash('Отдел успешно создан.')
			elif form.delete.data is True:
				if department is None:
					flash('Такого отдела не существует.')
				else:
					db.session.delete(department)
					db.session.commit()
					flash('Отдел успешно удалён.')
		else:
			department = Department.query.filter(Department.id == dep_id).first()
			if department is None:
				flash('Такого отдела не существует.')
			else:
				department.name = department_name
				db.session.commit()
				flash('Отдел успешно изменён.')
	else:
		for error in form.department_name.errors:
			flash(error)
	return redirect(url_for('main.ShowUsers'))