import string
import random


def gen_random_password():
    return ''.join(random.choice(string.ascii_lowercase + string.ascii_uppercase + string.digits) for _ in range(10))


def generate_login(login, int_login, same_logins):
    if int_login:
        login_num = 1
        while f"{login}-{login_num}" in same_logins:
            login_num += 1
        return f"{login}-{login_num}"
    else:
        if login not in same_logins:
            return login
        login_num = 1
        while f"{login}{login_num}" in same_logins:
            login_num += 1
        return f"{login}{login_num}"
