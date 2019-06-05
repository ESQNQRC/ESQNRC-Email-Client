import email, getpass, imaplib, os, time
import threading


#################################################################################################################
#               Team: Lambder                                                                                   #
#                   Cesar Salazar                                                                               #
#                   Daniel Berbesi                                                                              #
#                   Saul                                                                                        #
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

def analizerMail( ):
    
    user= "esqnqrc.group@gmail.com"  #input("Enter your GMail username:")
    pwd = "cebevasa"  #getpass.getpass("Enter your password: ")

    # connecting to the gmail imap server
    imapMail = imaplib.IMAP4_SSL("imap.gmail.com")
    # Login
    imapMail.login(user,pwd)
    # List all the mails

    # Idle loop
    while True:

        imapMail.list()

        imapMail.select('Inbox') # here you a can choose a mail box like spam instead

        print("Checking inbox")

        (resp, data) = imapMail.search(None, '(UNSEEN)') # filter unseen mails

        data = data[0].split() # getting the mails id

        for emailid in data:

            print("Processing : ")
    
            resp, data = imapMail.fetch(emailid, "(RFC822)") # fetching the mail, "`(RFC822)`" means "get the whole stuff", but you can ask for headers only, etc
    
            email_info = data[0][1] # getting the mail content
    
            mail = email.message_from_bytes(email_info) # parsing the mail content to get a mail object
    
            (resp, data) = imapMail.store(emailid, '-FLAGS', '\\Seen') # Mark email as unseen again (bc fetching brings body of email too)

            #Check if any attachments at all
            if mail.get_content_maintype() != 'multipart':
                continue

            print ("["+mail["From"]+"] :" + mail["Subject"] + "\n")

        time.sleep(10)



#####################################################   MAIN  #############################################

threadFunction = threading.Thread(target=analizerMail)

threadFunction.start()

threadFunction.join()

imapMail.logout()