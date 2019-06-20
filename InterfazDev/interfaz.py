import sys
from tkinter import *
from tkinter import scrolledtext
from tkinter import messagebox


window = Tk()

window.title("Lambder Email-Client")
window.geometry("800x520+350+100")
window.resizable(width=False, height=False)
labelColor = Label(window, bg="red4", width=120,height=3)
labelColor.pack()
imagen=PhotoImage(file="lambderlogo.png")
fondo=Label(window, image=imagen).place(x=650, y=3)
icon=PhotoImage(file="iconred.png")
iconU=Label(window, image=icon).place(x=4, y=4)
labelUser = Label(window, text="User: lambder@gmail.com" , font=("Century Gothic", 12), bg="red4", fg="white" )
labelUser.place(x=60, y=15)
labelVertical = Label(window, bg="gray83", width=25,height=20)
labelVertical.place(x=12, y=70)
labelHorizontal = Label(window, bg="gray83", width=82,height=20)
labelHorizontal.place(x=210, y=70)


def newEmail():
	windowEmail = Tk()
	windowEmail.title("New Email")
	windowEmail.geometry("500x400+450+200")
	toUser = Label(windowEmail, text="To " , font=("Century Gothic", 10), padx=7, pady=7)
	toUser.grid(column=0, row=0)
	enterUser = Entry(windowEmail,width=50)
	enterUser.grid(column=1, row=0)
	subject =Label(windowEmail, text="Subject: " , font=("Century Gothic", 10), padx=5, pady=7)
	subject.grid(column=0, row=1)
	enterSubject = Entry(windowEmail,width=50)
	enterSubject.grid(column=1, row=1)
	content = scrolledtext.ScrolledText(windowEmail,width=50,height=15)
	content.place(x=20, y=80)
	btnSendEmail = Button(windowEmail, text="Send Email", command=sendEmail, bg="red4", fg="white" , font=("Century Gothic", 10))
	btnSendEmail.place(x=110, y=350)
	btnToAttach = Button(windowEmail, text="To Attach", command=toAttach, bg="red4", fg="white" , font=("Century Gothic", 10))
	btnToAttach.place(x=270, y=350)

def sendEmail():

	messagebox.showinfo('Confirmation', 'Email send!')
	#windowEmail.quit()


def toAttach():
	windowToAttach = Tk()
	windowToAttach.title("To Attach")
	windowToAttach.geometry("400x300+400+250")

def Exit():
	window.destroy()

btnNewEmail = Button(window, text="New email", command=newEmail, bg="red4", fg="white" , font=("Century Gothic", 10))
btnNewEmail.place(x=50, y=80)

btnExit = Button(window, text="Exit", command=Exit, bg="red4", fg="white" , font=("Century Gothic", 10), width=9,height=1)
btnExit.place(x=50, y=120)


window.mainloop()