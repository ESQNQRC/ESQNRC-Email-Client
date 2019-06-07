import email, getpass, imaplib, os, time, threading, configparser, string, sys


#################################################################################################################
#               Team: Lambder                                                                                   #
#                   Cesar Salazar                                                                               #
#                   Daniel Berbesi                                                                              #
#                   Saul Ugueto                                                                                 #
#                   Valentina Contreras                                                                         #
# Script to get unseen emails from a email account                                                              #
# Information Extracted from:                                                                                   #
#                                                                                                               #
# https://yuji.wordpress.com/2011/06/22/python-imaplib-imap-example-with-gmail/                                 #
# https://www.tutorialspoint.com/python/python_imap.how-to-read-email-from-gmail-using-python                   #
# https://stackoverflow.com/questions/348630/how-can-i-download-all-emails-with-attachments-from-gmail?lq=1     #
# https://stackoverflow.com/questions/13210737/get-only-new-emails-imaplib-and-python                           #
# https://codehandbook.org/how-to-read-email-from-gmail-using-python/                                           #
# https://gist.github.com/robulouski/7441883                                                                    #
#                                                                                                               #
#################################################################################################################
    
 # user data
userConfig = {
    "database.user": "",
    "database.password": ""}


 # load userConfig
def loadConfig(file, config={}):

    #returns a dictionary with keys of the form
    #<section>.<option> and the corresponding values

    config = config.copy(  )
    cp = configparser.ConfigParser(  )
    cp.read(file)
    for sec in cp.sections(  ):
        name = str.lower(sec)
        for opt in cp.options(sec):
            config[name + "." + str.lower(opt)] = str.strip(
                cp.get(sec, opt))
    return config


def analizerMail():

    # get user from userConfig
    user = loadConfig("config.ini", userConfig)["database.user"]
    # get password from userConfig
    pwd = loadConfig("config.ini", userConfig)["database.password"]

    # connecting to the gmail imap server
    imapMail = imaplib.IMAP4_SSL("imap.gmail.com")
    # Login
    imapMail.login(user,pwd)
    # List all the mails

    try: 
        #Idle Loop
        while True:

            imapMail.list()

            imapMail.select('Inbox') # here you a can choose a mail box like INBOX instead

            print("Checking inbox")

            (resp, data) = imapMail.search(None, '(UNSEEN)') # filter unseen mails

            data = data[0].split() # getting the mails id

            for emailid in data:

                print("Processing : ")
    
                (resp, data) = imapMail.fetch(emailid, "(RFC822)") # fetching the mail, "`(RFC822)`" means "get the whole stuff", but you can ask for headers only, etc
    
                email_info = data[0][1] # getting the mail content
    
                mail = email.message_from_bytes(email_info) # parsing the mail content to get a mail object
    
                (resp, data) = imapMail.store(emailid, '-FLAGS', '\\Seen') # Mark email as unseen again (bc fetching brings body of email too)

                #Check if any attachments at all
                if mail.get_content_maintype() != 'multipart':
                    continue

                print ("["+mail["From"]+"] :" + mail["Subject"] + "\n")

            time.sleep(10)

    finally:        

        imapMail.logout()


#####################################################   MAIN  #############################################

try:
    
    threadFunction = threading.Thread(target=analizerMail)

    threadFunction.setDaemon(True)

    threadFunction.start()

    threadFunction.join()

except:

    print("\nProgram stopped")

