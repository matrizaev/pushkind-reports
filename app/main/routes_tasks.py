from app import db
from flask_login import current_user, login_required
from app.main import bp
from app.models import User, UserRoles, Task, Report, Department, ReportTask
from flask import render_template, redirect, url_for, flash, request
from app.main.forms import TaskForm, AssignmentForm
from app.main.utils import role_required, role_forbidden
from sqlalchemy import or_

@bp.route('/tasks')
@login_required
@role_forbidden([UserRoles.default])
def ShowTasks():
	task_form = TaskForm()
	assign_form = AssignmentForm()
	if current_user.role == UserRoles.admin:
		tasks = Task.query.order_by(Task.dep_id).all()
		departments = Department.query.all()
		departments_list = [(d.id, d.name) for d in departments]
	else:
		tasks = Task.query.filter(or_(Task.dep_id == current_user.dep_id, Task.dep_id == None)).order_by(Task.dep_id).all()
		departments_list = [(current_user.dep_id,current_user.department.name)]
	if current_user.role == UserRoles.manager:
		users = User.query.filter(User.dep_id == current_user.dep_id, User.id != current_user.id, User.role == UserRoles.employee).order_by(User.name).all()
		users_list = [(u.id, u.name) for u in users]
	elif current_user.role == UserRoles.employee:
		users_list = [(current_user.id,current_user.name)]
	else:
		users_list = []
	departments_list.append((0, 'Без отдела'))
	task_form.department.choices = departments_list
	assign_form.user.choices = users_list
	return render_template('tasks.html', tasks=tasks, task_form=task_form, assign_form=assign_form)


@bp.route('/task/', defaults={'task_id': None}, methods=['POST'])
@bp.route('/task/<int:task_id>', methods=['POST'])
@login_required
@role_required([UserRoles.admin, UserRoles.manager])
def ModifyTask(task_id):
	form = TaskForm()
	if current_user.role == UserRoles.admin:
		departments = Department.query.all()
		departments_list = [(d.id, d.name) for d in departments]		
	else:
		departments_list = [(current_user.dep_id,current_user.department.name)]		
	departments_list.append((0, 'Без отдела'))
	form.department.choices = departments_list
	if form.validate_on_submit():
		if task_id is None:
			task = Task()
			db.session.add(task)
		else:
			task = Task.query.filter(Task.id == task_id).first()
		task.name = form.task_name.data.strip()
		task.metric = form.metric.data.strip()
		if form.department.data != 0:
			task.dep_id = form.department.data
		else:
			task.dep_id = None
		db.session.commit()
		flash('Задача успешно сохранена.')
	else:
		for error in form.task_name.errors + form.metric.errors + form.department.errors:
			flash(error)
	return redirect(url_for('main.ShowTasks'))
	
@bp.route('/task/<int:task_id>/delete', methods=['GET'])
@login_required
@role_required([UserRoles.admin, UserRoles.manager])
def DeleteTask(task_id):
	task = Task.query.filter(Task.id == task_id).first()
	if task is None:
		flash('Такой задачи не существует.')
		return redirect(url_for('main.ShowTasks'))
	if current_user.role == UserRoles.manager and task.dep_id is not None and current_user.dep_id != task.dep_id:
		return render_template('errors/403.html'),403
	db.session.delete(task)
	db.session.commit()
	flash('Задача успешно удалена.')
	return redirect(url_for('main.ShowTasks'))
	
@bp.route('/task/<int:task_id>/assign', methods=['POST'])
@login_required
@role_required([UserRoles.employee, UserRoles.manager])
def AssignTask(task_id):
	task = Task.query.filter().first()
	if task is None:
		flash('Такой задачи не существует.')
		return redirect(url_for('main.ShowTasks'))
	form = AssignmentForm()
	if current_user.role == UserRoles.manager:
		users = User.query.filter(User.dep_id == current_user.dep_id, User.id != current_user.id, User.role == UserRoles.employee).order_by(User.name).all()
		users_list = [(u.id, u.name) for u in users]
	else:
		users_list = [(current_user.id,current_user.name)]
	form.user.choices = users_list
	if form.validate_on_submit():
		report = Report.query.filter(Report.user_id == form.user.data, Report.date == form.date.data).first()
		if report is None:
			report = Report(user_id = form.user.data, date = form.date.data)
			db.session.add(report)
			db.session.commit()
		report_task = ReportTask(name = task.name, metric = task.metric, measurement = form.measurement.data, completed = form.completed.data)
		if form.comment.data is not None:
			report_task.comment = form.comment.data.strip()
		db.session.add(report_task)
		report_task.report = report
		db.session.commit()
		flash('Задача успешно назначена сотруднику.')
	else:
		for error in form.user.errors + form.date.errors + form.measurement.errors + form.completed.errors + form.comment.errors:
			flash(error)
	return redirect(url_for('main.ShowTasks'))