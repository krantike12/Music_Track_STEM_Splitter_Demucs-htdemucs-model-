import subprocess
import os
import librosa
from flask import Flask, redirect, render_template, json, jsonify, request, send_from_directory


app = Flask(__name__)

Output_dir = "outputs"


@app.route('/file')
def file():
    return render_template('index.html')


# def extract_mfcc(path, n_mfcc=13):
#     y, sr = librosa.load(input_path)
#     genre_mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=n_mfcc)
#     genre_mfcc_mean = genre_mfcc.mean(axis=1)
#     return genre_mfcc_mean
#     # Placeholder for genre detection logic

# genres = [
#     "blues",
#     "classical",
#     "country",
#     "disco",
#     "hiphop",
#     "jazz",
#     "metal",
#     "pop",
#     "reggae",
#     "rock"
# ]
   
    
#     # Dummy logic to select a genre based on the mean MFCC values
# x = [] #features
# y = [] #genres label
    
    
# for genre in genres:
#     files = os.listdir('uploads')
#     for file in files:
#         #print(file)
#         input_path = os.path.join('uploads', file)
#         vector = extract_mfcc(path=input_path)
#         #print(vector)
#         x.append(vector)
#         y.append(genre)
#         #print(input_path)
        


@app.route('/upload-music', methods = ["POST"])
def split_Auido():
    file = request.files['myFile']
    
    #librosa set up
   
    file_id = os.path.splitext(file.filename)[0]
    if not file:
        return jsonify({"No File Received"}), 500
    
    #upload to folder
    input_path = os.path.join('uploads', file.filename)
    file.save(input_path)
    print(input_path)
    print(file)

    y, sr = librosa.load(input_path)
    
    #give tempo 
    tempo, beats = librosa.beat.beat_track(y=y, sr=sr)
    print(f"Estimated tempo: {tempo} beats per minute")
    
    #key detection
    chromagram = librosa.feature.chroma_stft(y=y, sr=sr)
    keys = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
    index = chromagram.mean(axis=1).argmax() 
    key = keys[index]
    print(f"Estimated key: {key}")

    #subprocess
    subprocess.run([
        "demucs",
        "--mp3",
        "-o",
        Output_dir,
        input_path
    ], check=True)
    
    #folder verification 
    Output_Folder = os.path.join(Output_dir, "htdemucs", file_id)
    if not os.path.exists(Output_Folder):
        return jsonify({"No such folder or file exists"})
    
    files = os.listdir(Output_Folder)
    results = {
        "metadata" :{
            
        },
        "audios" : {
            
        }
    }
    for f in files:
        stem_name = os.path.splitext(f)[0]
        results["audios"][stem_name] = f"/htdemucs/{file_id}/{f}"
    results['metadata']["Tempo"] = str(tempo) + "BPM"
    results['metadata']["Key"] = key 
    results["metadata"]["Sample Rate"] = str(sr) + "Hz"
    song_duration = librosa.get_duration(y=y, sr=sr)
    song_duration = round((1 / 60) * song_duration, 2)
    results["metadata"]["Duration"] = str(song_duration) + "mins"
    results["metadata"]["Title"] = file.filename 
    return results


@app.route('/outputs/<path:file_path>', methods=["post", "get"])
def show_file(file_path):
    return send_from_directory("outputs", file_path)



    

if __name__ == "__main__":  
    app.run(debug=True)