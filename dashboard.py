from flask import Flask, render_template, jsonify
from models import db, StreamingMetrics
import plotly.express as px
import pandas as pd

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://username:password@localhost/musicdb"
db.init_app(app)

@app.route("/")
def index():
    """Main dashboard page."""
    return render_template("dashboard.html")

@app.route("/spotify/data")
def spotify_data():
    """Fetches streaming metrics from the database for visualization."""
    metrics = StreamingMetrics.query.all()
    data = [{
        "song_name": m.song_name,
        "artist_name": m.artist_name,
        "plays": m.plays,
        "likes": m.likes,
        "shares": m.shares,
        "saves": m.saves
    } for m in metrics]
    return jsonify(data)

@app.route("/spotify/visuals")
def spotify_visuals():
    """Generates interactive Spotify analytics charts."""
    metrics = StreamingMetrics.query.all()
    df = pd.DataFrame([{
        "Song": m.song_name,
        "Artist": m.artist_name,
        "Plays": m.plays,
        "Likes": m.likes,
        "Shares": m.shares,
        "Saves": m.saves
    } for m in metrics])

    # Generate visualizations
    fig1 = px.bar(df, x="Song", y="Plays", title="Most Played Songs")
    fig2 = px.bar(df, x="Artist", y="Plays", title="Top Artists by Plays")
    
    return jsonify({
        "most_played_songs": fig1.to_json(),
        "top_artists": fig2.to_json()
    })

if __name__ == "__main__":
    app.run(debug=True)
