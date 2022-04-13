from __future__ import print_function
from flask import Flask, render_template
from flask import request
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import pickle
from dotenv import load_dotenv
import os
#code which helps initialize our server
load_dotenv()
client_credentials_manager = SpotifyClientCredentials(os.getenv("SPOTIFY_CLIENT_ID"), os.getenv("SPOTIFY_CLIENT_SECRET"))

scaler_mlp = pickle.load(open("models/3yp_scaler_mlp_smote.pkl","rb"))
mlp = pickle.load(open("models/3yp_mlp_smote.pkl","rb"))

scaler_mlp_online = pickle.load(open("models/3yp_scaler_mlp_online.pkl","rb"))
mlp_online = pickle.load(open("models/3yp_mlp_online.pkl","rb"))

scaler_svm = pickle.load(open("models/3yp_scaler_svm.pkl","rb"))
svm = pickle.load(open("models/3yp_svm.pkl","rb"))

scaler_svm_smote = pickle.load(open("models/3yp_scaler_svm_smote.pkl","rb"))
svm_smote = pickle.load(open("models/3yp_svm_smote.pkl","rb"))

scaler_log = pickle.load(open("models/3yp_scaler_log.pkl","rb"))
log = pickle.load(open("models/3yp_log.pkl","rb"))

print("MLP loaded", mlp)
print()
print("MLP Online loaded", mlp_online)
print()
print("SVM with sel features loaded", svm)
print()
print("SVM SMOTE loaded", svm_smote)
print()
print("Log. Reg loaded", log)

sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
app = Flask(__name__)

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def page_not_found(e):
    return render_template('500.html'), 500

@app.route('/')
def index():
    return render_template('index.html');

@app.route('/search')
def searchAndPredictSong():
	query = request.args.get('q')
	selectedModel = request.args.get('sel')
	imageLink = ""
	trackName = ""
	artistName = ""
	isPopular = ""
	spotifyURL = ""
	if query != None and query != "":
		results = sp.search(q='track:' +  query, limit=1, type='track')
		# print(results)
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
				data.append([energy, liveness, tempo, speechiness, acousticness, instrumentalness, time_signature,
				      danceability, key, duration_ms, loudness, valence, mode])
				# print(data)
				#scaled_data = scaler.transform(data)
				if selectedModel == "SVM":

					usingCls = "SVM"
					print("USING SVM")
					data_with_fs = []
					data_with_fs.append([energy, tempo, speechiness, instrumentalness, time_signature, duration_ms, loudness])
					scaled_data_with_fs = scaler_svm.transform(data_with_fs)
					predicted_label = svm.predict(scaled_data_with_fs)
					predicted_probablities = svm.predict_proba(scaled_data_with_fs)
					isPopular = predicted_label[0]
				elif selectedModel == "SVM SMOTE":
					usingCls = "SVM SMOTE"
					print("USING SVM SMOTE")
					data_with_fs = []
					data_with_fs.append([energy,tempo,speechiness,loudness,valence])
					scaled_data_with_fs = scaler_svm_smote.transform(data_with_fs)
					predicted_label = svm_smote.predict(scaled_data_with_fs)
					predicted_probablities = svm_smote.predict_proba(scaled_data_with_fs)
					isPopular = predicted_label[0]
				elif selectedModel == "Log. Reg.":
					usingCls = "Log. Reg."
					print("USING Log. Reg.");
					data_with_fs = []
					data_with_fs.append([energy, tempo, instrumentalness, danceability, loudness, valence])
					scaled_data_with_fs = scaler_log.transform(data_with_fs)
					predicted_label = log.predict(scaled_data_with_fs)
					predicted_probablities = log.predict_proba(scaled_data_with_fs)
					isPopular = predicted_label[0]
				elif selectedModel == "MLP":
					usingCls = "MLP"
					print("USING MLP");
					scaled_data = scaler_mlp.transform(data)
					predicted_label = mlp.predict(scaled_data)
					predicted_probablities = mlp.predict_proba(scaled_data)
					isPopular = predicted_label[0]
				elif selectedModel == "MLP Online":
					usingCls = "MLP Online"
					print("USING MLP Online")
					scaled_data = scaler_mlp_online.transform(data)
					predicted_label = mlp_online.predict(scaled_data)
					predicted_probablities = mlp_online.predict_proba(scaled_data)
					isPopular = predicted_label[0]
					y = []
					if popularity >= 90:
						y.append(1)
					else:
						y.append(0)
					print("Learning new example with popularity: ", popularity)
					mlp_online.partial_fit(scaled_data, y)
				else:
					usingCls = "MLP"
					print("USING MLP");
					scaled_data = scaler_mlp.transform(data)
					predicted_label = mlp.predict(scaled_data)
					predicted_probablities = mlp.predict_proba(scaled_data)
					isPopular = predicted_label[0]
				
				print("Predicted label is : ", predicted_label)
				print(round(predicted_probablities[0][0],3),",", round(predicted_probablities[0][1],3))
				print("Actual popularity is: ", popularity)
		else:
			message = "No song found for query: " + query
			return render_template('index.html', message = message)
	else:
		message = "Try 7 rings - Ariana Grande, Wow - Post Malone, thank u next - Ariana Grande"
		return render_template('index.html', message = message)
	return render_template('index.html', imageLink = imageLink, artistName = artistName,
							spotifyURL = spotifyURL, trackName=trackName, isPopular=isPopular, usingCls=usingCls)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')