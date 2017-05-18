"""
Module for interacting with Technical Service Bulletins
at my.brocade.com
"""
#!/usr/bin/python3
import getpass
import os
import re
import argparse
import requests
from bs4 import BeautifulSoup

def tsb_grab():
    """
    Function executing main script logic
    """
    #######################################################
    #### Parse Command-line options
    parser = argparse.ArgumentParser(description="""Fetches new Brocade Technical Service Bulletins (TSB) and stores them
                                                    in the local directory.""")    #fixme later

    parser.set_defaults(only_favorites=False)
    parser.set_defaults(cred_path=None)
    parser.set_defaults(verbose=False)
    parser.set_defaults(tsb_path_name="tsbs")

    parser.add_argument("--fav", action="store_true", dest="only_favorites",
                        help="Handle only TSBs for Brocade products an authenticated user has choosen as favorite")
    parser.add_argument("--cred", action="store", dest="cred_path",
                        help="Path to file with user-name and password credentials. String format in file 'username password'.")
    parser.add_argument("--path", action="store", dest="tsb_path_name",
                        help="Directory where you want to store the TSBs. Assumes there is no trailing / in path name.")
    parser.add_argument("-v", action="store_true", dest="verbose", help="Add verbose logging output for downloaded TSBs.")

    args = parser.parse_args()

    only_favorites = args.only_favorites
    cred_path = args.cred_path
    verbose = args.verbose
    tsb_path_name = args.tsb_path_name

    #######################################################
    #### Handle credentials
    if cred_path is not None:

        with open(cred_path) as cred_file:
            credentials = cred_file.readline()

        creds = credentials.split()

        if len(creds) is not 2:
            print("ERROR: Incorrectly formatted credentials in credentials file {0}. Format in file should be 'username password'".format(cred_path))
            return False
        else:
            username = creds[0]
            password = creds[1]

    else:
        username = input("Username: ")
        password = getpass.getpass()

        if (username is None) or (password is None):
            print("No user-name or password defined, check help (tsb_grab -h)")
            return False

    #######################################################
    #### Variables for querys
    url_brocade = "http://www.brocade.com"
    url_login = "https://logineai.brocade.com/BrocadeEAI/AuthenticateUser"
    url_product_catalog = "https://my.brocade.com/wps/myportal/myb/products/productcatalog"
    url_content_query = "https://my.brocade.com/esservice/secure/query"
    url_my_brocade_wps = "https://my.brocade.com/wps/myportal"

    # my.brocade.com secure query JSON template 
    query2 = {
        "queryText":"",
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
    #### Create a session
    # Terrible hack to overcome nasty SSL HANDSHAKE error
    # Down-grade ciphers for my.brocade.com login 'DES-CBC3-SHA'
    requests.packages.urllib3.util.ssl_.DEFAULT_CIPHERS = 'DES-CBC3-SHA:ECDH+AESGCM:DH+AESGCM:ECDH+AES256:DH+AES256:ECDH+AES128:DH+AES:ECDH+3DES:DH+3DES:RSA+AESGCM:RSA+AES:RSA+3DES:!aNULL:!MD5:!DSS'
    # End of hack
    s_brocade = requests.Session()

    #################################################################
    #### Authenticate to my.brocade.com and store the session cookies.
    if verbose:
        print('#'*40)
        print("# Logging in to my.brocade.com")
        print('#'*40)

    post_data = {'username': username, 'password' : password}
    r_login = s_brocade.post(url_login, data=post_data)

    if r_login.status_code != 200:  #200=OK
        print("Encountered error {} during authentication\n{}".format(r_login.status_code, r_login.reason))
        return False

    login_soup = BeautifulSoup(r_login.text, 'html.parser')
    if verbose: print((login_soup.find('p')).text)

    #################################################################
    #### Get my.brocade.com entitlement cookies
    if verbose:
        print('#'*40)
        print("# Gathering user entitlement")
        print('#'*40)

    r_entitle = s_brocade.get(url_my_brocade_wps)
    entitle_soup = BeautifulSoup(r_entitle.text, 'html.parser')

    # Extract entitlement string from web-page
    entitlement_string = entitle_soup.find_all('script', string=re.compile('brEntitlement'))
    e_code = re.search('brEntitlement=(.*?)[,;]', entitlement_string.__str__())

    # Add entitlement cookie to cookiejar for session
    s_brocade.cookies.set('mybrocInfo', 'brEntitlement=' + e_code.group(1))
    if verbose: print("Entitlement set!\n")

    #################################################################
    #### Get the list of products

    # Pull the product list
    r_product_list = s_brocade.get(url_product_catalog)

    # Parse the product list
    product_list_soup = BeautifulSoup(r_product_list.text, 'html.parser')

    # Select either product favorites or full product list based on command-line input
    product_list_wanted = None
    if only_favorites == True:
        product_list_wanted = product_list_soup.find('div', class_="product-listing__category product-listing__category-favourites")
    else:
        product_list_wanted = product_list_soup.find('div', class_="product-listing__category-container")

    product_url_list = product_list_wanted.select('a.product-listing__product-link')

    #Transform the <a href> tags into just the product reference
    products_ref_list = []

    for i in range(len(product_url_list)):
        #Get the pCode value and add it products_ref_list pCode=<code>&pName=<name>
        products_ref_list.append((re.search('pCode=(.*?)\&', product_url_list[i]['href'])).group(1))

    #################################################################
    #### Go through every product page
    if verbose:
        print("#"*40)
        if not only_favorites:
            print('# Building TSB list from my.brocade.com')
        else:
            print('# Building TSB list from my.brocade.com FAVORITES only')
        print("#"*40)

    # Dictionary for products (key) and uris list (value)
    product_tsb_uri_list = {}

    for n in range(len(products_ref_list)):
        # Get the TSB list from a product page
        product_name = products_ref_list[n]
        query2["queryText"] = product_name
        r_product = s_brocade.post(url_content_query, json=query2)
        product_tsbs_json = r_product.json()
        product_tsbs = product_tsbs_json['response']['hits']['hits']

        #Skip products w/ no TSBs
        if len(product_tsbs) is not 0:
            product_tsb_uri_list[product_name] = []
            if verbose: print("Gathering TSB URLs for {0}".format(product_name))
            #Print/Store the TSBs URL list for that product
            for i in range(len(product_tsbs)):
                tsb_path = product_tsbs[i]['fields']['filepath'][0]
                #Print TSB
                #print(tsb_path)
                #Store TSB URI
                product_tsb_uri_list[product_name].append(url_brocade + tsb_path)
            #print()
        else:
            if verbose: print("  Skipping product: {0} (No TSBs)".format(product_name))

    #print(*product_tsb_uri_list.items(), sep='\n')

    #################################################################
    #### Compare the URI list to the downloaded TSBs list and download any new TSBs
    if verbose:
        print()
        print("#"*40)
        print('# Checking for TSBs to download')
        print("#"*40)

    tsbs_downloaded = 0

    #Iterate over each product found
    for product in product_tsb_uri_list:
        product_path = tsb_path_name + "/" + product
        tsb_uri_list = product_tsb_uri_list[product]

        #Create product directory
        if not os.path.exists(product_path):
            os.makedirs(product_path)

        #Download TSBs for products found if the TSB does not exist on local system
        for i in range(len(tsb_uri_list)):
            #Split the URI into a list and get the last element
            tsb_name = (tsb_uri_list[i].split('/'))[-1]
            tsb_path = product_path + "/" + tsb_name

            if not os.path.exists(tsb_path):

                if verbose: print("Downloading {0}".format(tsb_name))

                r_pdf = s_brocade.get(tsb_uri_list[i])
                with open(tsb_path, 'wb') as f_path:
                    f_path.write(r_pdf.content)

                print("  Saved {0}".format(tsb_path))
                tsbs_downloaded += 1
            #else:
                #print("TSB already downloaded: {0}".format(tsb_path))
    print()
    print("Total new TSBs found: {0}".format(tsbs_downloaded))

    # End of tsb_grab()
    ################################################################
tsb_grab()
