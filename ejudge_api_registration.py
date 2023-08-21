import requests
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


MAX_ROWS = 20000

SHOW_USERS_API = '?SID={SID}&action=305&_search=true&rows={max_rows}&searchField=login&searchString={search_string}&searchOper={search_oper}'


class EjudgeApiSession:
    def __init__(self, ejudge_login, ejudge_password, ejudge_url):
        self.session = requests.session()
        self.serve_control_url = ejudge_url + '/cgi-bin/serve-control'
        start_page = self.session.post(
            self.serve_control_url,
            data={
                'login': ejudge_login,
                'password': ejudge_password,
            },
            headers=dict(referer=self.serve_control_url),
        )
        self.sid = start_page.url[start_page.url.find('SID=') + 4:]

    def create_login(self, login, int_login):
        result = self.session.get(
            self.serve_control_url + SHOW_USERS_API.format(
                SID=self.sid,
                max_rows=MAX_ROWS,
                search_string=login,
                search_oper='bw',
            )
        )
        logins_json = result.json()
        same_logins = {i['cell'][2] for i in logins_json['rows']}
        return generate_login(login, int_login, same_logins)

    def create_user(self, required_login, int_login=False):
        login = self.create_login(required_login, int_login)
        password = gen_random_password()
        for i in range(100):
            res = self.session.post(
                self.serve_control_url,
                data={
                    'SID': self.sid,
                    'other_login': login,
                    'reg_password1': password,
                    'reg_password2': password,
                    'action': 73,
                },
                allow_redirects=True
            )
            if res.text.find('duplicated login name') != -1:
                login = self.create_login(required_login, int_login)
                continue

            login_find = self.session.get(
                self.serve_control_url + SHOW_USERS_API.format(
                    SID=self.sid,
                    max_rows=10,
                    search_string=login,
                    search_oper='eq'
                )
            ).json()

            if len(login_find["rows"]) > 0 and login_find["rows"][0]["cell"][2] != login:
                login = self.create_login(required_login, int_login)
                continue

            user_id = login_find["rows"][0]["id"]

            return {
                'login': login,
                'password': password,
                'user_id': user_id,
            }

        return {
            'login': "register error",
            'password': "register error",
        }

    def register_for_contest(self, user_id, login, contest_id, name=""):
        self.session.post(
            self.serve_control_url,
            data={
                'SID': self.sid,
                'other_user_id': user_id,
                'other_contest_id_1': contest_id,
                'other_contest_id_2': contest_id,
                'status': 0,
                'action': 94,
            },
            allow_redirects=True
        )
        x = self.session.post(
            self.serve_control_url,
            data={
                'SID': self.sid,
                'other_user_id': user_id,
                'contest_id': contest_id,
                'other_login': login,
                'field_101': name,
                'action': 88,
                'email': "",
            },
            allow_redirects=True
        )

    def create_user_and_add_contests(self, required_login, name, int_login, contests):
        register_result = self.create_user(required_login, int_login)
        for contest in contests:
            self.register_for_contest(register_result["user_id"], register_result["login"], contest, name)
        return register_result
