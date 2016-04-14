import requests
from django.contrib.auth.backends import RemoteUserBackend


class TaigaAuthBackend(RemoteUserBackend):

    def authenticate(self, taiga_user, taiga_pass):

        data = {
            "type": "normal",
            "username": taiga_user,
            "password": taiga_pass
        }

        response = requests.post('http://178.62.226.174:81/api/v1/auth', data=data)

        if response.status_code == requests.codes.ok:
            return super(TaigaAuthBackend, self).authenticate(taiga_user)

        return None
