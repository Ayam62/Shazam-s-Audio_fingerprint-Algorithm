# Audio Fingerprinting & Song Recognition (Shazam Algorithm Demo)

This project is a Python implementation of a simplified Shazam-like audio fingerprinting system. It demonstrates how to extract robust audio fingerprints from music, store them in a database, and recognize songs from short audio clips using signal processing and database search.

---
## Demo Video
Watch the demo here:  
👉 [Audio Fingerprinting Demo Video](https://drive.google.com/file/d/1tgwF7rcNTv8H86TNbTP723MtYgSxCSxc/view?usp=drive_link)

###  Features

-   **Spectrogram Generation:** Converts audio files into spectrograms using `librosa`.
-   **Peak Detection:** Finds local maxima in the spectrogram to identify robust audio features.
-   **Fingerprint Hashing:** Hashes pairs of peaks to create unique fingerprints.
-   **MongoDB Storage:** Stores fingerprints for each song in a MongoDB Atlas database.
-   **Audio Recording:** Records 10-second audio clips for querying.
-   **Song Matching:** Compares recorded/query fingerprints against the database to identify the song.

---

## 📂 Project Structure
**audio-fingerprint/**
- ├── `audio_fingerprint.py` → Main code: fingerprinting, DB, matching  
- ├── `songs/` → Folder for reference `.wav` songs  
- ├── `recorded.wav` → Temporary file for recorded audio  
- ├── `requirements.txt` → Python dependencies  
- └── `README.md` → This file  



###  Setup & Installation

1.  **Clone the repo**

    ```bash
    git clone [https://github.com/yourusername/audio-fingerprint-demo.git](https://github.com/yourusername/audio-fingerprint-demo.git)
    cd audio-fingerprint-demo
    ```

2.  **Install dependencies**

    ```bash
    pip install -r requirements.txt
    ```

3.  **MongoDB Atlas Setup**

    -   Create a free MongoDB Atlas cluster.
    -   Add your username/password as environment variables:

    ```bash
    export username='your_mongodb_username'
    export password='your_mongodb_password'
    ```

4.  **Add Reference Songs**

    -   Place `.wav` files in the `songs` folder.

---

###  How It Works

1.  **Fingerprinting Songs**
    -   The code extracts spectrogram peaks and hashes them for each song.
    -   Fingerprints are stored in MongoDB with a song ID.

2.  **Querying (Recognition)**
    -   Record a 10-second audio clip.
    -   Extract fingerprints from the recording.
    -   Match fingerprints against the database to find the best match.

---

###  Usage Example

```python
# Upload fingerprints for all songs in 'songs/' folder
# Uncomment in audio_fingerprint.py:
# songs_folder = Path("songs")
# audio_files = list(songs_folder.glob("*.wav"))
# for file_path in audio_files:
#     song_id = file_path.stem
#     sound_amplitude_DB_2D, sr = convert_to_spectrogram(file_path)
#     peaks = local_maxima_finder(sound_amplitude_DB_2D)
#     hashes = hashing(peaks)
#     store_in_DB(hashes, song_id, collection)

# Record and recognize a song
filename = record_audio()
hashes_to_compare = create_fingerprint_recorded_audio(filename)
result = match_query(song_ids, hashes_to_compare, collection)
print(result)
```


###  Algorithm Diagram

Audio (.wav) → Spectrogram → Peak Detection → Hashing → Fingerprints → MongoDB
​                                                   

---

###  Concepts Used

-   Short-Time Fourier Transform (STFT)
-   Spectrogram analysis
-   Local maxima detection
-   Hash-based fingerprinting
-   Database search & matching

---

###  References
-   [Shazam Algorithm Explained(https://www.youtube.com/watch?v=a0CVCcb0RJM&t=62s)]

