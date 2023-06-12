import os

from dotenv import load_dotenv
from pyfcm import FCMNotification

load_dotenv()

push_service = FCMNotification(api_key=os.getenv("FCM_SERVER_KEY"))


def send_firebase_notification(fcm_token, title, message):
    if fcm_token:
        print(fcm_token)
        data_message = {
            'title': title,
            'message': message
        }
        result = push_service.notify_single_device(
            registration_id=fcm_token,
            data_message=data_message
        )
        print(result)

        if result['success'] == 1:
            print('Уведомление успешно отправлено')
        else:
            print('Ошибка отправки уведомления')
    else:
        print('FCM registration token is None')
