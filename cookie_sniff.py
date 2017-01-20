#!/usr/bin/python3
import getpass
import requests
import ssl
from bs4 import BeautifulSoup
import re

def cookie_sniff():

    username = input("Username: ")
    password = getpass.getpass()

    url_login = "https://logineai.brocade.com/BrocadeEAI/AuthenticateUser"
    #url_brocade = "http://www.brocade.com"
    #url_my_brocade = "http://my.brocade.com"
    url_my_brocade_wps = "https://my.brocade.com/wps/myportal"
    #url_brocade_login = "http://login.brocade.com"

    requests.packages.urllib3.util.ssl_.DEFAULT_CIPHERS = 'DES-CBC3-SHA:ECDH+AESGCM:DH+AESGCM:ECDH+AES256:DH+AES256:ECDH+AES128:DH+AES:ECDH+3DES:DH+3DES:RSA+AESGCM:RSA+AES:RSA+3DES:!aNULL:!MD5:!DSS'

    s = requests.Session()

#    url_list = [
#            url_brocade,
#            url_my_brocade,
#            url_brocade_login,
#            url_my_brocade_wps
#            ]

    print("Cookies at start of session: \n", s.cookies, "\n" )

    post_data = {'username': username, 'password': password}

    r_login = s.post(url_login, data=post_data)

    print("Cookies after login: ", *(s.cookies.items()), "\n", sep="\n")

    #for i in range(len(url_list)):
    #    r = s.get(url_list[i])
    #    print("\n", len(s.cookies.items()), "session cookies after {0}:\n".format(url_list[i]))
    #    print(*(s.cookies.items()), sep="\n")

    r_entitle = s.get(url_my_brocade_wps)
    entitle_soup = BeautifulSoup(r_entitle.text, 'html.parser')

    entitlement_string = entitle_soup.find_all('script', string=re.compile('brEntitlement'))

    e_code = re.search('brEntitlement=(.*?)[,;]', entitlement_string.__str__())

    s.cookies.set('mybrocInfo', 'brEntitlement='+e_code.group(1))

    print("Cookies after entitlement: ", *(s.cookies.items()), sep="\n")

cookie_sniff()
