import os
import secrets
from datetime import datetime, time
from PIL import Image
from flask import render_template, url_for, flash, redirect, request
from src.TennisApplication.forms import *
from src.TennisApplication import app, db, bcrypt
from src.TennisApplication.models import User, Tournament, Club, Reservation, Court
from flask_login import login_user, current_user, logout_user, login_required
from sqlalchemy import and_


@app.route("/")
@app.route("/home")
def home():
    def get_club_names():
        club_name_rows = Club.query.with_entities(Club.name).all()
        club_names = [row[0] for row in club_name_rows]
        return club_names
    club_names = get_club_names()
    return render_template('home.html', club_names=club_names)


@app.route("/about")
def about():
    return render_template('about.html', title='About')


@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password,
                    first_name=form.first_name.data, last_name=form.last_name.data, birth_date=form.birth_date.data,
                    phone_number=form.phone_number.data, city=form.city.data)
        db.session.add(user)
        db.session.commit()
        flash(f'{form.username.data} created account! You are able to log in', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route("/login", methods=['GET', 'POST'])
def login():

    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Unsuccessful login. Check username and password', 'danger')

    return render_template('login.html', title='Login', form=form)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))


def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_name = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static', 'profile_pictures', picture_name)

    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_name


@app.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccount()
    if form.validate_on_submit():
        if form.picture.data:
            picture_name = save_picture(form.picture.data)
            current_user.image_file = picture_name
        current_user.username = form.username.data
        current_user.email = form.email.data
        current_user.first_name = form.first_name.data
        current_user.last_name = form.last_name.data
        current_user.birth_date = form.birth_date.data
        current_user.phone_number = form.phone_number.data
        current_user.city = form.city.data
        db.session.commit()
        flash('Your account has been updated', 'success')
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
        form.first_name.data = current_user.first_name
        form.last_name.data = current_user.last_name
        form.birth_date.data = current_user.birth_date
        form.phone_number.data = current_user.phone_number
        form.city.data = current_user.city
    image_file = url_for('static', filename=os.path.join('profile_pictures', current_user.image_file))
    return render_template('account.html', title='Account', image_file=image_file, form=form)


@app.route("/reservation", methods=['GET', 'POST'])
def reservation():

    def get_court(club_id, court_number):
        court = Court.query.filter(Court.club_id == club_id and Court.court_number == court_number).first()
        return court

    def get_reservations(date, court):
        reservations = Reservation.query.filter(and_(Reservation.date_from >= date),
                                                Reservation.court_id == court.id).all()
        reservation_list = [list(range(reservation.date_from.hour, reservation.date_to.hour))
                            for reservation in reservations]
        flatten_list = [hours for reservation in reservation_list for hours in reservation]
        return flatten_list

    form = FilterReservations()
    reserve = MakeReservation()
    if request.method == 'GET':
        show = False
        reservations = ()
        club_id, date, court_number = None, None, None
    elif request.form.get('filter'):
        show = True
        date = form.date.data
        court_number = form.court_number.data
        club_id = form.club_id.data
        court = get_court(club_id, court_number)
        reservations = get_reservations(date, court)
    elif request.form.get('submit'):
        show = True
        date = reserve.date.data
        court_number = reserve.court_number.data
        club_id = reserve.club_id.data
        court = get_court(club_id, court_number)
        reservations = get_reservations(date, court)
        available_hours = [hour not in reservations for hour in range(reserve.hour_from.data, reserve.hour_to.data)]
        if False not in available_hours:
            date_from = datetime.combine(reserve.date.data, time(reserve.hour_from.data))
            date_to = datetime.combine(reserve.date.data, time(reserve.hour_to.data))
            new_reservation = Reservation(user_id=current_user.id, court_id=court.id, date_from=date_from,
                                          date_to=date_to)
            db.session.add(new_reservation)
            db.session.commit()
            flash('You committed reservation succesfully', 'success')
            redirect(url_for('home'))
        else:
            flash('Unable to commit reservation', 'danger')
    return render_template('reservation.html', title='Reservation', reservations=reservations, form=form, show=show,
                           club_id=club_id, court_number=court_number, reserve=reserve)


@app.route("/tournament", methods=['GET', 'POST'])
def tournament():
    tournaments1 = db.session.query(Tournament).all()
    tournaments = []
    for tournament in tournaments1:
        tournaments.append((tournament.id, tournament.club_id, tournament.max_players))
    return render_template('tournament.html', title='Tournament', tournaments=tournaments)


@app.route("/tournament_form", methods=['GET', 'POST'])
def tournament_form():
    if not current_user.is_authenticated:
        return redirect(url_for('home'))
    form = TournamentForm()
    if form.validate_on_submit():
        tournament12 = Tournament(date_from=form.date.data, club_id=form.club_id.data,
                                  organizer_id=current_user.get_id(), winner_rewards=form.winner_rewards.data,
                                  min_skill_lvl=form.min_skill_lvl.data, max_players=form.max_players.data,
                                  is_registration_closed=False)
        print(tournament12)
        db.session.add(tournament12)
        db.session.commit()
        flash('tournament added', 'success')
        return redirect(url_for('tournament'))
    return render_template('tournament_form.html', title='Tournament_form', form=form)

@app.route("/tournament_details/<id_t>", methods=['GET', 'POST'])
def tournament_details(id_t):
    tournaments1 = db.session.query(Tournament).all()
    tournament= tournaments1[int(id_t)-1]
    print(tournament)
    # tournament = None
    # for tournament2 in tournaments1:
    #     if tournament2.id == id_t:
    #         print("hi")
    #         tournament = tournament2
    #         break
    #
    # print(tournament)

    return render_template('tournament_details.html', title='Tournament_details', tournament=tournament)


