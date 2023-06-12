from functions import *
import pickle
import face_recognition
import cv2
import numpy as np


class FaceRec:
    def __init__(self):
        self.known_face_encodings = []
        self.known_face_names = []
        self.frame_resizing = 0.25

    def load_encoding_images(self, images_path, save_file=None):
        if save_file and os.path.exists(save_file):
            # Load pre-encoded face encodings from file
            with open(save_file, 'rb') as f:
                data = pickle.load(f)
            self.known_face_encodings = data['encodings']
            self.known_face_names = data['names']
        else:
            # Encode faces and save the encodings
            images_path = os.path.abspath(images_path)
            for filename in os.listdir(images_path):
                if filename.endswith('.jpg') or filename.endswith('.png'):
                    image_path = os.path.join(images_path, filename)
                    img = cv2.imread(image_path)
                    rgb_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                    encoding = face_recognition.face_encodings(rgb_img)[0]
                    self.known_face_encodings.append(encoding)
                    self.known_face_names.append(os.path.splitext(filename)[0])

            if save_file:
                # Save the face encodings to file
                data = {'encodings': self.known_face_encodings, 'names': self.known_face_names}
                with open(save_file, 'wb') as f:
                    pickle.dump(data, f)

    def detect_known_faces(self, frame):
        small_frame = cv2.resize(frame, (0, 0), fx=self.frame_resizing, fy=self.frame_resizing)
        rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)
        face_locations = face_recognition.face_locations(rgb_small_frame)
        face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

        face_names = []
        for face_encoding in face_encodings:
            matches = face_recognition.compare_faces(self.known_face_encodings, face_encoding)
            name = "Unknown"

            face_distances = face_recognition.face_distance(self.known_face_encodings, face_encoding)
            best_match_index = np.argmin(face_distances)
            if matches[best_match_index]:
                name = self.known_face_names[best_match_index]
            face_names.append(name)

        face_locations = np.array(face_locations)
        face_locations = face_locations / self.frame_resizing
        return face_locations.astype(int), face_names
    
def scan_face():
    # Encode faces from a folder and save the encodings
    save_file = 'assets/vision/face_encodings.pkl'
    sfr = FaceRec()
    sfr.load_encoding_images("assets/vision/faces/", save_file=save_file)

    # Load Camera
    cap = cv2.VideoCapture(0)
    while True:
        ret, frame = cap.read()
        recognized_names = []  # Initialize the list inside the loop

        # Detect Faces
        face_locations, face_names = sfr.detect_known_faces(frame)
        if len(face_locations) == 0:  # No face detected
            error_message = "N"
            return error_message
        for face_loc, name in zip(face_locations, face_names):
            y1, x2, y2, x1 = face_loc[0], face_loc[1], face_loc[2], face_loc[3]

            recognized_names.append(name)  # Add recognized name to the list

            cv2.putText(frame, name, (x1, y1 - 10), cv2.FONT_HERSHEY_DUPLEX, 1, (0, 0, 200), 2)
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 200), 4)


        if len(recognized_names) > 0:
            break

    cap.release()
    cv2.destroyAllWindows()
    return(recognized_names)

def add_face(text):
    local_recogniser = get_recogniser()
    name = False
    play_sound("sound/sure.mp3", 0.5, blocking=True)
    while name == False:
        done = False
        while not done:
            play_sound("sound/name.mp3", 0.5, blocking=True)
            try:
                person = recognise_input(local_recogniser)
                done=True
            except speech_recognition.UnknownValueError:
                local_recogniser = speech_recognition.Recognizer()
                play_sound("sound/repeat.mp3", 0.5, blocking=False)
        
        print("Name: ", person)
        finish = False
        while not finish:
            speak(f"Is your name {person}?")
            try:
                response = recognise_input(local_recogniser)
                print("[INPUT] ",response)
                finish = True
            except speech_recognition.UnknownValueError:
                local_recogniser = speech_recognition.Recognizer()
                play_sound("sound/repeat.mp3", 0.5, blocking=True)

        if ('no' in response) or ('nope' in response):
            play_sound("sound/tryAgain.mp3", 0.5, blocking=True)
            name = False
        else:
            if ('yes' in response) or ('yeah' in response) or ('yep' in response):               
                name = True
            name = True #consider changing 
    cap = cv2.VideoCapture(0)
    play_sound("sound/picture.mp3", 0.5, blocking=True)
    _, image = cap.read()
    time.sleep(1)
    image_path = f"assets/vision/faces/{person}.jpg"
    cv2.imwrite(image_path, image)
    play_sound("sound/done.mp3", 0.5, blocking=True)

    print(f"Face captured and saved as {image_path}")
    cap.release()
    cv2.destroyAllWindows()
    save_file = 'assets/vision/face_encodings.pkl'
    sfr = FaceRec()
    sfr.load_encoding_images("faces/", save_file=save_file)

def greet_me(text):
    # Encode faces from a folder and save the encodings
    save_file = 'assets/vision/face_encodings.pkl'
    sfr = FaceRec()
    sfr.load_encoding_images("assets/vision/faces/", save_file=save_file)
    # Load Camera
    cap = cv2.VideoCapture(0)
    while True:
        ret, frame = cap.read()
        recognized_names = []  # Initialize the list inside the loop
        # Detect Faces
        face_locations, face_names = sfr.detect_known_faces(frame)
        if len(face_locations) == 0:  # No face detected
            error_message = "N"
            return error_message
        for face_loc, name in zip(face_locations, face_names):
            y1, x2, y2, x1 = face_loc[0], face_loc[1], face_loc[2], face_loc[3]
            recognized_names.append(name)  # Add recognized name to the list
            cv2.putText(frame, name, (x1, y1 - 10), cv2.FONT_HERSHEY_DUPLEX, 1, (0, 0, 200), 2)
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 200), 4)
        if len(recognized_names) > 0:
            break
    cap.release()
    cv2.destroyAllWindows()
    for name in recognized_names:
        if name == "N" or name == "Unknown":
            play_sound("sound/greet.mp3", 0.5, blocking=False)
        else:
            speak(f"Hey {name}. I'm K9.")