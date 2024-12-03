import cv2
import base64
import tempfile
import streamlit as st
from moviepy.editor import VideoFileClip
import openai

import mediapipe as mp

import pyttsx3
# Text-to-speech engine
engine = pyttsx3.init()

# Initialize MediaPipe Pose
mp_pose = mp.solutions.pose
pose = mp_pose.Pose()

# Function to analyze the posture and provide feedback
def analyze_posture(landmarks):
    feedback = ""
    # Example posture analysis: Checking if left knee is bent at an incorrect angle
    left_knee = landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value]
    left_hip = landmarks[mp_pose.PoseLandmark.LEFT_HIP.value]
    left_ankle = landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value]

    knee_angle = calculate_angle(left_hip, left_knee, left_ankle)

    # Example feedback based on knee angle
    if knee_angle < 160:
        feedback = "Straighten your left knee."
    elif knee_angle > 180:
        feedback = "Bend your left knee slightly."

    return feedback

# Function to calculate angle between three points
def calculate_angle(a, b, c):
    import math
    radians = math.atan2(c.y - b.y, c.x - b.x) - math.atan2(a.y - b.y, a.x - b.x)
    angle = abs(radians * 180.0 / math.pi)
    if angle > 180.0:
        angle = 360.0 - angle
    return angle
# Function to extract frames from the video and encode them in base64
def generate_base64_frame(video):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmpfile:
        tmpfile.write(video.read())
        video_filename = tmpfile.name

    video = cv2.VideoCapture(video_filename)
    base64Frames = []

    while video.isOpened():
        success, frame = video.read()
        if not success:
            break
        _, buffer = cv2.imencode(".jpg", frame)
        base64Frames.append(base64.b64encode(buffer).decode("utf-8"))
    video.release()

    return video_filename, base64Frames

# Function to generate feedback using OpenAI



# Function to give voice feedback
def give_voice_feedback(feedback_text):
    engine.say(feedback_text)
    engine.runAndWait()

def main():
    st.title('Real-time Yoga AI Trainer with Voice Feedback')

    # Upload video file
    uploaded_file = st.file_uploader("Choose a yoga video file", type=["mp4"])

    if uploaded_file is not None:
        # Save the uploaded file to a temporary location
        video_path = "temp_video.mp4"
        with open(video_path, 'wb') as f:
            f.write(uploaded_file.getbuffer())

        # Display the video
        st.video(uploaded_file)

        if st.button('Analyze Yoga Posture'):
            st.write("Analyzing... Please wait.")

            cap = cv2.VideoCapture(video_path)
            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    break

                # Convert the BGR image to RGB and process it with MediaPipe
                image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                results = pose.process(image_rgb)

                if results.pose_landmarks:
                    # Get landmarks and analyze posture
                    landmarks = results.pose_landmarks.landmark
                    feedback_text = analyze_posture(landmarks)

                    if feedback_text:
                        st.write(feedback_text)
                        # Provide feedback through voice
                        give_voice_feedback(feedback_text)

                # Break the loop early for demo purposes
                break

            cap.release()
if __name__ == '__main__':
    main()

