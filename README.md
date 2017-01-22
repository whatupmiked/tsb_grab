Web scrapper for downloading the latest Technical Service Bulletins (TSBs) for Brocade products that your my.brocade.com account has access to.  

TSBs will be downloaded to a directory called 'tsb/<product-name>'. If the TSB file already exists it will not be downloaded again. 

python3  
pip3 install requests  
pip3 install beautifulsoup4  
