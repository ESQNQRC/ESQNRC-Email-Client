import email, getpass, imaplib, os, time, threading, configparser, string, smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders


########################################################################################################################
#               Team: Lambder                                                                                          #
#                   Cesar Salazar                                                                                      #
#                   Daniel Berbesi                                                                                     #
#                   Saul Ugueto                                                                                        #
#                   Valentina Contreras                                                                                #
# Script to get unseen emails from a email account                                                                     #
# Send Emails                                                                                                          #
########################################################################################################################

 # user data
userConfig = {
    "database.user": "",
    "database.password": ""}

run = True #stop the daemon in False
sendMessageOn = False
#semaphore = threading.Semaphore(1)




#################################
 # send message function
def sendMessage():

    # semaphore.acquire()
    sendMessageOn = True

    toDestiny = input ("Enter TO (separate with ',' if more than one destinatary): ").split(",")
    subject = input ("Enter a Subject: ")
    body = input ("Enter a body message: ")
    filesToSend = input ("Enter path of files to attach if any (separete with ',' leave in blank if no files to attach): ").split(",")


    # create message object instance
    msgMail = MIMEMultipart()

### Section to set up the data ###

    # setup the parameters of the message
    password = userConfig["database.password"]      # password
    msgMail['From'] = userConfig["database.user"]   # user email
    msgMail['To'] = ', '.join(toDestiny)            # to who is email
    msgMail['Subject'] = subject                    # subject


    # add in the message body
    msgMail.attach(MIMEText(body, 'plain'))
 

### Section to Attach ####

    if filesToSend != ['']:
       
        for file_name in filesToSend:

            with open(file_name,"rb") as file_attach:
                # Add file as application/octet-stream
                file_MIME = MIMEBase("application", "octet-stream")
                file_MIME.set_payload(file_attach.read())

            # Encode file in ASCII characters to send by email    
            encoders.encode_base64(file_MIME)

            # Add header as key/value pair to attachment part
            file_MIME.add_header("Content-Disposition", f"attachment; filename= {file_name}",)

            # Add attachment to message and convert message to string
            msgMail.attach(file_MIME)






#### Section to login and send the email #######
    # create server
    server = smtplib.SMTP('smtp.gmail.com: 587')
    
    # encrypt the connection
    server.starttls()
 
    # Login Credentials for sending the mail
    server.login(msgMail['From'], password)
 
    # send the message via the server.
    server.sendmail(msgMail['From'], msgMail['To'].split(", "), msgMail.as_string())
 
    # Close Conection
    server.quit()

    print ("\nsuccessfully sent email to %s" % (msgMail['To']))

    del msgMail

    sendMessageOn = False
    # semaphore.release()
####################################  sendMessage ####################################################





############################################
 # load userConfig
def loadConfig(file):

    #returns a dictionary with keys of the form
    #<section>.<option> and the corresponding values
    cp = configparser.ConfigParser(  )
    cp.read(file)
    for sec in cp.sections(  ):
        name = str.lower(sec)
        for opt in cp.options(sec):
            userConfig[name + "." + str.lower(opt)] = str.strip(
                cp.get(sec, opt))
    return userConfig
############## loadCondif#######################










################################################
# This function checks for unseen emails
def analizerMail():

    
    # get user from userConfig
    user = userConfig["database.user"]
    # get password from userConfig
    pwd = userConfig["database.password"]

    # If no user or pass provided
    if (user == "" or pwd == ""):
        print("user or password empty")
        exit()


    # connecting to the gmail imap server
    imapMail = imaplib.IMAP4_SSL("imap.gmail.com")


    # Login
    try:
        imapMail.login(user,pwd)
    except:
        print("user or password incorrect")
        exit()

    global run
    
    
    # Makes a list of mails id (to show only new unseen ones)
    listOfShowedEmailsID = []
    listOfEmailsID = []
    allowedToShow = False

    try: 

        #Idle Loop
        while run:

            # Locks if user is sending an email
            # semaphore.acquire()

            if sendMessageOn:
                while sendMessageOn:
                    1

            # makes a list of email
            imapMail.list()

            imapMail.select('Inbox') # here you a can choose a mail box like INBOX instead

            ##print("Checking inbox")

            (resp, data) = imapMail.uid('search',None, '(UNSEEN)') # filter unseen mails

            data = data[0].split() # getting the mails id


            # Now for every unseen email
            for emailid in data:

                #print(emailid)
    
                # Check if email id is in the list of last emails shown
                try:
                # If exception doesn't comes up then item is in the last showed emails list, so we dont show it
                    listOfShowedEmailsID.index(emailid)
                    allowedToShow = False
                    #print("Try, item already showed")
                except: 
                # Except, so id isnt in the list, we need to show it
                    allowedToShow = True
                    #print("Except, item wasnt showed")


                # If it has something to show
                if allowedToShow:
                    (resp, data) = imapMail.uid('fetch',emailid, "(RFC822)") # fetching the mail, "`(RFC822)`" means "get the whole stuff", but you can ask for headers only, etc
        
                    email_info = data[0][1] # getting the mail content
        
                    mail = email.message_from_bytes(email_info) # parsing the mail content to get a mail object
        
                    (resp, data) = imapMail.uid('store',emailid, '-FLAGS', '\\Seen') # Mark email as unseen again (bc fetching brings body of email too)

                    #Check if any attachments at all
                    if mail.get_content_maintype() != 'multipart':
                        continue


                    # Add the current emailID to listOfEmailsID, to save new IDs

                    listOfEmailsID.append(emailid)

                    print ("["+mail["From"]+"] :" + mail["Subject"] + "\n")


            # If this list is not empty, then i got some new emails
            if listOfEmailsID:
                listOfShowedEmailsID.extend(listOfEmailsID)
                listOfEmailsID.clear()


            # Release the lock 
            # semaphore.release()
            time.sleep(5)

    finally:        

        imapMail.logout()
###################################### analizerEmail #################################################




#####################################################   MAIN  #############################################

if __name__ == "__main__":
    
    # get user config
    loadConfig("config.ini")

    print("Write 'send' to send an email ")

    # Starts notifications
    thread1 = threading.Thread(target = analizerMail)
    thread1.start()


    while True:
        if (input().lower() == "send"):
            thread2 = threading.Thread(target = sendMessage)
            thread2.start()
            thread2.join()




