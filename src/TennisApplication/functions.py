from wtforms import ValidationError
from wtforms.fields import datetime
from flask_login import current_user
from TennisApplication import db
from TennisApplication.models import Tournament, Club, Match, Reservation


def generate_matches(tournament_id):
    def nextHour(date):
        to_add = datetime.timedelta(hours=1)
        return date + to_add
    tournament = db.session.query(Tournament).filter_by(id=tournament_id)
    club = db.session.query(Club).filter_by(id=tournament.club_id)
    if not tournament.isRegistrationClosed:
        raise ValidationError('Registration is not closed')
    players = tournament.getPlayers()
    terms = len(players)-1
    courts = club.getCourts()
    curr_date = tournament.from_date
    for i in range(0,terms):
        cnt= 0
        while courts[cnt].isReserved(curr_date):
            cnt+=1
            if cnt > len(courts):
                curr_date = nextHour(curr_date)
                cnt=0
                break
        new_match = None
        if len(players)<i*2:
            new_match = Match(player_1= players[i*2],player_2= players[i*2+1],is_finished = False)
            db.session.add(new_match)
        new_reservation = Reservation(user_id=current_user.id,date_from = curr_date,date_to = nextHour(curr_date), court_id=courts[cnt],match_id=new_match,tournament_id=tournament_id)
        db.session.add(new_reservation)
    db.session.commit()
    return True

