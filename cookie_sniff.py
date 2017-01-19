#!/usr/bin/python3
import getpass
import requests
import ssl

def cookie_sniff():

    username = input("Username: ")
    password = getpass.getpass()

    url_login = "https://logineai.brocade.com/BrocadeEAI/AuthenticateUser"
    url_brocade = "http://www.brocade.com"
    url_my_brocade = "http://my.brocade.com"
    url_brocade_login = "http://login.brocade.com"

    requests.packages.urllib3.util.ssl_.DEFAULT_CIPHERS = 'DES-CBC3-SHA:ECDH+AESGCM:DH+AESGCM:ECDH+AES256:DH+AES256:ECDH+AES128:DH+AES:ECDH+3DES:DH+3DES:RSA+AESGCM:RSA+AES:RSA+3DES:!aNULL:!MD5:!DSS'

    s = requests.Session()

    url_list = [
            url_brocade,
            url_my_brocade,
            url_brocade_login
            ]

    print("Cookies at start of session: \n", s.cookies, "\n" )

    post_data = {'username': username, 'password': password}

    r_login = s.post(url_login, data=post_data)

    print("Cookies after login to ",
            url_login,
            ":\n\n Session Cookies:\n",
            s.cookies, "\n")

    for i in range(len(url_list)):
        r = s.get(url_list[i])
        print("\n", len(s.cookies.items()), "session cookies after {0}:\n".format(url_list[i]))
        print(*(s.cookies.items()), sep="\n")

cookie_sniff()
