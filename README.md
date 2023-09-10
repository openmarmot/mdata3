# mdata3
mdata3 (marmot data 3) is the third version of a secret manager I've made for my personal use. The major change with this version is it now also generates OTP codes.

Note : The data is encrypted with a simple cypher of my own creation. This is a hobby project, I am not recommending anyone use this to store their sensitive data. 

### Features
- store One Time Password (OTP) secrets and generate OTPs 
- view/edit text data in a encrypted vault
- the encryption algorithm now uses a self rotating salt to increase complexity
- the main menu will exit after 30 seconds to autosave any changes


### Install
- get the code
- pip install pyotp --user
- python mdata3
- enter the passphrase you want to use
- if you want to clear your data and start over just delete the two data files
- if you get a decryption error this means you are entering a 
    different passphrase from what was used to encrypt the file. 
    The password is encrypted as part of the file to prevent you from 
    accidentally re-saving the file with a different password

