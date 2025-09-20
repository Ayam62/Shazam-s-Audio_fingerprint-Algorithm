import numpy as np
# from scipy.io import wavfile
import librosa #to read the audio file, librosa is needed
import matplotlib.pyplot as plt
from pymongo import MongoClient
import certifi
from pathlib import Path
import sounddevice as sd
from scipy.io.wavfile import write
import os

username=os.getenv("username")
password=os.getenv("password")


uri = f"mongodb+srv://{username}:{password}@cluster0.w7tmw.mongodb.net/?retryWrites=true&w=majority"
client = MongoClient(uri, tls=True, tlsCAFile=certifi.where())
try:
    db = client.admin
    db.command("ping")
    print("Connected to MongoDB Atlas!")
except Exception as e:
    print("Connection error:", e)
    
db = client["shazam_db"]
collection = db["fingerprints"]

def convert_to_spectrogram(audio):
    waveform,sampling_rate=librosa.load(audio) #waveform has the array of amplitudes and samplig_rate represents the no. of samples taken persecond to represent the signal
    print(waveform,sampling_rate) 
    STFT=librosa.stft(waveform)
    Sound_DB_2D=librosa.amplitude_to_db(np.abs(STFT),ref=np.max) #intialll y the STFT was complex valued, the function librosa.amplitude_to_db converts its inner value into logarithmic scale that human ears can perceive. The first inner value is np.abs(STFT), this makes the complex value which represented both magnitude and phase now gives only the magnitude. The 2nd term i.e ref=np.(max) normalizes the value such that the loudest value in is 0b and other sounds are in negative axis .
    return Sound_DB_2D,sampling_rate


def spectrogram_plotter(sound_amplitude_DB_2D,sr):
    librosa.display.specshow(sound_amplitude_DB_2D,sr=sr, x_axis='time',y_axis='hz', cmap='magma')
    plt.colorbar(label='Intensity (dB)')
    plt.show()


    
    

# spectrogram_plotter(sound_amplitude_DB_2D,sr)

def local_maxima_finder(sound_DB_2D):
    window_size=50
    peaks=[]
    threshold_intensity=-40
   
    # print(sound_DB_2D.shape)
    for i in range(0, sound_DB_2D.shape[0], window_size//2):
        for j in range(0, sound_DB_2D.shape[1], window_size//2):
        
            
            block=sound_DB_2D[i:i+window_size,j:j+window_size] #making block out of the 2d spectrogram
            
            max_amp_pixel=np.unravel_index(np.argmax(block),block.shape) # Finding the maximum intensity's pixel in the respective block
            local_max_freq=i+max_amp_pixel[0] # because block is local so its shape is always from 0 to 20 , both horizontally and veritically, so it is added by i and j to make it global
            local_max_time=j+max_amp_pixel[1]
            # print(local_max_freq,local_max_time)
            local_max_amplitude_DB=sound_DB_2D[local_max_freq,local_max_time]
            
            if(local_max_amplitude_DB>threshold_intensity):
                peaks.append((local_max_freq,local_max_time,local_max_amplitude_DB))
            
    return peaks


# print(peaks)


    

def peak_plotter(peaks, sr):
    times = [t for f,t,amp in peaks]
    freqs = [f for f,t,amp in peaks]

    times_sec = librosa.frames_to_time(times, sr=sr)
    freqs_hz = librosa.fft_frequencies(sr=sr)
    freqs_sec = [freqs_hz[f] for f in freqs]

    plt.scatter(times_sec, freqs_sec, s=10)
    plt.xlabel("Time (s)")
    plt.ylabel("Frequency (Hz)")
    plt.show()

    
# peak_plotter(peaks)
#peaks=[(freq,time,amplitude)]

def hashing(peaks):
    hashes = []
    for i in range(len(peaks)-1):
        for k in range(1, 6):  # connect to next 5 peaks
            if i+k < len(peaks):
                f1, t1, _ = peaks[i]# dash is ignored because amplitude is not needed
                f2, t2, _ = peaks[i+k]
                delta_t = t2 - t1
                hashes.append({
                    "f1": int(f1),
                    "f2": int(f2),
                    "delta_t": int(delta_t),
                    "t_anchor": int(t1)  # absolute time/frame of anchor
                })
    return hashes




def store_in_DB(hashes, song_id, collection):
    docs = [{"song_id": song_id, **h} for h in hashes]#**h in hashes means everything inside hahes
    collection.insert_many(docs)

    
    
#######This code is only to upload songs for the first time
 
# songs_folder = Path("songs")
# audio_files = list(songs_folder.glob("*.wav"))
# for file_path in audio_files:
#     song_id = file_path.stem  # filename without extension
#     print(file_path)

#     sound_amplitude_DB_2D,sr=convert_to_spectrogram(file_path) 
#     peaks=local_maxima_finder(sound_amplitude_DB_2D) 
#     hashes=hashing(peaks)
#     store_in_DB(hashes,song_id,collection)


###### query to ask  for new music of 10 seconds
def record_audio():
    sampling_rate=22050
    duration=10
    filename="recorded.wav"
    print("Recording the audio....................")

    recording=(sd.rec(int(duration*sampling_rate),samplerate=sampling_rate,channels=1))
    sd.wait()
    print("Recording finished. You are ready to go!")

    ##saving the recoridng
    write(filename,sampling_rate,recording)
    print(f"Saved recording as {filename}")
    return filename

filename=record_audio()
# filename="recorded.wav"

def create_fingerprint_recorded_audio(filename):
    sound_amplitude_DB_2D,sr=convert_to_spectrogram(filename) 
    peaks=local_maxima_finder(sound_amplitude_DB_2D)
    hashes=hashing(peaks) 
    return hashes

hashes_to_compare=create_fingerprint_recorded_audio(filename)

song_ids = [ "Mitwa", "Laal_Peeli_Akhiyaan","country_road","Breathless (Breathless) (Raag.Fm)"]


from collections import defaultdict, Counter

def match_query(song_ids, query_hashes, collection):##query hashes are hashes to compare
    
    contributions = []
    query_dict = defaultdict(list)
    
    for h in query_hashes:
        key = (h['f1'], h['f2'], h['delta_t'])
        query_dict[key].append(h['t_anchor'])

    for song_id in song_ids:
        cursor = collection.find({"song_id": song_id})
        db_dict = defaultdict(list)
        for doc in cursor:
            key = (doc['f1'], doc['f2'], doc['delta_t'])
            db_dict[key].append(doc['t_anchor'])

        offset_counter = Counter()
        for key, query_times in query_dict.items():
            if key in db_dict:
                for t_db in db_dict[key]:
                    for t_query in query_times:
                        offset = t_db - t_query
                        offset_counter[offset] += 1

        contribution = max(offset_counter.values()) if offset_counter else 0
        contributions.append((song_id, contribution))

    return sorted(contributions, key=lambda x: x[1], reverse=True)



result=match_query(song_ids, hashes_to_compare,collection)
print(result)




    
        



    



     
    
    
    
    














    




        
    
    







   
    
    