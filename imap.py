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
# Information Extracted from:                                                                                          #
#                                                                                                                      #
# https://yuji.wordpress.com/2011/06/22/python-imaplib-imap-example-with-gmail/                                        #
# https://www.tutorialspoint.com/python/python_imap.how-to-read-email-from-gmail-using-python                          #
# https://stackoverflow.com/questions/348630/how-can-i-download-all-emails-with-attachments-from-gmail?lq=1            #
# https://stackoverflow.com/questions/13210737/get-only-new-emails-imaplib-and-python                                  #
# https://codehandbook.org/how-to-read-email-from-gmail-using-python/                                                  #
# https://gist.github.com/robulouski/7441883                                                                           #
# http://web.archive.org/web/20131017130434/http://www.jejik.com/articles/2007/02/a_simple_unix_linux_daemon_in_python/#
# https://gist.github.com/2624789/d42aaa12bf3a36356342                                                                 #                                  
# https://docs.python.org/2/library/email.mime.html                                                                    #
# https://code.tutsplus.com/es/tutorials/sending-emails-in-python-with-smtp--cms-29975                                 #
#                                                                                                                      #
########################################################################################################################

 # user data
userConfig = {
    "database.user": "",
    "database.password": ""}

run = True #stop the daemon in False

 # send message function
def sendMessage():
	# create message object instance
	msg = MIMEMultipart()

	# get user config
	loadConfig("config.ini")

	# setup the parameters of the message
	password = userConfig["database.password"]
	msg['From'] = userConfig["database.user"]

	if (msg['From'] == "" or password == ""):
		print("user or password empty")
		exit()

	# destination
	destin = input("\nInsert destination (use ',' to separate more destinations): ").split(',')

	chain = ""

	# for more destination
	for i in range(0, len(destin)):
		destin[i] = destin[i].strip()
		chain = chain+destin[i]
		if i+1 < len(destin):
			chain = chain+','

	msg['To'] = chain

	print(msg['To'])

	msg['Subject'] = input("\nInsert subject: ")
 
	message = input("\nInsert message: ")

	# add in the message body
	msg.attach(MIMEText(message, 'plain'))
 
	file_name = input("\nInsert file name (leave blank if you will not attach): ")

	# attach file
	if file_name != "":
		file_address = input("\nInsert file address: ")
		file = open(file_address, 'rb')
		file_MIME = MIMEBase('application', 'octet-stream')
		file_MIME.set_payload((file).read())
		encoders.encode_base64(file_MIME)
		file_MIME.add_header('Content-Disposition', "attachment; filename= %s" % file_name)
		msg.attach(file_MIME)
 
	# create server
	server = smtplib.SMTP('smtp.gmail.com: 587')
 	
 	# encrypt the connection
	server.starttls()
 
	# Login Credentials for sending the mail
	server.login(msg['From'], password)
 
	# send the message via the server.
	server.sendmail(msg['From'], msg['To'], msg.as_string())
 
	server.quit()
 
	print ("\nsuccessfully sent email to %s" % (msg['To']))


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


def analizerMail():

    loadConfig("config.ini")
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

            time.sleep(2)

    finally:        

        imapMail.logout()


#####################################################   MAIN  #############################################


sendMessage()

exit()

try:
    
    threadFunction = threading.Thread(target=analizerMail)

    threadFunction.setDaemon(True)

    threadFunction.start()

    threadFunction.join()

except:
    run = False
    print("\nProgram stopped")
    exit()

