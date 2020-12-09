from app import db
from flask_login import current_user, login_required
from app.main import bp
from app.models import User, UserRoles, Task, Report, Department, ReportTask
from flask import render_template, redirect, url_for, flash, request
from app.main.forms import ReportForm
from app.main.utils import role_required, role_forbidden
from datetime import date
import dateutil.parser
from dateutil.parser._parser import ParserError

@bp.route('/')
@bp.route('/index')
@bp.route('/reports')
@login_required
@role_forbidden([UserRoles.default])
def ShowIndex():
	filter_date = request.args.get('date')
	try:
		filter_date = dateutil.parser.parse(filter_date).date()
	except (TypeError, ParserError):
		filter_date = date.today()
	if current_user.role == UserRoles.admin:
		users = User.query.filter(User.dep_id != None, User.role == UserRoles.employee).order_by(User.dep_id).all()
	elif current_user.role == UserRoles.manager:
		users = User.query.filter(User.dep_id == current_user.dep_id, User.role == UserRoles.employee, ).all()
	else:
		users = [current_user]
	form = ReportForm()
	return render_template('reports.html', users=users, filter_date=filter_date, form=form)
	
@bp.route('/report/<int:rt_id>/modify', methods=['POST'])
@login_required
@role_required([UserRoles.employee])
def ModifyReport(rt_id):
	report_task = ReportTask.query.filter(ReportTask.id == rt_id, ReportTask.completed == False).first()
	if report_task is None or report_task.report.user_id != current_user.id:
		flash('Такое назначение не существует.')
		return redirect(url_for('main.ShowIndex'))
	form = ReportForm()
	if form.validate_on_submit():
		report_task.measurement = form.measurement.data
		report_task.completed = form.completed.data
		if form.comment.data is not None:
			report_task.comment = form.comment.data.strip()
		db.session.commit()
		flash('Назначение успешно исправлено.')
	else:
		for error in form.measurement.errors + form.completed.errors + form.comment.errors:
			flash(error)
	return redirect(url_for('main.ShowIndex', date=report_task.report.date))