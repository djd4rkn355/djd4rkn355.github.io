import firebase_admin
from firebase_admin import messaging
from firebase_admin import credentials

cred = credentials.Certificate("/home/pi/Desktop/avh-plan-firebase-adminsdk-5iy97-2a377ca3d3.json")
firebase_admin.initialize_app(cred)

topic = 'substitutions-debug'

# sends a message
message = messaging.Message(
    data={},
    topic=topic,
)

# sends a data notification, don't use this
# message = messaging.Message(
#     data={},
#     topic=topic,
# )

response = messaging.send(message)
print('Successfully sent message: ', response)
