import pymysql
import string
import random


class EjudgeDbSession:
    def __init__(self, db_login, db_password, db_name):
        self.connection = pymysql.connect("localhost", db_login, db_password, db_name)

    @staticmethod
    def gen_password():
        return ''.join(random.choice(string.ascii_lowercase + string.ascii_uppercase + string.digits) for _ in range(10))

    def create_login(self, login, int_login):
        cursor = self.connection.cursor()
        cursor.execute(f"SELECT login FROM logins WHERE login LIKE '{login}%'")
        same_logins = {i[0] for i in cursor.fetchall()}
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

    def create_user(self, required_login, int_login=False):
        cursor = self.connection.cursor()
        cursor.execute("SELECT COUNT(*) FROM logins")
        login = self.create_login(required_login, int_login)
        password = self.gen_password()
        while True:
            try:
                cursor.execute("INSERT INTO logins (login, pwdmethod, password) VALUES ('{}', 0, '{}')".format(
                    login,
                    password
                ))
                self.connection.commit()
                if 1 == cursor.execute("SELECT user_id FROM logins WHERE login='{}' AND password='{}'".format(
                    login,
                    password
                )):
                    return {
                        "login": login,
                        "password": password,
                        "user_id": cursor.fetchall()[0][0]
                    }
            except:
                login = self.create_login(required_login, int_login)

    def register_for_contest(self, user_id, contest_id, name=""):
        cursor = self.connection.cursor()
        cursor.execute("INSERT INTO cntsregs (user_id, contest_id) VALUES ({}, {})".format(
            user_id,
            contest_id
        ))
        self.connection.commit()
        cursor.execute("INSERT INTO users (user_id, contest_id, username) VALUES ({}, {}, '{}')".format(
            user_id,
            contest_id,
            name
        ))
        self.connection.commit()

    def create_user_and_add_contests(self, required_login, name, int_login, contests):
        register_result = self.create_user(required_login, int_login)
        for contest in contests:
            self.register_for_contest(register_result["user_id"], contest, name)
        return register_result
