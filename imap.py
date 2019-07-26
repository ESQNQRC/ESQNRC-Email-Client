from twx.botapi import TelegramBot, ReplyKeyboardMarkup
from telegram import Bot
import email, getpass, imaplib, os, time, threading, configparser, string, smtplib, sys, re,socket, dns.resolver, datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import sys,traceback

########################################################################################################################
#               Team: Lambder                                                                                          #
#                   Cesar Salazar                                                                                      #
#                   Daniel Berbesi                                                                                     #
#                   Saul Ugueto                                                                                        #
#                   Valentina Contreras                                                                                #
# Script to get unseen emails from a email account                                                                     #
# Send Emails                                                                                                          #
########################################################################################################################

run = True #stop the daemon in False

bls = ["zen.spamhaus.org", "dnsbl.inps.de"] # Use only bls because time problems

token = '885992983:AAEGo6sBA0hBfYYMFAzU7K-0SJYP-PbYf0Y'

botto = Bot(token)

def seeIfBad(urlsList):

    allUrlsGood = True
    for urxl in urlsList:  
    
        rlToGetIp = re.findall('((?:[-\w.]|(?:%[\da-fA-F]{2}))+)',urxl)
        domainIP = socket.gethostbyname(rlToGetIp[1])

        for bl in bls:
            try:
                my_resolver = dns.resolver.Resolver()
                query = '.'.join(reversed(str(domainIP).split("."))) + "." + bl
                my_resolver.timeout = 5
                my_resolver.lifetime = 5
                answers = my_resolver.query(query, "A")
                answer_txt = my_resolver.query(query, "TXT")
                
                return False # Cannot send email at least one url its bad

            except dns.resolver.NXDOMAIN: 
                
                allUrlsGood = True
            
    return allUrlsGood



def sendMessage(toDestino, subject, body, filesToSend, usr, pwd, chat_id):
    
    toDestiny = toDestino.split(",")

    urlsSubject = re.findall('(http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|(?:%[0-9a-fA-F][0-9a-fA-F]))+)', subject)
    urlsBody = re.findall('(http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|(?:%[0-9a-fA-F][0-9a-fA-F]))+)', body)

    # Check for bad urls
    if urlsSubject != []:
        if not(seeIfBad(urlsSubject)):
            bot.send_message(chat_id, 'Unsecure url detected')
            return 1
    if urlsBody != []:
        if not(seeIfBad(urlsBody)):
            bot.send_message(chat_id, 'Unsecure url detected')
            return 1

    # create message object instance
    msgMail = MIMEMultipart()

### Section to set up the data ###

    # setup the parameters of the message
    password = pwd      # password
    msgMail['From'] = usr   # user email
    msgMail['To'] = ', '.join(toDestiny)            # to who is email
    msgMail['Subject'] = subject                    # subject

    # add in the message body
    msgMail.attach(MIMEText(body, 'plain')) 

### Section to Attach ####

    try:

        if filesToSend != []:
       
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
        bot.send_message(chat_id, 'Error trying to send that file')
        return 1


#### Section to login and send the email #######
    # create server
    server = smtplib.SMTP('smtp.gmail.com: 587')
    
    # encrypt the connection
    server.starttls()
 
    # Login Credentials for sending the mail
    server.login(msgMail['From'], password)
 
    try:
        # send the message via the server.
        server.sendmail(msgMail['From'], msgMail['To'].split(", "), msgMail.as_string())
    except:
        bot.send_message(chat_id, 'recipient is incorrect')
        return 1
 
    # Close Conection
    server.quit()

    del msgMail

    return 0
####################################  sendMessage ####################################################




def analizerMail(user, pwd, chat_id, bot, last_update_id):  # This function checks for unseen emails

    # connecting to the gmail imap server
    imapMail = imaplib.IMAP4_SSL("imap.gmail.com")

    # Login
    try:
        imapMail.login(user,pwd)
    except:

        print("User or password incorrect <Sticker>")
        keyboard = [['Loggin account'],['Exit']]
        reply_markup = ReplyKeyboardMarkup.create(keyboard)
                        
        bot.send_message(chat_id, 'User or password incorrect', reply_markup=reply_markup).wait()
        bot.send_sticker(chat_id, 'CAADAgAD8wgAAgi3GQKHdYrrN-Wt_QI', reply_markup=reply_markup).wait()
                        
        layer2(bot, last_update_id)

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

            (resp, data) = imapMail.uid('search',None, '(UNSEEN)') # filter unseen mails

            data = data[0].split() # getting the mails id

            # Now for every unseen email
            for emailid in data:
    
                # Check if email id is in the list of last emails shown
                try:
                # If exception doesn't comes up then item is in the last showed emails list, so we dont show it
                    listOfShowedEmailsID.index(emailid)
                    allowedToShow = False

                except: 
                # Except, so id isnt in the list, we need to show it
                    allowedToShow = True

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
                    try:
                        resp = "["+mail["From"]+"] :" + mail["Subject"] + "\n"

                        bot.send_message(chat_id, resp)
                    except:
                        exit()

            # If this list is not empty, then i got some new emails
            if listOfEmailsID:
                listOfShowedEmailsID.extend(listOfEmailsID)
                listOfEmailsID.clear()

    finally:        

        imapMail.logout()





################################ MAIN #########################################################
def main():
    bot = TelegramBot(token) #Connect with the bot
    bot.update_bot_info().wait()
    print("botUsername: ", bot.username)

    last_update_id = 0













    def process_message_layer9(bot, u,last_update_id, usr, pwd, dest, sub, content,filesToSend):

        # if the message is a file
        if u.message.sender and u.message.chat:
            chat_id = u.message.chat.id # Extract data of message
            user = u.message.sender.id
            
            print("\n chat_id: ", chat_id)
            print("user: \n", user)

            if u.message.document:
                print(" \n BOT.MESSAGE.DOCUMENT, Layer 9")
                print(u.message.document)
                print("\n")

                # Get file info
                file_Info = botto.get_file(u.message.document.file_id) 

                # Download locally to manipulate later
                file_Info.download(u.message.document.file_name)

                filesToSend.append(u.message.document.file_name)


                print("\n Layer 9: Esperando por archivo o Send")
                keyboard = [['Send'],['Back']]
                reply_markup = ReplyKeyboardMarkup.create(keyboard)
                bot.send_message(chat_id,"Do you have another file? or do you want to send email?", reply_markup=reply_markup).wait()
                layer9(bot, last_update_id, usr, pwd, dest, sub, content,filesToSend)

            elif u.message.photo:
                print(" \n BOT.MESSAGE.PHOTO, Layer 9")
                print(u.message.photo)
                print("\n")

                # Get file info
                file_Info = botto.get_file(u.message.photo[3].file_id) 

                # Download locally to manipulate later
                tofu = u.message.photo[3].file_id
                
                file_Info.download(tofu)

                filesToSend.append(tofu)

                print("\n Layer 9: Esperando por archivo o Send")
                keyboard = [['Send'],['Back']]
                reply_markup = ReplyKeyboardMarkup.create(keyboard)
                bot.send_message(chat_id,"Do you have another file? or do you want to send email?", reply_markup=reply_markup).wait()
                layer9(bot, last_update_id, usr, pwd, dest, sub, content,filesToSend)

            elif u.message.text:
                if u.message.text == 'Send':

                    print("Sending mail, Layer 9")
                    bot.send_message(chat_id, 'Sending email')

                    if sendMessage(dest, sub, content, filesToSend, usr, pwd, chat_id) == 0:
                        bot.send_message(chat_id, 'Email send')

                    print("Select an option, Layer 9")
                    keyboard = [['Show unseen emails'],['Send a email'], ['Back']]
                    reply_markup = ReplyKeyboardMarkup.create(keyboard)
                    bot.send_message(chat_id, 'Select an option', reply_markup=reply_markup).wait()
                    layer4(bot, last_update_id, usr, pwd)

                elif u.message.text == 'Back':
                    print("Select an option, Layer 9")
                    keyboard = [['Show unseen emails'],['Send a email'], ['Back']]
                    reply_markup = ReplyKeyboardMarkup.create(keyboard)
                    bot.send_message(chat_id, 'Select an option', reply_markup=reply_markup).wait()
                    layer4(bot, last_update_id, usr, pwd)
                else:
                    print("Select an option, Layer 9")
                    keyboard = [['Send'],['Back']]
                    reply_markup = ReplyKeyboardMarkup.create(keyboard)
                    bot.send_message(chat_id, 'Select an option', reply_markup=reply_markup).wait()
        else:
            print("Select an option, Layer 9")
            keyboard = [['Show unseen emails'],['Send a email'], ['Back']]
            reply_markup = ReplyKeyboardMarkup.create(keyboard)
            bot.send_message(u.message.chat.id, 'Select an option', reply_markup=reply_markup).wait()
            layer4(bot, last_update_id, usr, pwd)




    def layer9(bot, last_update_id, usr, pwd, dest, sub, content,filesToSend): # Send mail with or without files
        print("\n Layer 9\n")
        while True: 
            updates = bot.get_updates(offset = last_update_id).wait()
            try: 
                for update in updates: 
                    if int(update.update_id) > int(last_update_id):
                        last_update_id = update.update_id 
                        print("last_update_id: ",last_update_id)
                        process_message_layer9(bot, update,last_update_id, usr, pwd, dest, sub, content,filesToSend)
                        continue 
                continue 
            except Exception: 
                ex = None 
                print(traceback.format_exc())
                continue










    def process_message_layer8(bot, u, last_update_id, usr, pwd, dest, sub, content):

        if u.message.sender and u.message.text and u.message.chat: # if the message is text
            chat_id = u.message.chat.id # Extract data of message
            user = u.message.sender.id
            message = u.message.text

            print("\n chat_id: ", chat_id)
            print("user: ", user)
            print("message: ", message)
            print("\n")

            if message == 'Back':
                print("Select an option, Layer 8")
                keyboard = [['Show unseen emails'],['Send a email'], ['Back']]
                reply_markup = ReplyKeyboardMarkup.create(keyboard)
                bot.send_message(chat_id, 'Select an option', reply_markup=reply_markup).wait()
                layer4(bot, last_update_id, usr, pwd)

            elif message == 'Attach files':
                print("Enviame los archivos, Layer 8")
                keyboard = [['Send'],['Back']]
                reply_markup = ReplyKeyboardMarkup.create(keyboard)
                bot.send_message(chat_id, 'Send me your files', reply_markup=reply_markup).wait()
                layer9(bot, last_update_id, usr, pwd, dest, sub, content,[])


            elif message == 'Do not attach files':
                print("Sending mail, Layer 8")
                bot.send_message(chat_id, 'Sending email')

                if sendMessage(dest, sub, content, [], usr, pwd, chat_id) == 0:
                    bot.send_message(chat_id, 'Email send')

                print("Select an option, Layer 8")
                keyboard = [['Show unseen emails'],['Send a email'], ['Back']]
                reply_markup = ReplyKeyboardMarkup.create(keyboard)
                bot.send_message(chat_id, 'Select an option', reply_markup=reply_markup).wait()
                layer4(bot, last_update_id, usr, pwd)

            else:
                print("Select an option, Layer 8")
                keyboard = [['Attach files'], ['Do not attach files'], ['Back']]
                reply_markup = ReplyKeyboardMarkup.create(keyboard)
                bot.send_message(chat_id, 'Select an option', reply_markup=reply_markup).wait()
                layer8(bot, last_update_id, usr, pwd, dest, sub, content)


        else:
            print("Select an option, Layer 8")
            keyboard = [['Show unseen emails'],['Send a email'], ['Back']]
            reply_markup = ReplyKeyboardMarkup.create(keyboard)
            bot.send_message(u.message.chat.id, 'Select an option', reply_markup=reply_markup).wait()
            layer4(bot, last_update_id, usr, pwd)

    def layer8(bot, last_update_id, usr, pwd, dest, sub, content): # Send mail with or without files
        print("\n Layer 8\n")
        while True: 
            updates = bot.get_updates(offset = last_update_id).wait()
            try: 
                for update in updates: 
                    if int(update.update_id) > int(last_update_id):
                        last_update_id = update.update_id 
                        print("last_update_id: ",last_update_id)
                        process_message_layer8(bot, update, last_update_id, usr, pwd, dest, sub, content)
                        continue 
                continue 
            except Exception: 
                ex = None 
                print(traceback.format_exc())
                continue





    def process_message_layer7(bot, u, last_update_id, usr, pwd, dest, sub):

        if u.message.sender and u.message.text and u.message.chat: # if the message is text
            chat_id = u.message.chat.id # Extract data of message
            user = u.message.sender.id
            message = u.message.text

            print("\n chat_id: ", chat_id)
            print("user: ", user)
            print("message: ", message)
            print("\n")

            if message == 'Back':
                print("Select an option, Layer 7")
                keyboard = [['Show unseen emails'],['Send a email'], ['Back']]
                reply_markup = ReplyKeyboardMarkup.create(keyboard)
                bot.send_message(chat_id, 'Select an option', reply_markup=reply_markup).wait()
                layer4(bot, last_update_id, usr, pwd)

            else:
                print("Select an option, Layer 7")
                keyboard = [['Attach files'], ['Do not attach files'], ['Back']]
                reply_markup = ReplyKeyboardMarkup.create(keyboard)
                bot.send_message(chat_id, 'Select an option', reply_markup=reply_markup).wait()
                layer8(bot, last_update_id, usr, pwd, dest, sub, message)

        else:
            print("Select an option, Layer 7")
            keyboard = [['Show unseen emails'],['Send a email'], ['Back']]
            reply_markup = ReplyKeyboardMarkup.create(keyboard)
            bot.send_message(u.message.chat.id, 'Select an option', reply_markup=reply_markup).wait()
            layer4(bot, last_update_id, usr, pwd)

    def layer7(bot, last_update_id, usr, pwd, dest, sub): # Content
        print("\n Layer 7\n")
        while True: 
            updates = bot.get_updates(offset = last_update_id).wait()
            try: 
                for update in updates: 
                    if int(update.update_id) > int(last_update_id): 
                        last_update_id = update.update_id 
                        print("last_update_id: ",last_update_id)
                        process_message_layer7(bot, update, last_update_id, usr, pwd, dest, sub)
                        continue 
                continue 
            except Exception: 
                ex = None 
                print(traceback.format_exc())
                continue

    def process_message_layer6(bot, u, last_update_id, usr, pwd, dest):

        if u.message.sender and u.message.text and u.message.chat: # if the message is text
            chat_id = u.message.chat.id # Extract data of message
            user = u.message.sender.id
            message = u.message.text

            print("\n chat_id: ", chat_id)
            print("user: ", user)
            print("message: ", message)
            print("\n")

            if message == 'Back':
                print("Select an option, Layer 6")
                keyboard = [['Show unseen emails'],['Send a email'], ['Back']]
                reply_markup = ReplyKeyboardMarkup.create(keyboard)
                bot.send_message(chat_id, 'Select an option', reply_markup=reply_markup).wait()
                layer4(bot, last_update_id, usr, pwd)

            else:
                print("Send me the body, Layer 6")
                keyboard = [['Back']]
                reply_markup = ReplyKeyboardMarkup.create(keyboard)
                bot.send_message(chat_id, 'Send me the body', reply_markup=reply_markup).wait()
                layer7(bot, last_update_id, usr, pwd, dest, message)

        else:
            print("Select an option, Layer 6")
            keyboard = [['Show unseen emails'],['Send a email'], ['Back']]
            reply_markup = ReplyKeyboardMarkup.create(keyboard)
            bot.send_message(u.message.chat.id, 'Select an option', reply_markup=reply_markup).wait()
            layer4(bot, last_update_id, usr, pwd)

    def layer6(bot, last_update_id, usr, pwd, dest): #Subject
        print("\n Layer 6\n")
        while True: 
            updates = bot.get_updates(offset = last_update_id).wait()
            try: 
                for update in updates: 
                    if int(update.update_id) > int(last_update_id):
                        last_update_id = update.update_id 
                        print("last_update_id: ",last_update_id)
                        process_message_layer6(bot, update, last_update_id, usr, pwd, dest)
                        continue 
                continue 
            except Exception: 
                ex = None 
                print(traceback.format_exc())
                continue

    def process_message_layer5(bot, u, last_update_id, usr, pwd):

        if u.message.sender and u.message.text and u.message.chat: # if the message is text
            chat_id = u.message.chat.id # Extract data of message
            user = u.message.sender.id
            message = u.message.text

            print("\n chat_id: ", chat_id)
            print("user: ", user)
            print("message: ", message)
            print("\n")


            if message == 'Back':
                print("Select an option, Layer 5")
                keyboard = [['Show unseen emails'],['Send a email'], ['Back']]
                reply_markup = ReplyKeyboardMarkup.create(keyboard)
                bot.send_message(chat_id, 'Select an option', reply_markup=reply_markup).wait()
                layer4(bot, last_update_id, usr, pwd)

            else:
                print("Send me the subject, Layer 5")
                keyboard = [['Back']]
                reply_markup = ReplyKeyboardMarkup.create(keyboard)
                bot.send_message(chat_id, 'Send me the subject', reply_markup=reply_markup).wait()
                layer6(bot, last_update_id, usr, pwd, message)

        else:
            print("Select an option, Layer 5")
            keyboard = [['Show unseen emails'],['Send a email'], ['Back']]
            reply_markup = ReplyKeyboardMarkup.create(keyboard)
            bot.send_message(u.message.chat.id, 'Select an option', reply_markup=reply_markup).wait()
            layer4(bot, last_update_id, usr, pwd)

    def layer5(bot, last_update_id, usr, pwd): #Insert mail address
        print("\n Layer 5\n")
        while True: 
            updates = bot.get_updates(offset = last_update_id).wait()
            try: 
                for update in updates: 
                    if int(update.update_id) > int(last_update_id): 
                        last_update_id = update.update_id 
                        print("last_update_id: ",last_update_id)
                        process_message_layer5(bot, update, last_update_id, usr, pwd)
                        continue 
                continue 
            except Exception: 
                ex = None 
                print(traceback.format_exc())
                continue

    def process_message_layer4(bot, u, last_update_id, usr, pwd):

        global run

        if u.message.sender and u.message.text and u.message.chat: # if the message is text
            chat_id = u.message.chat.id # Extract data of message
            user = u.message.sender.id
            message = u.message.text

            print("\n chat_id: ", chat_id)
            print("user: ", user)
            print("message: ", message)
            print("\n")


            if message == 'Back':
                run = False
                print("Select a option, Layer 4")
                keyboard = [['Loggin account'],['Exit']]
                reply_markup = ReplyKeyboardMarkup.create(keyboard)
                bot.send_message(chat_id, 'Select a option', reply_markup=reply_markup).wait()
                layer2(bot, last_update_id)

            elif message == 'Show unseen emails':
                print('Showing emails, Layer 4')
                bot.send_message(chat_id, 'Showing emails')
                run = True

                th = threading.Thread(target = analizerMail, args=(usr, pwd, chat_id, bot, last_update_id,))
                th.start()

            elif message == 'Send a email':
                run = False
                print('Send me the emails of the destinations (separate with \',\'), Layer 4')
                keyboard = [['Back']]
                reply_markup = ReplyKeyboardMarkup.create(keyboard)
                bot.send_message(chat_id, 'Send me the emails of the destinations (separate with \',\')', reply_markup=reply_markup).wait()
                layer5(bot, last_update_id, usr, pwd)

            else:
                print("Select an option, Layer 4")
                keyboard = [['Show unseen emails'],['Send a email'], ['Back']]
                reply_markup = ReplyKeyboardMarkup.create(keyboard)
                bot.send_message(chat_id, 'Select an option', reply_markup=reply_markup).wait()

        else:
            print("Select an option, Layer 4")
            keyboard = [['Show unseen emails'],['Send a email'], ['Back']]
            reply_markup = ReplyKeyboardMarkup.create(keyboard)
            bot.send_message(u.message.chat.id, 'Select an option', reply_markup=reply_markup).wait()

    def layer4(bot, last_update_id, usr, pwd): #Show emails, send email and back
        print("\n Layer 4\n")
        while True: 
            updates = bot.get_updates(offset = last_update_id).wait()
            try: 
                for update in updates: 
                    if int(update.update_id) > int(last_update_id): 
                        last_update_id = update.update_id 
                        print("last_update_id: ",last_update_id)
                        process_message_layer4(bot, update, last_update_id, usr, pwd)
                        continue 
                continue 
            except Exception: 
                ex = None 
                print(traceback.format_exc())
                continue

    def process_message_layer3(bot, u, last_update_id):

        if u.message.sender and u.message.text and u.message.chat: # if the message is text
            chat_id = u.message.chat.id # Extract data of message
            user = u.message.sender.id
            message = u.message.text

            print("\n chat_id: ", chat_id)
            print("user: ", user)
            print("message: ", message)
            print("\n")


            if message == 'Back':
                print("Select an option, Layer 3")
                keyboard = [['Loggin account'],['Exit']]
                reply_markup = ReplyKeyboardMarkup.create(keyboard)
                bot.send_message(chat_id, 'Select an option', reply_markup=reply_markup).wait()
                layer2(bot, last_update_id)

            else: 

                if len(message.split()) != 2:
                    print("Incorrect input, Layer 3")
                    keyboard = [['Loggin account'],['Exit']]
                    reply_markup = ReplyKeyboardMarkup.create(keyboard)
                    bot.send_message(chat_id, 'Incorrect input', reply_markup=reply_markup).wait()                     
                    bot.send_sticker(chat_id, 'CAADAgAD1wgAAgi3GQJjq91gSNeyaQI', reply_markup=reply_markup).wait()
                    layer2(bot, last_update_id)

                else:

                    user = message.split()[0]
                    pwd  = message.split()[1]


                    # connecting to the gmail imap server
                    imapMail = imaplib.IMAP4_SSL("imap.gmail.com")

                    # Login
                    try:
                        imapMail.login(user,pwd)

                    except:

                        print("User or password incorrect <Sticker>, Layer 3")
                        keyboard = [['Loggin account'],['Exit']]
                        reply_markup = ReplyKeyboardMarkup.create(keyboard)
                        
                        bot.send_message(chat_id, 'User or password incorrect', reply_markup=reply_markup).wait()
                        bot.send_sticker(chat_id, 'CAADAgAD8wgAAgi3GQKHdYrrN-Wt_QI', reply_markup=reply_markup).wait()
                        
                        layer2(bot, last_update_id)



                    print("Logging successful <Sticker>, Layer 3")
                    bot.send_message(chat_id, 'Loggin successful').wait()
                    bot.send_sticker(chat_id, 'CAADAgADsggAAgi3GQITL8y1531UoQI').wait()
                    imapMail.logout()

                    print("Select an option, Layer 3")
                    keyboard = [['Show unseen emails'],['Send a email'], ['Back']]
                    reply_markup = ReplyKeyboardMarkup.create(keyboard)
                    bot.send_message(chat_id, 'Select an option', reply_markup=reply_markup).wait()
                    layer4(bot, last_update_id, user, pwd)

        else:
            print("Incorrect input, Layer 3")
            keyboard = [['Loggin account'],['Exit']]
            reply_markup = ReplyKeyboardMarkup.create(keyboard)
            
            bot.send_message(u.message.chat.id, 'Incorrect input', reply_markup=reply_markup).wait()                     
            bot.send_sticker(chat_id, 'CAADAgAD1wgAAgi3GQJjq91gSNeyaQI', reply_markup=reply_markup).wait()
            
            layer2(bot, last_update_id)

    def layer3(bot, last_update_id): # Loggin
        print("\n Layer 3\n")
        while True: 
            updates = bot.get_updates(offset = last_update_id).wait()
            try: 
                for update in updates:
                    if int(update.update_id) > int(last_update_id): 
                        last_update_id = update.update_id 
                        print("last_update_id: ",last_update_id)
                        process_message_layer3(bot, update, last_update_id)
                        continue 
                continue 
            except Exception: 
                ex = None 
                print(traceback.format_exc())
                continue







    def process_message_layer2(bot, u, last_update_id): 

        if u.message.sender and u.message.text and u.message.chat: # if the message is text
            chat_id = u.message.chat.id # Extract data of message
            user = u.message.sender.id
            message = u.message.text

            print("\n chat_id: ", chat_id)
            print("user: ", user)
            print("message: ", message)
            print("\n")

            if message == 'Loggin account':
                print("Send me your User and Password (separate with space), Layer 2")
                keyboard = [['Back']]
                reply_markup = ReplyKeyboardMarkup.create(keyboard)
                bot.send_message(chat_id, 'Send me your User and Password (separate with space)', reply_markup=reply_markup).wait()
                layer3(bot, last_update_id)

            elif message == 'Exit':
                print("See you later, Layer 2")
                keyboard = [['Start LambderBot']]
                reply_markup = ReplyKeyboardMarkup.create(keyboard)
                bot.send_message(chat_id, 'See you later', reply_markup=reply_markup).wait()
                layer1(bot, last_update_id)

            else: 
                print("Select an option, Layer 2")
                keyboard = [['Loggin account'],['Exit']]
                reply_markup = ReplyKeyboardMarkup.create(keyboard)
                bot.send_message(chat_id, 'Select an option', reply_markup=reply_markup).wait()                  

        else:
            print("Select an option, Layer 2")
            keyboard = [['Loggin account'],['Exit']]
            reply_markup = ReplyKeyboardMarkup.create(keyboard)
            bot.send_message(u.message.chat.id, 'Select an option', reply_markup=reply_markup).wait()

    def layer2(bot, last_update_id): # Loggin or loggout
        print("\n Layer 2\n")
        while True: 
            updates = bot.get_updates(offset = last_update_id).wait()
            try:    
                for update in updates: 
                    if int(update.update_id) > int(last_update_id): 
                        last_update_id = update.update_id 
                        print("\nlast_update_id: ",last_update_id)
                        process_message_layer2(bot, update, last_update_id)
                        continue 
                continue 
            except Exception: 
                ex = None 
                print(traceback.format_exc())
                continue






    def process_message_layer1(bot, u, last_update_id): 

        if u.message.sender and u.message.text and u.message.chat: # if the message is text
            chat_id = u.message.chat.id # Extract data of message
            user = u.message.sender.id
            message = u.message.text

            print("\n chat_id: ", chat_id)
            print("user: ", user)
            print("message: ", message)
            print("\n")

            if message == 'Start LambderBot': # if message is ...
                keyboard = [['Loggin account'],['Exit']] # Buttons Loggin account and Exit
                reply_markup = ReplyKeyboardMarkup.create(keyboard) # Create Button
                
                bot.send_message(chat_id, 'Hello\nSelect an option', reply_markup=reply_markup).wait() # Show message and Button
                bot.send_sticker(chat_id, 'CAADAgAD5QgAAgi3GQLR-yMPZfVRlAI', reply_markup=reply_markup).wait()
                
                print('Hello, Select an option, Layer 1')
                layer2(bot, last_update_id) # Call Second Layer

            elif message == '/start': 
                print("Select an option, Layer 1")
                keyboard = [['Start LambderBot']]
                reply_markup = ReplyKeyboardMarkup.create(keyboard)
                bot.send_message(chat_id, 'Select an option', reply_markup=reply_markup).wait() # update buttons and stay in this layer

            else: 
                print("Select an option, Layer 1")
                keyboard = [['Start LambderBot']]
                reply_markup = ReplyKeyboardMarkup.create(keyboard)
                bot.send_message(chat_id, 'Select an option', reply_markup=reply_markup).wait()                  

        else:
            print("Select an option, Layer 1")
            keyboard = [['Start LambderBot']]
            reply_markup = ReplyKeyboardMarkup.create(keyboard)
            bot.send_message(u.message.chat.id, 'Select an option', reply_markup=reply_markup).wait()

    def layer1(bot, last_update_id): #Welcome layer
        print("\n Layer 1\n")
        while True: # While for message from this layer, because the user can insert bad text
            updates = bot.get_updates(offset = last_update_id).wait()
            try: 
                for update in updates: #get message data
                    if int(update.update_id) > int(last_update_id): #if the message is new, process
                        last_update_id = update.update_id 
                        print("\nlast_update_id: ",last_update_id)
                        process_message_layer1(bot, update, last_update_id) # call process message
                        continue 
                continue 
            except Exception: 
                ex = None 
                print(traceback.format_exc())
                continue

    layer1(bot, last_update_id) # Start first layer


if __name__ == '__main__':
    main()
