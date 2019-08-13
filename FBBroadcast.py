import firebase_admin
from firebase_admin import messaging
from firebase_admin import credentials

cred = credentials.Certificate("C:/Users/kduez/git/avh-plan-firebase-adminsdk-5iy97-2a377ca3d3.json")
firebase_admin.initialize_app(cred)

topic = 'substitutions-broadcast'

# sends a message
message = messaging.Message(
    notification=messaging.Notification(
        title='AvH-Vertretungsplan',
        body='Dies ist eine Testbenachrichtigung.',
    ),
    topic=topic,
)

# sends a data notification, don't use this
# message = messaging.Message(
#     data={},
#     topic=topic,
# )

response = messaging.send(message)
print('Successfully sent message: ', response)