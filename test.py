import cv2
import mediapipe as mp
import smtplib
import ssl
from email.message import EmailMessage
import pygame
import threading
import os

# Initialize pose estimation
mp_pose = mp.solutions.pose
pose = mp_pose.Pose()
mp_draw = mp.solutions.drawing_utils

# Initialize pygame sound system
pygame.mixer.init()
try:
    if os.path.exists("beep.mp3"):
        alert_sound = pygame.mixer.Sound("beep.mp3")
    else:
        alert_sound = None
        print("⚠️ beep.mp3 not found. Sound will not play.")
except Exception as e:
    alert_sound = None
    print(f"⚠️ Error loading sound: {e}")

# Email sending function
def send_email(image_path):
    sender_email = "libnahmaria@gmail.com"
    receiver_email = "libnahbca325@gmail.com"
    password = "qqsffhpoeqapqoxg"

    subject = "⚠️ Suspicious Person Detected"
    body = "A person was detected on camera. See the attached image."

    msg = EmailMessage()
    msg["From"] = sender_email
    msg["To"] = receiver_email
    msg["Subject"] = subject
    msg.set_content(body)

    with open(image_path, "rb") as f:
        img_data = f.read()
        msg.add_attachment(img_data, maintype="image", subtype="jpeg", filename="intruder.jpg")
    try:
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as smtp:
            smtp.login(sender_email, password)
            smtp.send_message(msg)
            print("📧 Email sent.")
    except Exception as e:
        print(f"❌ Failed to send email: {e}")

# Background wrapper
def send_email_async(image_path):
    threading.Thread(target=send_email, args=(image_path,), daemon=True).start()

# Start video capture
cap = cv2.VideoCapture(0)
sent = False

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = pose.process(image_rgb)

    if results.pose_landmarks:
        mp_draw.draw_landmarks(frame, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)

        if not sent:
            img_path = "intruder.jpg"
            cv2.imwrite(img_path, frame)

            send_email_async(img_path)
            if alert_sound:
                    alert_sound.play()
            sent = True

    cv2.imshow("Pose Estimation", frame)

    if cv2.waitKey(10) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()
