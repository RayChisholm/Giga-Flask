from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Email, Length, Optional


class ZendeskSettingsForm(FlaskForm):
    """Form for Zendesk API credentials"""
    subdomain = StringField('Zendesk Subdomain', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    api_token = PasswordField('API Token', validators=[DataRequired()])
    submit = SubmitField('Save Settings')


class UserManagementForm(FlaskForm):
    """Form for creating/editing users"""
    username = StringField('Username', validators=[
        DataRequired(),
        Length(min=3, max=64)
    ])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[Optional(), Length(min=6)])
    role = SelectField('Role', choices=[('user', 'User'), ('admin', 'Admin')], validators=[DataRequired()])
    active = BooleanField('Active')
    submit = SubmitField('Save User')
