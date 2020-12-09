from flask_wtf import FlaskForm
from wtforms import SubmitField, IntegerField, StringField, SelectField, TextAreaField, FormField, Form, PasswordField, BooleanField, FloatField
from wtforms.validators import DataRequired, Length, ValidationError, Email, InputRequired, Optional
from app.models import UserRoles
import datetime
from wtforms.fields.html5 import DateField
from app.main.utils import DATE_FORMAT

class DepartmentForm(FlaskForm):
	department_name = StringField('Название', validators = [DataRequired(message='Название отдела - обязательное поле.')])
	create = SubmitField('Создать')
	delete = SubmitField('Удалить')

class UserForm(FlaskForm):
	full_name = StringField('ФИО')
	role = SelectField('Роль',[InputRequired(message = 'Некорректная роль пользователя.')], coerce = int,
						choices = [(int(role), str(role)) for role in UserRoles])
	department = SelectField('Отдел',[InputRequired(message = 'Некорректный отдел.')], coerce = int)
	submit = SubmitField('Сохранить')
	
class TaskForm(FlaskForm):
	task_name = StringField('Название', validators = [DataRequired(message='Название отдела - обязательное поле.')])
	metric = StringField('Метрика')
	department = SelectField('Отдел',[InputRequired(message = 'Некорректный отдел.')], coerce = int)
	submit = SubmitField('Сохранить')
	
class AssignmentForm(FlaskForm):
	user = SelectField('Сотрудник',[InputRequired(message = 'Некорректный сотрудник.')], coerce = int)
	date = DateField('Дата', [InputRequired(message = 'Дата - обязательное поле.')], format=DATE_FORMAT)
	measurement = FloatField('Показатель', [Optional()], render_kw={'type': 'number', 'step':'0.01'})
	comment = TextAreaField('Комментарий', [Optional(), Length(max = 1024)])
	completed = BooleanField('Исполнено')
	submit = SubmitField('Назначить')
	
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		if not self.date.data:
			self.date.data = datetime.date.today()
			
class ReportForm(FlaskForm):
	measurement = FloatField('Показатель', [Optional()], render_kw={'type': 'number', 'step':'0.01'})
	comment = StringField('Комментарий', [Optional(), Length(max = 1024)])
	completed = BooleanField('Исполнено')