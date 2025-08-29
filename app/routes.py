from flask import render_template, flash, redirect, url_for, request, Blueprint, jsonify
from flask_login import current_user, login_user, logout_user, login_required

from app import db
from app.models import User, Participant
from app.forms import LoginForm, RegistrationForm, ParticipantForm, ChangePasswordForm
from werkzeug.utils import secure_filename
import os
from flask import current_app

bp = Blueprint('main', __name__)

@bp.route('/')
@bp.route('/index')
def index():

    participants = Participant.query.all()
    participants.sort(key=lambda p: (
            p.toptime_Finalrunde if p.toptime_Finalrunde is not None else float('-inf'),
            p.toptime_Zwischenrunde if p.toptime_Zwischenrunde is not None else float('-inf'),
            p.toptime_Vorrunde if p.toptime_Vorrunde is not None else float('-inf')
    ), reverse=True)

    if not participants:
        flash('Keine Teilnehmer gefunden')
        form = ParticipantForm()
        return render_template('participant.html', title='Teilnehmer hinzufügen', form=form)

    if not current_user.is_authenticated:
        return render_template('ranking.html', title='Rangliste', rankings=participants)

       
    return render_template(
        'index.html', 
        title='Home', 
        participants=participants, 
    )

@bp.route('/active')
def active():
    participant = Participant.query.filter_by(active=True).first()
    return render_template('active.html', title='Live', participant=participant)

@bp.route('/stage')
@login_required
def stage():
    participant = Participant.query.filter_by(active=True).first()
    return render_template('stage.html', title='Stage', participant=participant)

@bp.route('/active_id')
def active_id():
    """Lightweight endpoint to check the current active participant id.
    Used by the stage/live views to avoid full-page reloads unless needed.
    """
    participant = Participant.query.filter_by(active=True).first()
    pid = participant.id if participant else None
    return jsonify({"id": pid})

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password', 'danger')
            return redirect(url_for('main.login'))
        login_user(user, remember=form.remember_me.data)
        flash('Welcome back!', 'success')
        return redirect(url_for('main.index'))
    return render_template('login.html', title='Sign In', form=form)

@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.index'))

@bp.route('/register', methods=['GET', 'POST'])
def register():
    # If user is already logged in, no need to register
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    # Temporarily disable self-registration unless explicitly allowed
    from flask import current_app
    if not current_app.config.get('ALLOW_REGISTRATION', False):
        flash('Registrierung ist derzeit deaktiviert. Bitte melden Sie sich an.', 'info')
        return redirect(url_for('main.login'))

    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!', 'success')
        return redirect(url_for('main.login'))
    return render_template('register.html', title='Register', form=form)

@bp.route('/password', methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if not current_user.check_password(form.current_password.data):
            flash('Aktuelles Passwort ist falsch.', 'danger')
            return redirect(url_for('main.change_password'))
        current_user.set_password(form.new_password.data)
        db.session.commit()
        flash('Passwort erfolgreich geändert.', 'success')
        return redirect(url_for('main.index'))
    return render_template('change_password.html', title='Passwort ändern', form=form)

@bp.route('/participants')
@login_required
def participant():
    participants = Participant.query.all()
    show_thumbs = request.args.get('thumbs', default='1')
    try:
        show_thumbs = False if str(show_thumbs) in ('0', 'false', 'False') else True
    except Exception:
        show_thumbs = True
    return render_template('participant.html', title='Alle Teilnehmer', participants=participants, show_thumbs=show_thumbs)

@bp.route('/participant_add', methods=['GET', 'POST'])
@login_required
def participant_add():
    form = ParticipantForm()
    if form.validate_on_submit():
        participant = Participant()
        form.update_data(participant)
        # Handle photo upload
        file = form.photo.data
        if file:
            filename = secure_filename(file.filename)
            # avoid collisions
            base, ext = os.path.splitext(filename)
            safe_name = f"{base}_{str(id(participant))}{ext}"
            upload_dir = current_app.config['UPLOAD_FOLDER']
            os.makedirs(upload_dir, exist_ok=True)
            file_path = os.path.join(upload_dir, safe_name)
            file.save(file_path)
            # store relative path under static
            participant.photo = os.path.join('uploads', safe_name).replace('\\', '/')
        db.session.add(participant)
        db.session.commit()
        flash('Participant added successfully!', 'success')
        return redirect(url_for('main.index'))
    return render_template('participant_add.html', title='Add Participant', form=form)

@bp.route('/participant_edit/<int:id>', methods=['GET', 'POST'])
@login_required
def participant_edit(id):
    participant = Participant.query.get_or_404(id)
    form = ParticipantForm(obj=participant)
    if form.validate_on_submit():
        form.update_data(participant)
        # Handle new photo upload (optional)
        file = form.photo.data
        if file:
            filename = secure_filename(file.filename)
            base, ext = os.path.splitext(filename)
            safe_name = f"{base}_{participant.id}{ext}"
            upload_dir = current_app.config['UPLOAD_FOLDER']
            os.makedirs(upload_dir, exist_ok=True)
            file_path = os.path.join(upload_dir, safe_name)
            file.save(file_path)
            participant.photo = os.path.join('uploads', safe_name).replace('\\', '/')
        db.session.commit()
        flash('Participant updated successfully!', 'success')
        return redirect(url_for('main.index'))
    form.load_data(participant)
    
    return render_template('participant_edit.html', title='Edit Participant', form=form, participant=participant)

@bp.route('/participant_delete/<int:id>', methods=['POST'])
@login_required
def participant_delete(id):
    participant = Participant.query.get_or_404(id)
    # Optionally remove photo file (ignore errors)
    if participant.photo:
        try:
            os.remove(os.path.join(current_app.static_folder, participant.photo))
        except Exception:
            pass
    db.session.delete(participant)
    db.session.commit()
    flash('Participant deleted successfully!', 'success')
    return redirect(url_for('main.index'))

@bp.route('/update_times/<int:id>', methods=['POST'])
@login_required
def update_times(id):
    participant = Participant.query.get_or_404(id)
    
    if 'update_times' in request.form:
        participant.time1 = request.form.get('time1', type=float)
        participant.time2 = request.form.get('time2', type=float)
        participant.time3 = request.form.get('time3', type=float)
        participant.time4 = request.form.get('time4', type=float)
        participant.time5 = request.form.get('time5', type=float)
        participant.time6 = request.form.get('time6', type=float)
        
        db.session.commit()
        flash('Times and round statuses updated successfully!', 'success')
    
    if 'set_active' in request.form:
        Participant.query.update({Participant.active: False})
        participant.active = True
        db.session.commit()
        flash('Active participant set successfully!', 'success')

    return redirect(url_for('main.index'))

@bp.route('/update_times_bulk', methods=['POST'])
@login_required
def update_times_bulk():
    participants = Participant.query.all()
    for participant in participants:
        participant.time1 = request.form.get(f'time1_{participant.id}', type=float)
        participant.time2 = request.form.get(f'time2_{participant.id}', type=float)
        participant.time3 = request.form.get(f'time3_{participant.id}', type=float)
        participant.time4 = request.form.get(f'time4_{participant.id}', type=float)
        participant.time5 = request.form.get(f'time5_{participant.id}', type=float)
        participant.time6 = request.form.get(f'time6_{participant.id}', type=float)
    db.session.commit()
    flash('Times and round statuses updated successfully!', 'success')
    return redirect(url_for('main.index'))

@bp.route('/finish_round/<string:round>', methods=['POST'])
@login_required
def finish_round(round):
    

    if round == 'VR1':
        participants = Participant.query.all()
        # Sortiere Teilnehmer nach Zeit in der ersten Vorrunde in absteigender Reihenfolge
        sorted_participants = sorted(participants, key=lambda p: p.time1 if p.time1 is not None else float('-inf'), reverse=True)

        # Setze alle Teilnehmer auf nicht qualifiziert
        for participant in participants:
            participant.round1_qualified = False

        # Qualifiziere alle Teilnehmer mit Zeit >= 99 Sekunden
        qualified_participants = []
        for participant in participants:
            if participant.time1 is not None and participant.time1 >= 99:
                participant.round1_qualified = True
                participant.round2_qualified = True
                participant.round3_qualified = True
                qualified_participants.append(participant)

        # Fülle die Qualifikationen auf, bis mindestens 5 Teilnehmer qualifiziert sind
        for participant in sorted_participants:
            if len(qualified_participants) < 5:
                if not participant.round1_qualified:  # Nur nicht bereits qualifizierte Teilnehmer hinzufügen
                    participant.round1_qualified = True
                    participant.round2_qualified = True
                    participant.round3_qualified = True
                    qualified_participants.append(participant)
            else:
                break



    elif round == 'VR2':
        participants = Participant.query.all()
        # Sortiere Teilnehmer nach Zeit in der ersten Vorrunde in absteigender Reihenfolge
        sorted_participants = sorted(participants, key=lambda p: p.time2 if p.time2 is not None else float('-inf'), reverse=True)


        # Qualifiziere alle Teilnehmer mit Zeit >= 99 Sekunden
        qualified_participants = []
        for participant in participants:
            if participant.time2 is not None and participant.time2 >= 99:
                participant.round2_qualified = True
                participant.round3_qualified = True
                qualified_participants.append(participant)

        # Fülle die Qualifikationen auf, bis mindestens 5 Teilnehmer qualifiziert sind
        for participant in sorted_participants:
            if len(qualified_participants) < 5:
                if not participant.round2_qualified :  # Nur nicht bereits qualifizierte Teilnehmer hinzufügen
                    participant.round2_qualified = True
                    participant.round3_qualified = True
                    qualified_participants.append(participant)
            else:
                break


    elif round == 'VR3':
        participants = Participant.query.all()
        # Sortiere Teilnehmer nach Zeit in der ersten Vorrunde in absteigender Reihenfolge
        sorted_participants = sorted(participants, key=lambda p: p.time3 if p.time3 is not None else float('-inf'), reverse=True)


        # Qualifiziere alle Teilnehmer mit Zeit >= 99 Sekunden
        qualified_participants = []
        for participant in participants:
            if participant.time3 is not None and participant.time3 >= 99:
                participant.round3_qualified = True
                qualified_participants.append(participant)

        # Fülle die Qualifikationen auf, bis mindestens 5 Teilnehmer qualifiziert sind
        for participant in sorted_participants:
            if len(qualified_participants) < 5:
                if not participant.round3_qualified :  # Nur nicht bereits qualifizierte Teilnehmer hinzufügen
                    participant.round3_qualified = True
                    qualified_participants.append(participant)
            else:
                break


    elif round == 'ZR':
        participants = Participant.query.all()

        # Sortiere Teilnehmer nach Zeit in der Zwischenrunde in absteigender Reihenfolge
        sorted_participants = sorted(participants, key=lambda p: p.toptime_Zwischenrunde if p.toptime_Zwischenrunde is not None else float('-inf'), reverse=True)

        # Setze das Feld zwischenrunde_qualified auf True für die besten zehn Teilnehmer
        for i, participant in enumerate(sorted_participants):
            if i < 10:
                participant.zwischenrunde_qualified = True
            else:
                participant.zwischenrunde_qualified = False

        # Speichere die Änderungen in der Datenbank (abhängig davon, wie du deine DB-Session verwaltest)
        db.session.commit()

   
    elif round == 'FINAL':
        participants = Participant.query.all()
        for participant in participants:
            participant.final_qualified = True

    db.session.commit()
    flash(f'Runde {round} abgeschlossen!', 'success')
    
    return redirect(url_for('main.index'))


@bp.route('/set_active/<int:id>', methods=['POST'])
@login_required
def set_active(id):
    Participant.query.update({Participant.active: False})
    active_participant = Participant.query.get(id)
    if active_participant:
        active_participant.active = True
    db.session.commit()
    flash('Active participant set successfully!', 'success')
    return redirect(url_for('main.index'))

@bp.route('/reset_results', methods=['POST'])
@login_required
def reset_results():
    participants = Participant.query.all()
    for participant in participants:
        participant.active = False
        participant.time1 = None
        participant.time2 = None
        participant.time3 = None
        participant.time4 = None
        participant.time5 = None
        participant.time6 = None
        participant.round1_qualified = False
        participant.round2_qualified = False
        participant.round3_qualified = False
        participant.zwischenrunde_qualified = False
        participant.final_qualified = False
    
    db.session.commit()
    flash('All fields have been reset.', 'success')
    return redirect(url_for('main.index'))

@bp.route('/reset_participants', methods=['POST'])
@login_required
def reset_participants():
    Participant.query.delete()
    db.session.commit()
    flash('Alle Teilnehmer wurden gelöscht.', 'success')
    return redirect(url_for('main.participant'))

@bp.route('/ranking')
def ranking():
    participants = Participant.query.all()
    rankings = sorted(participants, key=lambda p: (
            p.toptime_Finalrunde if p.toptime_Finalrunde is not None else float('-inf'),
            p.toptime_Zwischenrunde if p.toptime_Zwischenrunde is not None else float('-inf'),
            p.toptime_Vorrunde if p.toptime_Vorrunde is not None else float('-inf')
    ), reverse=True)

    return render_template('ranking.html', title='Rangliste', rankings=rankings)


 
