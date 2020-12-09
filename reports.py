from app import create_app, db
from app.models import User, UserRoles, Department, Task, Report, ReportTask

application = create_app()

@application.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'UserRoles':UserRoles, 'Department':Department, 'Task':Task,\
	'Report':Report, 'ReportTask':ReportTask}