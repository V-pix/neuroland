import os
from typing import List

import onesignal
from onesignal.api import default_api
from onesignal.model.notification import Notification

from .models import AlfaCRMUser


def send_onesignal_notification(title, message, users: List[AlfaCRMUser]):
    configuration = onesignal.Configuration(
        api_key=os.getenv("REST_API_KEY", default="api_key"),
    )
    onesignal_client = onesignal.ApiClient()
    onesignal_client.configuration = configuration
    external_user_ids = [user.id for user in users]
    with onesignal.ApiClient(configuration) as api_client:
        api_instance = default_api.DefaultApi(api_client)
        notification = Notification(
            app_id=os.getenv("APP_ID", default="app_id"),
            contents={"en": message},
            headings={"en": title},
            recipients=external_user_ids,
        )
        notification.set_attribute(
            "included_segments", ["Subscribed Users", "Active Users"]
        )
        # notification.set_attribute('included_segments', ["All"])
        api_key_header = "Basic " + os.getenv(
            "REST_API_KEY", default="api_key"
        )
        api_instance.api_client.set_default_header(
            "Authorization", api_key_header
        )
        try:
            onesignal_response = api_instance.create_notification(
                notification
            )
            print("Уведомление отправлено: ", onesignal_response)
            return onesignal_response.id
            # print(onesignal_response.status_code)
            # print(onesignal_response.json())
        except Exception as e:
            print("Ошибка отправки уведомления: ", e)
