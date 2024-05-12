import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from neo4j import GraphDatabase

# Spotify API credentials
CLIENT_ID = ''
CLIENT_SECRET = ''

# Connect to Spotify API
sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id=CLIENT_ID, client_secret=CLIENT_SECRET))

# Connect to Neo4j
uri = ""
username = ""
password = ""
driver = GraphDatabase.driver(uri, auth=(username, password))

def get_genre_tracks(genre):
    tracks = []
    results = sp.search(q=f'genre:"{genre}"', type='track', limit=10)
    for track in results['tracks']['items']:
        tracks.append((track['name'], track['artists'][0]['name']))
    return tracks

def create_graph(user, genre, tracks):
    with driver.session() as session:
        session.run("MERGE (u:User {name: $name})", name=user)
        session.run("MERGE (g:Genre {name: $name})", name=genre)
        for track in tracks:
            session.run("MERGE (t:Track {name: $name, artist: $artist})", name=track[0], artist=track[1])
            session.run("MATCH (u:User {name: $user}), (g:Genre {name: $genre}), (t:Track {name: $track_name, artist: $artist}) "
                        "MERGE (u)-[:LIKES]->(g) "
                        "MERGE (g)-[:INCLUDES]->(t)", user=user, genre=genre, track_name=track[0], artist=track[1])

def main():
    user = input("Ingresa tu nombre: ")
    genre = input("Ingresa tu género músical favorito: ")
    tracks = get_genre_tracks(genre)
    print("Aquí están las canciones que recomendamos que escuches: ")
    for idx, track in enumerate(tracks, start=1):
        print(f"{idx}. {track[0]} by {track[1]}")
    create_graph(user, genre, tracks)
    print("Graph created in Neo4j")

if __name__ == "__main__":
    main()
