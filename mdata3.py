'''
module : mdata3.py
Language : Python 3.x
email : andrew@openmarmot.com
notes : OTP and secret vault. 

otp file syntax:
description1:otp_secret_1
description2:otp_secret_2

vault file syntax: no limitations

'''

#import built in modules
from queue import Queue
from threading import Thread
import os
import sys
import subprocess
import random
import string
import copy

#import custom packages
# https://pypi.org/project/pyotp/
import pyotp 

#global vars
character_key=['a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q']
character_key+=['r','s','t','u','v','w','x','y','z','A','B','C','D','E','F','G','H']
character_key+=['I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y']
character_key+=['Z','0','1','2','3','4','5','6','7','8','9','!','@','#','$','%','^']
character_key+=['&','*','-','_','/','=','.',' ',':','+','?','(',')','~','<','>']

otp_file_name='mdata_otp_data'
secret_vault_file_name='mdata_vault_data'

# path to your favorite editor. 
# this will be correct for most linux and most apple os
path_to_editor='/usr/bin/vim'

#------------------------------------------------------------------------------
def check_if_file_exists(file_name):
    '''checks if file exists; returns a bool'''
    if os.path.exists(file_name):
        return True
    else:
        return False

#------------------------------------------------------------------------------
def decrypt_data_array(encrypted_array,passphrase):
    ''' decrypt a encrypted array. the first element of the array is the salt'''
    global character_key

    salt=encrypted_array.pop(0)
    encryption_key=generate_encryption_key(passphrase+salt)

    data=[]
    for eline in encrypted_array:
        dline=''
        for char in eline:
            try:
                dline+=character_key[encryption_key.index(char)]
            except ValueError:
                dline+=char #char is not in key ? pass it through
        data.append(dline)

    if data[0]!=passphrase:
        print('Decryption error!')
        sys.exit(1)
    else:
        data.pop(0)
    return data

#------------------------------------------------------------------------------
def decrypt_file(file_name,passphrase):
    '''decrypt file, returning the data array'''
    encrypted_array=get_array_from_file(file_name)
    return decrypt_data_array(encrypted_array,passphrase)

#------------------------------------------------------------------------------
def encrypt_array_and_write_file(data,file_name,passphrase):
    encrypted_data=encrypt_data_array(data,passphrase)
    write_array_to_file(file_name,encrypted_data)

#------------------------------------------------------------------------------
def encrypt_data_array(data,passphrase):
    '''encrypts a data array and returns the result'''
    # note the encryption format has the salt as the first element of the array
    # the passphrase is encrypted as the second element to allow the decryption to be checked
    data=[passphrase]+data

    global character_key
    '''encrypts a data array and returns the result'''
    # create new salt instead of reusing to create a new encryption key
    salt=generate_salt()
    encryption_key=generate_encryption_key(passphrase+salt)
    encrypted_data=[]
    for dline in data:
        eline=''
        for char in dline:
            try:
                eline+=encryption_key[character_key.index(char)]
            except ValueError:
                eline+=char #char is not in key ? pass it through
                print('WARN : character '+char+' is not in the key')
        encrypted_data.append(eline)
    # add salt as first element
    encrypted_data=[salt]+encrypted_data
    return encrypted_data

#------------------------------------------------------------------------------
def edit_data_array(data):
    ''' returns a edited data array'''
    global path

    # dump data to a file
    write_array_to_file('temp',data)

    # edit the file via os tools
    subprocess.call([path_to_editor, 'temp'])

    # retrieve the results 
    new_data=get_array_from_file('temp')

    # cleanup
    try:
        os.remove('temp')
    except FileNotFoundError:
        print('File delete error : file not found')

    return new_data

#------------------------------------------------------------------------------
def get_array_from_file(file_name):
    '''reads a file and returns a array of the contents'''
    data=[]
    try:
        for line in open(file_name):
            line=line.rstrip() 
            data.append(line)
    except FileNotFoundError:
        print('File ' + file_name + ' not found')
        return None
    return data

#------------------------------------------------------------------------------
def generate_encryption_key(passphrase):
    '''generate the encryption key array'''
    global character_key
    encryption_key=copy.copy(character_key)
    encryption_key.reverse()
    for x in passphrase:
        char1=encryption_key.pop(character_key.index(x))
        char2=encryption_key.pop(0) 
        encryption_key.append(char2)
        encryption_key.append(char1)
    
    return encryption_key

#------------------------------------------------------------------------------
def generate_salt(length=20):
    '''generates salt'''
    length+=random.randint(0,length)
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))

#------------------------------------------------------------------------------
def initialize_files(file_name_array,passphrase):
    '''checks that the data files exist, if not create them'''

    for b in file_name_array:
        if check_if_file_exists(b)==False:
            print(b+' does not exist. creating..')
            encrypt_array_and_write_file(['empty'],b,passphrase)


#------------------------------------------------------------------------------
def input_thread(q):
    try:
        # Get the input within 30 seconds
        selection = input('Enter selection: ')
        q.put(selection)
    except:
        # If no input received within 30 seconds, put "timeout" in the queue
        q.put("timeout")

#------------------------------------------------------------------------------
def print_data_array(data):
    '''prints a array of strings to the console'''
    for b in data:
        print(b)

#------------------------------------------------------------------------------
def print_otp_codes(data):
    '''generates and prints otp codes'''
    for b in data:
        key_pair=b.split(':')
        if len(key_pair)==2:
            try:
                otp = pyotp.TOTP(key_pair[1])
                print(key_pair[0],str(otp.now()))
            except Exception as e:
                print(f"An error occurred: {e}")
                print('OTP error with '+key_pair[0]+' code')
        else:
            print('WARN : malformed otp data.')
            print('-Correct format-')
            print('name1:secret1')
            print('name2:secret2')
            print('-------------')

#------------------------------------------------------------------------------
def print_search_results(data,keyword):
    '''searches an array of strings for a keyword and then prints the neighboring strings'''

    for i in range(len(data)):
        if keyword in data[i]:
            print('------------------------------------')
            for b in data[i:i+7]:
                print(b)
            print('------------------------------------')

#------------------------------------------------------------------------------
def write_array_to_file(file_name,data):
    file_obj=open(file_name,'w') 
    for line in data:
        file_obj.write(line+'\n')
    file_obj.close

#------------------------------------------------------------------------------
def main():
    global otp_file_name
    global secret_vault_file_name
    
    # get the passphrase
    print('===================================')
    print('    Marmot Data 3')
    passphrase=input('Enter PassPhrase: ')
    os.system('clear')

    # initial decrypt
    initialize_files([otp_file_name,secret_vault_file_name],passphrase)
    otp_data=decrypt_file(otp_file_name,passphrase)
    vault_data=decrypt_file(secret_vault_file_name,passphrase)

    # main program loop
    while True:
        os.system('clear')
        print('===================================')
        print('    Marmot Data 3')
        print('    e - Exit')
        print('    1 - Generate OTP Codes')
        print('    2 - View Secret Vault')
        print('    3 - Search Secret Vault')
        print('    4 - Edit OTP name:secret pairs')
        print('    5 - Edit Secret Vault data')
        
        q = Queue()
        t = Thread(target=input_thread, args=(q,))
        t.start()
        t.join(30)  # Timeout of 30 seconds
        if not q.empty():
            selection = q.get()
        else:
            selection = "e"

        if selection=='e':
            os.system('clear')
            print('Encrypting and saving OTP data..')
            encrypt_array_and_write_file(otp_data,otp_file_name,passphrase)
            print('Encrypting and saving Vault data..')
            encrypt_array_and_write_file(vault_data,secret_vault_file_name,passphrase)
            print('Cleanup..')
            passphrase=None
            otp_data=None
            vault_data=None
            print('Please close this console for security. Goodbye!')
            sys.exit()
        elif selection=='1':
            print_otp_codes(otp_data)
            input('Hit Enter to continue ')
        elif selection=='2':
            print_data_array(vault_data)
            input('Hit Enter to continue ')
        elif selection=='3':
            print_search_results(vault_data,input('Enter Search Keyword: '))
            input('Hit Enter to continue ')
        elif selection=='4':
            otp_data=edit_data_array(otp_data)
        elif selection=='5':
            vault_data=edit_data_array(vault_data)

main()