from sqlalchemy.sql import text
from app import app, db

# Add index to 'song_name' column in the StreamingMetrics table
with app.app_context():
    db.session.execute(text("CREATE INDEX IF NOT EXISTS idx_song_name ON streaming_metrics (song_name);"))
    db.session.commit()
    print("Index added to 'song_name' column.")

