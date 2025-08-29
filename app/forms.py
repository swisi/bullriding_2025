from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, BooleanField, SubmitField, IntegerField, HiddenField, FloatField, SelectField
from wtforms.validators import DataRequired, ValidationError, Email, EqualTo, Optional
from app.models import User, Participant

class LoginForm(FlaskForm):
    username = StringField('Benutzername', validators=[DataRequired()])
    password = PasswordField('Passwort', validators=[DataRequired()])
    remember_me = BooleanField('Angemeldet bleiben')
    submit = SubmitField('Anmelden')

class RegistrationForm(FlaskForm):
    username = StringField('Benutzername', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Passwort', validators=[DataRequired()])
    password2 = PasswordField(
        'Passwort wiederholen', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Registrieren')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Bitte einen anderen Benutzernamen verwenden.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Bitte eine andere Mailadresse verwenden')

class ChangePasswordForm(FlaskForm):
    current_password = PasswordField('Aktuelles Passwort', validators=[DataRequired()])
    new_password = PasswordField('Neues Passwort', validators=[DataRequired()])
    new_password2 = PasswordField('Neues Passwort wiederholen', validators=[DataRequired(), EqualTo('new_password')])
    submit = SubmitField('Passwort ändern')

class ParticipantForm(FlaskForm):
    id = HiddenField('ID')
    start_nr = IntegerField('Start Number')
    first_name = StringField('Vorname', validators=[DataRequired()])
    last_name = StringField('Name', validators=[DataRequired()])
    address = StringField('Addresse', validators=[DataRequired()])
    postal_code = StringField('PLZ', validators=[DataRequired()])
    city = StringField('Ort', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    phone = StringField('Telefon')
    photo = FileField('Foto', validators=[Optional(), FileAllowed(['jpg', 'jpeg', 'png', 'gif'], 'Images only!')])
    submit = SubmitField('Speichern')

    def load_data(self, participant):
        self.id.data = participant.id
        self.start_nr.data = participant.start_nr
        self.first_name.data = participant.first_name
        self.last_name.data = participant.last_name
        self.address.data = participant.address
        self.postal_code.data = participant.postal_code
        self.city.data = participant.city
        self.email.data = participant.email
        self.phone.data = participant.phone
        # Foto wird nicht vorbefüllt

    def update_data(self, participant):
        participant.start_nr = self.start_nr.data
        participant.first_name = self.first_name.data
        participant.last_name = self.last_name.data
        participant.address = self.address.data
        participant.postal_code = self.postal_code.data
        participant.city = self.city.data
        participant.email = self.email.data
        participant.phone = self.phone.data
        
    def validate_start_nr(self, start_nr):
        if start_nr.data is None:
            return
        current_id = None
        try:
            current_id = int(self.id.data) if self.id.data else None
        except (TypeError, ValueError):
            current_id = None

        query = Participant.query.filter(Participant.start_nr == start_nr.data)
        if current_id is not None:
            query = query.filter(Participant.id != current_id)
        if query.first():
            raise ValidationError('This start number is already in use. Please choose a different one.')

    def _convert_to_float(self, value):
        try:
            return float(value) if value.strip() else None
        except ValueError:
            return None
