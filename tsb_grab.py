#!/usr/bin/python3
import getpass
import requests
from bs4 import BeautifulSoup
import os


def tsb_grab():

    username = input("Username: ")
    password = getpass.getpass()

    if( (username is None) or (password is None) ):
        print("No user-name or password defined, check help (tsb_grab -h)")
        return False

    url_brocade = "http://www.brocade.com"
    url_login = "https://logineai.brocade.com/BrocadeEAI/AuthenticateUser"
    url_product_catalog = "https://my.brocade.com/wps/myportal/myb/products/productcatalog"
    url_mlxe_example = "https://brocade.com/en/support/document-library/dl-segment-products-os-detail-page.mlxeswitch.product.html?filter=technical-service-bulletin"

    # Create a session
    s = requests.Session()

    #### Authenticate to my.brocade.com and store the session cookies.
    # From Alexander curl example
    # curl "https://logineai.brocade.com/BrocadeEAI/AuthenticateUser" -c cookies.txt --compressed --data "username=yourlogin&password=yourpassword" 1>/dev/null 2>/dev/null
    # http://docs.python-requests.org/en/master/user/advanced/
    post_data = "username={0}&password={1}".format(username, password)
    r_login = s.post(url_login, data=post_data)

    print(r_login.text)

    #### Pull the product list
    r_product_list = s.get(url_product_catalog)

    #### Parse the product list
    product_list_soup = BeautifulSoup(r_product_list.text, 'html.parser')

    product_url_list = product_list_soup.select('a[product-listing__product-link]')

    products_ref_list = []

    #Transform the a tags into just the product_ref
    for i in range(len(product_list)):
        #Get the pCode value and put it in theproducts_ref_list
        #pCode=<code>&pName=<name>
        products_ref_list[i] = (re.search('pCode=(.*?)&amp', product_url_list[i]['href'])).group(1)

    #### Go through every product page
#    for product in products_ref_list:
        # Get the TSB list from a product page 
#        r_product = s.get("https://brocade.com/en/support/document-library/dl-segment-products-os-detail-page.{0}.product.html?filter=technical-service-bulletin".format(product)
#        product_page_soup = BeautifulSoup(r_product.text, 'html.parser')

        # Parse results panel in document library


    #soup = BeautifulSoup(r.text, 'html.parser')

tsb_grab()
