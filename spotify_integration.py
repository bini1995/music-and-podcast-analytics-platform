import requests
import base64
from models import db, StreamingMetrics
from dotenv import load_dotenv
import os

load_dotenv()

CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")

def get_spotify_token() -> str:
    """Retrieve an access token from Spotify."""
    url = "https://accounts.spotify.com/api/token"
    headers = {
        "Authorization": "Basic " + base64.b64encode(f"{CLIENT_ID}:{CLIENT_SECRET}".encode()).decode()
    }
    data = {"grant_type": "client_credentials"}
    
    try:
        response = requests.post(url, headers=headers, data=data)
        response.raise_for_status()
        token = response.json().get("access_token")
        if token:
            print(f"[INFO] Retrieved Spotify Token: {token[:10]}...")  # Mask token for security
        return token
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] Failed to get Spotify token: {e}")
        return None

def search_spotify(query, search_type="track"):
    """Search for a song on Spotify."""
    token = get_spotify_token()
    if not token:
        print("[ERROR] Failed to authenticate with Spotify API.")
        return {}

    url = "https://api.spotify.com/v1/search"
    headers = {"Authorization": f"Bearer {token}"}
    params = {"q": query, "type": search_type, "limit": 5}

    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        print("[INFO] Spotify search successful.")
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] Failed to search Spotify: {e}")
        return {}
    

def store_search_results(query, app):
    """Fetch Spotify search results and store them with analytics."""
    token = get_spotify_token()
    headers = {"Authorization": f"Bearer {token}"}
    params = {"q": query, "type": "track", "limit": 5}
    
    response = requests.get("https://api.spotify.com/v1/search", headers=headers, params=params)
    
    if response.status_code == 200:
        results = response.json()["tracks"]["items"]
        with app.app_context():
            for track in results:
                song_name = track["name"]
                artist_name = track["artists"][0]["name"]
                album_name = track["album"]["name"]
                plays = track["popularity"]
                saves = track.get("saves", 0)  # Assuming API provides saves count
                shares = track.get("shares", 0)  # Assuming API provides shares count
                likes = track.get("likes", 0)  # Assuming API provides likes count

                existing_song = StreamingMetrics.query.filter_by(song_name=song_name).first()
                if existing_song:
                    existing_song.plays += plays
                    existing_song.saves = (existing_song.saves or 0) + saves
                    existing_song.shares = (existing_song.shares or 0) + shares
                    existing_song.likes = (existing_song.likes or 0) + likes

                else:
                    new_entry = StreamingMetrics(
                        song_name=song_name,
                        artist_name=artist_name,
                        album_name=album_name,
                        plays=plays,
                        saves=saves,
                        shares=shares,
                        likes=likes
                    )
                    db.session.add(new_entry)
            
            db.session.commit()
    else:
        print(f"[ERROR] Spotify API Error: {response.status_code}")


if __name__ == "__main__":
    query = "Shape of You"  # Replace with any song name
    from app import app  # Import app only when running the script directly
    store_search_results(query, app)
