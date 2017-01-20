#!/usr/bin/python3
import getpass
import requests
import ssl
from bs4 import BeautifulSoup
import os
import re


def tsb_grab():

    username = input("Username: ")
    password = getpass.getpass()

    if( (username is None) or (password is None) ):
        print("No user-name or password defined, check help (tsb_grab -h)")
        return False

    url_brocade = "http://www.brocade.com"
    url_login = "https://logineai.brocade.com/BrocadeEAI/AuthenticateUser"
    url_product_catalog = "https://my.brocade.com/wps/myportal/myb/products/productcatalog"
    url_content_query = "https://my.brocade.com/esservice/secure/query"
    url_my_brocade_wps = "https://my.brocade.com/wps/myportal"

    # my.brocade.com secure query JSON template HARDWARE
    query2 = {
        "queryText":"icx7750",
        "langCode":"en",
        "aggsSize":0,
        "size":20,
        "sortOrder":{
            "fieldname":"Title",
            "order":"asc"
            },
        "from":0,
        "filters":[
            {
                "name":"contenttype",
                "values":["Technical Service Bulletin"]
            }],
            "aggregateFields":[{
                "name":"contenttype",
                "includeValues":[
                    "Technical Service Bulletin",
                    ],
                "sortByTerm":"true",
                "asc":"true"
                }],
            "queryFields":["productcode"]
        }

    #################################################################
    # Create a session
    # Terrible hack to overcome nasty SSL HANDSHAKE error
    # Down-grade ciphers for my.brocade.com login
    #requests.packages.urllib3.util.ssl_.DEFAULT_CIPHERS = 'DES-CBC3-SHA'
    requests.packages.urllib3.util.ssl_.DEFAULT_CIPHERS = 'DES-CBC3-SHA:ECDH+AESGCM:DH+AESGCM:ECDH+AES256:DH+AES256:ECDH+AES128:DH+AES:ECDH+3DES:DH+3DES:RSA+AESGCM:RSA+AES:RSA+3DES:!aNULL:!MD5:!DSS'
    # End of hack
    s = requests.Session()

    #################################################################
    #### Authenticate to my.brocade.com and store the session cookies.
    post_data = {'username': username, 'password' : password}
    r_login = s.post(url_login, data=post_data)

    print(r_login.text)

    #################################################################
    #### Get my.brocade.com entitlement cookies
    r_entitle = s.get(url_my_brocade_wps)
    entitle_soup = BeautifulSoup(r_entitle.text, 'html.parser')

    # Extract entitlement string from web-page
    entitlement_string = entitle_soup.find_all('script', string=re.compile('brEntitlement'))
    e_code = re.search('brEntitlement=(.*?)[,;]', entitlement_string.__str__())

    # Add entitlement cookie to cookiejar for session
    s.cookies.set('brEntitlement', e_code.group(1))

    #################################################################
    #### Get the list of products

    # Pull the product list
    r_product_list = s.get(url_product_catalog)

    # Parse the product list
    product_list_soup = BeautifulSoup(r_product_list.text, 'html.parser')

    product_url_list = product_list_soup.select('a.product-listing__product-link')

    products_ref_list = []

    #Transform the a tags into just the product reference
    for i in range(len(product_url_list)):
        #Get the pCode value and add it products_ref_list pCode=<code>&pName=<name>
        products_ref_list.append( (re.search('pCode=(.*?)\&', product_url_list[i]['href'])).group(1) )

    #Remove duplicates
    products_ref_set = set(products_ref_list)
    products_ref_list = sorted(list(products_ref_set))

    #################################################################
    #### Go through every product page
    for n in range(len(products_ref_list)):
        # Get the TSB list from a product page 
        query2["queryText"] = products_ref_list[n]
        r_product = s.post(url_content_query, json=query2)
        product_tsbs = r_product.json()

        print("Getting TSB URL for {0}".format(products_ref_list[n]))

        #Print the TSBs URL list for that product
        for i in range(len(product_tsbs['response']['hits']['hits'])):
            print(product_tsbs['response']['hits']['hits'][i]['fields']['filepath'][0])

        print()

tsb_grab()
