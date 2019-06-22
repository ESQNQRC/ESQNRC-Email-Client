from tkinter import *
from tkinter import scrolledtext
from tkinter import messagebox
import email, getpass, imaplib, os, time, threading, configparser, string, smtplib, sys, re,socket, dns.resolver
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

userConfig = {
    "database.user": "",
    "database.password": ""}

run = True #stop the daemon in False

bls = ["zen.spamhaus.org", "dnsbl.inps.de"] # Use only bls because time problems



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



###########################
 # send message function
def sendMessage(toDestino, subject, body, filesToTransfer):

    toDestiny = toDestino.split(",")
    filesToSend = filesToTransfer.split(",")
    urlsSubject = re.findall('(http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|(?:%[0-9a-fA-F][0-9a-fA-F]))+)', subject)
    urlsBody = re.findall('(http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|(?:%[0-9a-fA-F][0-9a-fA-F]))+)', body)

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


    if filesToSend != ['']:
       
        for file_name in filesToSend:
            try:
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
                messagebox.showerror("Error", 'File not found')
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

    del msgMail
####################################  sendMessage ####################################################



################################################
# This function checks for unseen emails
def analizerMail(user, pwd):

    # connecting to the gmail imap server
    imapMail = imaplib.IMAP4_SSL("imap.gmail.com")

    # Login
    try:
        imapMail.login(user,pwd)
    except:
        messagebox.showinfo("Error", 'User or password incorrect')
        btnNewEmail.place_forget()
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
                    try:
                    	resp = "["+mail["From"]+"] :" + mail["Subject"] + "\n"
                    	text2.configure(state="normal")
                    	text2.insert(END, resp)
                    	text2.configure(state="disabled")
                    except:
                    	exit()

            # If this list is not empty, then i got some new emails
            if listOfEmailsID:
                listOfShowedEmailsID.extend(listOfEmailsID)
                listOfEmailsID.clear()

    finally:        

        imapMail.logout()
###################################### analizerMail #################################################



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
############## loadConfig#######################



def newEmail():
	windowEmail = Tk()
	windowEmail.title("New Email")
	windowEmail.geometry("500x420+450+200")
	toUser = Label(windowEmail, text="To " , font=("Century Gothic", 10), padx=7, pady=7)
	toUser.grid(column=0, row=0)

	enterUser = Entry(windowEmail,width=50)
	enterUser.grid(column=1, row=0)
	subject =Label(windowEmail, text="Subject: " , font=("Century Gothic", 10), padx=5, pady=7)
	subject.grid(column=0, row=1)
	enterSubject = Entry(windowEmail,width=50)
	enterSubject.grid(column=1, row=1)
	content = scrolledtext.ScrolledText(windowEmail,width=50,height=15)
	content.place(x=50, y=100)


	toAtt = Label(windowEmail, text="Name files" , font=("Century Gothic", 10), padx=7, pady=7)
	toAtt.grid(column=0, row=2)
	toAttach = Entry(windowEmail,width=50)
	toAttach.grid(column=1, row=2)

	def sendEmail():
		sendMessage(enterUser.get(), enterSubject.get(), content.get("0.0",END), toAttach.get())
		
		messagebox.showinfo('Confirmation', 'Email send!')
		windowEmail.destroy()

	btnSendEmail = Button(windowEmail, text="Send Email", command=sendEmail, bg="red4", fg="white" , font=("Century Gothic", 10))
	btnSendEmail.place(x=190, y=373)

def toAttach():
	windowToAttach = Tk()
	windowToAttach.title("To Attach")
	windowToAttach.geometry("400x300+400+250")



def Exit():
	window.destroy()
	run = False
	exit()



loadConfig("config.ini")

window = Tk()

window.title("Lambder Email-Client")
window.geometry("620x400+350+100")
window.resizable(width=False, height=False)
labelColor = Label(window, bg="red4", width=120,height=3)
labelColor.pack()
imagen=PhotoImage(file="lambderlogo.png")
fondo=Label(window, image=imagen).place(x=650, y=3)
icon=PhotoImage(file="iconred.png")
iconU=Label(window, image=icon).place(x=4, y=4)
labelUser = Label(window, text="User: "+userConfig["database.user"] , font=("Century Gothic", 12), bg="red4", fg="white" )
labelUser.place(x=60, y=15)
labelVertical = Label(window, bg="gray83", width=25,height=20)
labelVertical.place(x=12, y=70)
labelHorizontal = Label(window, bg="gray83", width=82,height=20)
labelHorizontal.place(x=210, y=70)



text2 = Text(window, height=19.5, width=50)
scroll = Scrollbar(window, command=text2.yview)
text2.configure(yscrollcommand=scroll.set)
text2.configure(state="disabled")
text2.bind('follow',"<1>", lambda event, t=text2: text2.insert(END,"""Hola"""))

scroll.pack(side=RIGHT, fill=Y)
text2.pack(side=RIGHT)
text2.place(x=200, y=55)


# get user from userConfig
user = userConfig["database.user"]
# get password from userConfig
pwd = userConfig["database.password"]

btnNewEmail = Button(window, text="New email", command=newEmail, bg="red4", fg="white" , font=("Century Gothic", 10))
btnNewEmail.place(x=50, y=180)

btnExit = Button(window, text="Exit", command=Exit, bg="red4", fg="white" , font=("Century Gothic", 10), width=9,height=1)
btnExit.place(x=50, y=230)

# If no user or pass provided
if (user == "" or pwd == ""):
	messagebox.showinfo("Error", 'User or password empty')
	window.destroy()

try:

	th = threading.Thread(target = analizerMail, args=(user, pwd,))
	th.start()
	window.mainloop()

except: 
	run = False
	exit()