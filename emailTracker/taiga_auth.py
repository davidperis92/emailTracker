import requests


def authenticate(taiga_user, taiga_pass):

    data = {
        'type': 'normal',
        'username': taiga_user,
        'password': taiga_pass
    }

    return requests.post('http://178.62.226.174:81/api/v1/auth', data=data)
