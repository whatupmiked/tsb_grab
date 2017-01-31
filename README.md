Web scrapper for downloading the latest Technical Service Bulletins (TSBs) for Brocade products that your my.brocade.com account has access to.  

TSBs will be downloaded to a directory called 'tsbs\<product-name\>'. If the TSB file already exists it will not be downloaded again. 

## Installation  

#### Download the script  

```  
git clone htttps://www.github.com/whatupmiked/tsb_grab  
```  
#### Added Python 3 modules to your system.  

pip3 install requests  
pip3 install beautifulsoup4  

## Usage Examples  

Prompt for username/password details to mybrocade. Gather all TSBs for all products that your account has access to. Store the files in a directory called /tsbs which will be created in the same directory as the script.  
```  
python3 tsb_grab  
```  
Gather username/password details from a file called 'myPasswordFile' in the scripts directory. Store the collected TSBs in the users home directory. Only collect TSBs for your 'favorite' products. Enabling verbose logging of the scripts actions.   
```  
python3 tsb_grab -v --cred myPasswordFile --path ~/Brocade/TSBs --fav  
```
*NOTE*: When using a credentials file it is recommended that the file permissions are changed so that the file is not read-able by all users.  

## Stackstorm Integration  

Stackstorm is an opensource automation too. Documentation can be found at http://docs.stackstorm.com.  

An example stackstorm rule has been provided in tsb_grab.3min.yaml.

To add the rule to your existing stackstorm installation via command-line:  
```
st2 rule create tsb_grab.3min.yaml  
```
*NOTE*: Change the parameters in the yaml for your script location, credentials location, and path where you want the script stored.   

## python3  

#### CENTOS 7 Python3.4 installation steps  
  1. yum install epel-release  
  2. yum install python34 python-pip  
  3. yum install python34-setuptools  
  4. easy_install-3.4 pip

