from flask import render_template, current_app
from app.email import SendEmail

def SendPasswordResetEmail(user):
	token = user.GetPasswordResetToken()
	SendEmail('Запрос на сброс пароля.',
			   sender=current_app.config['MAIL_USERNAME'],
			   recipients=[user.email],
			   text_body=render_template('email/reset.txt', token=token),
			   html_body=render_template('email/reset.html', token=token))