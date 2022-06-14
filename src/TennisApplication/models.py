from src.TennisApplication import db, login_manager
from flask_login import UserMixin


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(20), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    password = db.Column(db.String(30), nullable=False)

    first_name = db.Column(db.String(20), nullable=False)
    last_name = db.Column(db.String(20), nullable=False)
    birth_date = db.Column(db.Date, nullable=False)
    phone_number = db.Column(db.String(16), nullable=False)
    city = db.Column(db.String(20), nullable=False)

    # _ = db.relationship('*', backref='author', lazy=True)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.image_file}', '{self.first_name}', " \
               f"'{self.last_name}', '{self.birth_date}', '{self.phone_number}', '{self.city}')"

    def get_id(self):
        return self.id


class Court(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    club_id = db.Column(db.Integer, db.ForeignKey('club.id'))
    court_number = db.Column(db.Integer, nullable=False)
    surface = db.Column(db.String(20), nullable=False)
    lights = db.Column(db.Boolean, nullable=False)
    roof = db.Column(db.Boolean, nullable=False)

    def isReserved(self, date_f, date_t):
        reservations = db.session.query(Reservation).all()
        for reservation in reservations:
            if reservation.court_id.data == self.data and reservation.date_from.data:
                pass


    def __repr__(self):
        return f"Court('{self.id}', {self.court_number}', {self.club_id}', '{self.surface}', '{self.lights}', '{self.roof}')"


class Reservation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    court_id = db.Column(db.Integer, db.ForeignKey('court.id'))
    date_from = db.Column(db.DateTime, nullable=False)
    date_to = db.Column(db.DateTime, nullable=False)
    tournament_id = db.Column(db.Integer, db.ForeignKey('tournament.id'))




class Tournament(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date_from = db.Column(db.DateTime, nullable=False)
    club_id = db.Column(db.Integer, db.ForeignKey('club.id'))
    organizer_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    max_players = db.Column(db.Integer, nullable=False)
    winner_rewards = db.Column(db.String(30), nullable=True)
    min_skill_lvl = db.Column(db.Integer, nullable=True)
    is_registration_closed = db.Column(db.Boolean, nullable=False)

    def __repr__(self):
        return f"Tournament('{self.date_from}', '{self.club_id}', '{self.organizer_id}', '{self.max_players}', " \
               f"'{self.winner_rewards}', '{self.min_skill_lvl}', '{self.is_registration_closed}')"


class Club(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), unique=True, nullable=False)
    logo = db.Column(db.String(20), nullable=True, default='default.jpg')
    location = db.Column(db.String(20), nullable=False)
    about = db.Column(db.String(20), nullable=True)

    def __repr__(self):
        return f"Club('{self.id}', '{self.name}', '{self.logo}', '{self.location}', " \
               f"{self.about})"


class TournamentUser(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    tournament_id = db.Column(db.Integer, db.ForeignKey('tournament.id'))


class Match(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    player_1 = db.Column(db.Integer, db.ForeignKey('user.id'))
    player_2 = db.Column(db.Integer, db.ForeignKey('user.id'))
    score = db.Column(db.Integer, nullable=True)
    is_finished = db.Column(db.Boolean, nullable=False)
