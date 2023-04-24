import os
from flask import Flask, render_template, request, url_for, flash, redirect
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from sqlalchemy import text
from datetime import datetime
import pandas as pd
import numpy as np

projpath = os.path.dirname(os.path.abspath(__file__))
database_file = "sqlite:///{}".format(os.path.join(projpath, "database.db"))

engine = create_engine(database_file)

# getting data from blizzard API
df_guilds = pd.read_csv('data/guilds.csv')
df_players = pd.read_csv('data/players2.csv')

df_guilds.to_sql('Guilds', database_file, if_exists = 'replace')
df_players.to_sql('Players', database_file, if_exists = 'replace') 

app = Flask(__name__) 
app.config['SQLALCHEMY_DATABASE_URI'] = database_file
db = SQLAlchemy(app)

# defining tables 
class Guilds(db.Model):
  id = db.Column(db.Integer, primary_key = True)
  name = db.Column(db.String(120), primary_key = False)
  #realm_id = db.Column(db.Integer, primary_key = False) 
  realm = db.Column(db.String(120), primary_key = False)
  region = db.Column(db.String(120), primary_key = False)

  def __repr__(self): 
    return "<guild name: {}>".format(self.name)

class Players(db.Model): 
  id = db.Column(db.Integer, primary_key = True)
  character_name = db.Column(db.String(120), primary_key = False)
  character_realm_slug = db.Column(db.String(120),primary_key = False) 
  player_class = db.Column(db.String(120), primary_key = False)
  guildID = db.Column(db.Integer, primary_key = False)
  helmet_name = db.Column(db.String(120), primary_key = False)
  helmet_id = db.Column(db.Integer, primary_key = False)
  shoulders_name = db.Column(db.String(120), primary_key = False)
  shoulders_id = db.Column(db.Integer, primary_key = False)
  chest_name = db.Column(db.String(120), primary_key = False)
  chest_id = db.Column(db.Integer, primary_key = False)
  legs_name = db.Column(db.String(120), primary_key = False)
  legs_id = db.Column(db.Integer, primary_key = False)

  def __repr__(self): 
    return "<name : {}>".format(self.character_name)

with app.app_context(): 
  db.create_all()

@app.route('/', methods=["GET", "POST"])
def main(): 
  if request.form: 
    guild = Guilds(name=request.form.get("name"), id=np.random.randint(0,90000), realm=request.form.get('realm'), region=request.form.get('region'))
    db.session.add(guild)
    db.session.commit()
  guilds = Guilds.query.all()
  return render_template("guilds.html", guilds=guilds)

@app.route('/addRoster', methods = ["GET", "POST"])
def addRoster(): 
  if request.form: 
    guildID = request.args.get('guildID')
    player = Players(character_name=request.form.get("name"), id=np.random.randint(0,90000), guildID=request.form.get('guildID'), player_class = request.form.get("class"))
    db.session.add(player)
    db.session.commit()
  players = Players.query.all()
  return redirect('/')

@app.route('/delete', methods = ["GET", "POST"]) 
def delete(): 
  id = request.form.get("id")
  guild = Guilds.query.filter_by(id=id).first() 
  db.session.delete(guild)
  db.session.commit() 
  return redirect("/")

@app.route('/deleteRoster', methods = ["GET", "POST"]) 
def deleteRoster(): 
  id = request.form.get("id")
  player = Players.query.filter_by(id=id).first() 
  db.session.delete(player)
  db.session.commit() 
  return redirect('/')

@app.route('/update', methods = ["GET", "POST"])
def update(): 
  newname = request.form.get("newname") 
  guildID = request.form.get("id")
  guild = Guilds.query.filter_by(id = guildID).first()
  guild.name = newname
  db.session.commit()
  return redirect("/")

@app.route('/updateRoster', methods = ["GET", "POST"])
def updateRoster(): 
  newname = request.form.get("newname") 
  characterID = request.form.get("id")
  player = Players.query.filter_by(id = characterID).first()
  player.character_name = newname
  db.session.commit()
  return redirect('/')

@app.route('/roster', methods = ["GET", "POST"])
def viewRoster(): 
  guildID = request.args.get('guildID')
  rqst = text('SELECT * FROM Players WHERE guildID = ' + guildID)
  with engine.connect() as conn: 
    result = conn.execute(rqst)
  return render_template("roster.html", players = result)

@app.route('/player', methods = ["GET", "POST"]) 
def viewClass(): 
  className = request.args.get('class')
  newRQST = text('SELECT DISTINCT s.helmet_name, COUNT(*) AS num from Players s WHERE player_class= ' + '"' + className + '"' + ' GROUP BY helmet_name UNION SELECT DISTINCT s.shoulders_name, COUNT(*) AS num from Players s WHERE player_class = ' + '"' + className + '"' + ' GROUP BY shoulders_name UNION SELECT DISTINCT s.chest_name, COUNT(*) AS num from Players s WHERE player_class =' + '"' + className + '"' + ' GROUP BY chest_name UNION SELECT DISTINCT s.legs_name, COUNT(*) AS num from Players s WHERE player_class=' + '"' + className + '"' + ' GROUP BY legs_name ORDER BY num DESC')
  with engine.connect() as conn: 
    result = conn.execute(newRQST)
  return render_template("items.html", players = result)


@app.route('/items', methods = ["GET", "POST"]) 
def viewItems(): 
  playerID = request.args.get('id')
  print(playerID)
  rqst = text('SELECT p.helmet_name, p.id FROM players p WHERE p.id = ' + playerID + ' UNION SELECT p.shoulders_name, p.id FROM players p WHERE p.id = ' + playerID + ' UNION SELECT p.chest_name, p.id  FROM players p WHERE p.id = ' + playerID + ' UNION SELECT p.legs_name, p.id FROM players p WHERE p.id = ' + playerID)
  with engine.connect() as conn: 
    result = conn.execute(rqst)
  return render_template("items2.html", players = result)

@app.route('/updateItem', methods = ["GET", "POST"]) 
def updateItem(): 
  playerID = request.form['id']
  itemName = request.form['itemName']
  newName = request.form['newname']
  #print(playerID, itemName, newName)
  player = Players.query.filter_by(id = playerID).first()
  if player.helmet_name == itemName: 
    player.helment_name = newName
  if player.shoulders_name == itemName: 
    player.shoulders_name = newName
  if player.chest_name == itemName: 
    player.chest_name = newName
  if player.legs_name == itemName: 
    player.legs_name = newName
  db.session.commit()
  return redirect('/')

@app.route('/deleteItem', methods = ["GET", "POST"]) 
def deleteItem(): 
  playerID = request.form.get('id')
  itemName = request.form.get('itemName')
  player = Players.query.filter_by(id = playerID).first()
  if player.helmet_name == itemName: 
    player.helment_name = ""
  if player.shoulders_name == itemName: 
    player.shoulders_name = ""
  if player.chest_name == itemName: 
    player.chest_name = ""
  if player.legs_name == itemName: 
    player.legs_name = ""
  db.session.commit()
  return redirect('/')

if __name__ == "__main__": 
  app.run(debug=True)





