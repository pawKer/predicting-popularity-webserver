from flask import Flask, render_template
from flask import request
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import config
import pickle
#code which helps initialize our server
client_credentials_manager = SpotifyClientCredentials(config.client_id, config.client_secret)
model = pickle.load(open("model.pkl","rb"))
doOnlineLearn = False
scaler = pickle.load(open("scaler.pkl","rb"))
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html');

@app.route('/search')
def malone():
	query = request.args.get('q')
	imageLink = ""
	trackName = ""
	artistName = ""
	audioFeatures = ""
	isPopular = ""
	spotifyURL = ""
	if query != "":
		print(query)
		results = sp.search(q='track:' +  query, limit=1, type='track')
		print(results)
		if results['tracks']['items'] != []:
			imageLink = results['tracks']['items'][0]['album']['images'][0]['url']
			artistName = results['tracks']['items'][0]['album']['artists'][0]['name']
			trackName = results['tracks']['items'][0]['name']
			trackId = results['tracks']['items'][0]['id']
			spotifyURL = results['tracks']['items'][0]['external_urls']['spotify']
			popularity = results['tracks']['items'][0]['popularity']
			features = sp.audio_features([trackId])
			if features[0] != None:
				energy = features[0]['energy']
				liveness = features[0]['liveness'] 
				tempo = features[0]['tempo']
				speechiness = features[0]['speechiness']
				acousticness = features[0]['acousticness']
				instrumentalness = features[0]['instrumentalness']
				time_signature = features[0]['time_signature']
				danceability = features[0]['danceability']
				key = features[0]['key']
				duration_ms = features[0]['duration_ms']
				loudness = features[0]['loudness']
				valence = features[0]['valence']
				mode = features[0]['mode']
	            
				# Create a new row of data for each song using the features above
				data = []
				newRow = []
				newRow = data.append([energy, liveness, tempo, speechiness, acousticness, instrumentalness, time_signature,
				      danceability, key, duration_ms, loudness, valence, mode])
				scaled_data = scaler.transform(data)
				predicted_label = model.predict(scaled_data)
				isPopular = predicted_label[0]
				y = []
				if popularity >= 90:
					y.append(1)
				else:
					y.append(0)
				if doOnlineLearn :
					print("Learning new example with popularity: ", popularity)
					model.partial_fit(scaled_data, y)
				print("Predicted label is : ", predicted_label)
		else:
			message = "No song found for query: " + query
			return render_template('index.html', message = message)
	return render_template('index.html', imageLink = imageLink, artistName = artistName,
							spotifyURL = spotifyURL, trackName=trackName, isPopular=isPopular)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')