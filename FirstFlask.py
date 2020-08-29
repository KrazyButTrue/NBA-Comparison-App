from flask import Flask, render_template, url_for, request, redirect
from nba_api.stats.static import players
from nba_api.stats.endpoints import commonplayerinfo, playercareerstats
import pandas as pd
from flask_sqlalchemy import SQLAlchemy
import time

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///Players.db'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

class Players(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(100))

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        new_player = request.form.get('player')

        if new_player:
            new_player_obj = Players(name=new_player)
            db.session.add(new_player_obj)
            db.session.commit()

    players_db = Players.query.all()
    #time.sleep(2)
    nba_players = players.get_active_players()
    time.sleep(2)
    player_data = []
    try:
        for x in players_db:
            player = [player for player in nba_players if player['full_name'] == x.name][0]
            player_id = player['id']
            player_info = commonplayerinfo.CommonPlayerInfo(player_id=player_id)
        #time.sleep(2)
            player_stats = player_info.player_headline_stats.get_data_frame()
            #time.sleep(2)

            players_dict = {
                'name': x.name,
                'year': player_stats.at[0,"TimeFrame"],
                'PTS': player_stats.at[0,"PTS"],
                'AST': player_stats.at[0,"AST"],
                'REB': player_stats.at[0,"REB"],
                'PIE': player_stats.at[0,"PIE"]
            }

            player_data.append(players_dict)
    except IndexError:
        return redirect(url_for('delete'))
    return render_template("index.html", title="Home", player_data=player_data)

@app.route('/delete', methods=['POST', 'GET'])
def delete():
    db.session.query(Players).delete()
    db.session.commit()
    return redirect(url_for('home'))

if __name__ == "__main__":
    db.create_all()
    app.run(debug = True)
