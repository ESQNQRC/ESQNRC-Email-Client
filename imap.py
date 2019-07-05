import email, getpass, imaplib, os, time, threading, configparser, string, smtplib,re,socket,dns.resolver
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

bls = ["zen.spamhaus.org", "dnsbl.inps.de"] # Use only bls because time problems
#bls2= ["zen.spamhaus.org", "dnsbl.inps.de", "dnsbl.sorbs.net", "xbl.spamhaus.org", "pbl.spamhaus.org", "dnsbl-1.uceprotect.net"]



#########################################################
def seeIfBad(urlsList):

    allUrlsGood = True
    for urxl in urlsList:  
    
        rlToGetIp = re.findall('((?:[-\w.]|(?:%[\da-fA-F]{2}))+)',urxl)
        domainIP = socket.gethostbyname(rlToGetIp[1])
        #print(domainIP)

        for bl in bls:
            try:
                my_resolver = dns.resolver.Resolver()
                query = '.'.join(reversed(str(domainIP).split("."))) + "." + bl
                my_resolver.timeout = 5
                my_resolver.lifetime = 5
                answers = my_resolver.query(query, "A")
                answer_txt = my_resolver.query(query, "TXT")
                
                #print ('IP: %s IS listed in %s (%s: %s)' %(domainIP, bl, answers[0], answer_txt[0]))
                return False # Cannot send email at least one url its bad

            except dns.resolver.NXDOMAIN: 
                #print ('IP: %s is NOT listed in %s' %(domainIP, bl))
                allUrlsGood = True
            
            # Need to handle this exceptions
            #except dns.resolver.Timeout:
                #print ('WARNING: Timeout querying ' + bl)
            #except dns.resolver.NoNameservers:
                #print ('WARNING: No nameservers for ' + bl)
            #except dns.resolver.NoAnswer:
                #print ('WARNING: No answer for ' + bl)
    return allUrlsGood

#########################################################







#################################
 # send message function
def sendMessage():

    # semaphore.acquire()
    sendMessageOn = True

    toDestiny = input ("Enter TO (separate with ',' if more than one destinatary): ").split(",")
    subject = input ("Enter a Subject: ")
    body = input ("Enter a body message: ")
    filesToSend = input ("Enter path of files to attach if any (separete with ',' leave in blank if no files to attach): ").split(",")
    for i in range(0, len(filesToSend)):
        filesToSend[i] = filesToSend[i].strip()
    urlsSubject = re.findall('(http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|(?:%[0-9a-fA-F][0-9a-fA-F]))+)', subject)
    urlsBody = re.findall('(http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|(?:%[0-9a-fA-F][0-9a-fA-F]))+)', body)

    #print(urlsSubject)
    #print(urlsBody)
    
    # Check for bad urls
    if urlsSubject != []:
        if not(seeIfBad(urlsSubject)):
            print("Unsecure url detected")
            return
    if urlsBody != []:
        if not(seeIfBad(urlsBody)):
            print("Unsecure url detected")
            return


    
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

    try:

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
    except:
        print("Error when opening the file\nEmail canceled\n")

        print("Write 'send' to send an email\nWrite 'exit' to close program\n ")
        return




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

    print("\nWrite 'send' to send an email\nWrite 'exit' to close program\n ")

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

    if (userConfig["database.user"] == "" or userConfig["database.password"] == ""):
        print("user or password empty")
        exit()

    print("Write 'send' to send an email\nWrite 'exit' to close program\n ")

    # Starts notifications
    thread1 = threading.Thread(target = analizerMail)
    thread1.setDaemon(True)
    thread1.start()



    while True:
        imput = input().lower()
        if (imput == "send"):
            thread2 = threading.Thread(target = sendMessage)
            thread2.start()
            thread2.join()
        elif (imput == "exit"):
            exit(0)




