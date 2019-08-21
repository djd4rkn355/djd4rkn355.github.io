import firebase_admin
from firebase_admin import messaging
from firebase_admin import credentials

cred = credentials.Certificate("/home/pi/Desktop/avh-plan-firebase-adminsdk-5iy97-2a377ca3d3.json")
firebase_admin.initialize_app(cred)
topic_android = 'substitutions-debug'
message_android = messaging.Message(
    data={},
    topic=topic_android,
)
response_android = messaging.send(message_android)
print('Successfully sent message to Android clients: ', response_android)
