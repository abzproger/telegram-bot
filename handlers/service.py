import requests


def email_exists(email):
    response = requests.get(f'https://perfect-inc.com/tools/email-checker/api/?email={email}').json()  # Проверка на существование email
    return response