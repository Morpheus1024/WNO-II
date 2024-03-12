# Należy zrobić graficznego klienta poczty na protokołach IMAP/POP3 i SMTP. 
# Odebranie maili i ich wyświetlenie.

#wysłanie maila 1p
#autoresponder 1p
#filtracja odebranych maili 2p z wykorzystaniem modelu nlp np. sentence respondera, wyznacza score dla wiadomości
#sortować te wiadomości po score i wyświetlić w oknie

import imaplib
import smtplib
import email
from email.mime.text import MIMEText
import tkinter as tk
from tkinter import ttk
import time
import threading
import spacy

username = "mikolaj.galant@gmail.com"
password= "ldcw fnot qhkn pfjr"


aresponse_state = 0
aresponse_text = " "

all_mail_list = []

mutex = threading.Lock()

def click_on_email(event):
    selected_item = inbox.selection()
    if selected_item:
        temat = inbox.item(selected_item,'values')[1]
        nadawca = inbox.item(selected_item,'values')[0]
        topic_label.config(text=f"Temat: {temat}")
        from_label.config(text=f"Od: {nadawca}")
        mail_text.delete(1.0, tk.END)
        mail_text.insert(tk.END, inbox.item(selected_item,'values')[2])

        #print(temat, nadawca)
        window.update()

def first_read_email():
    email_address = username
    imap_server = "imap.gmail.com"
    smtp_server = "smtp.gmail.com"

    # Logowanie do skrzynki mailowej
    mail = imaplib.IMAP4_SSL(imap_server)
    mail.login(email_address, password)
    mail.select("inbox")

    status, messages = mail.search(None, "ALL")

    message_ids = messages[0].split()[:]
    #inbox.delete(*inbox.get_children())
    first_time=False
    read_email_list=message_ids
    # Clear the contents of the inbox

    for msg_id in message_ids:
        _, msg_data = mail.fetch(msg_id, "(RFC822)")
        raw_email = msg_data[0][1]
        msg = email.message_from_bytes(raw_email)
        body=""
        for part in msg.walk():
            if part.get_content_type() == "text/plain":
                body = part.get_payload(decode=True).decode('utf-8')
                break
            else:
                body=msg.get_payload(decode=True)
        #print(f"Subject: {msg['Subject']}")
        #print(f"From: {msg['From']}")
        #print("\n"+"=" * 40 +"\n")
        inbox.insert("", "end", text=msg['Subject'], values=(msg['From'], msg['Subject'], body))
        
        all_mail_list.append({
            'From': msg['From'],
            'Subject': msg['Subject'],
            'Body': body
        })

    
    window.update()


def read_email():
    global mutex
    with mutex:
        email_address = username
        imap_server = "imap.gmail.com"
        smtp_server = "smtp.gmail.com"

        #Logowanie do skrzynki mailowej
        mail = imaplib.IMAP4_SSL(imap_server)
        mail.login(email_address, password)
        mail.select("inbox")


        status, messages = mail.search(None, "UNSEEN")

        message_ids = messages[0].split()[:]
        #inbox.delete(*inbox.get_children())
        first_time=False
        read_email_list=message_ids
        # Clear the contents of the inbox

        for msg_id in message_ids:
            _, msg_data = mail.fetch(msg_id, "(RFC822)")
            raw_email = msg_data[0][1]
            msg = email.message_from_bytes(raw_email)
            body=" "
            for part in msg.walk():
                if part.get_content_type() == "text/plain":
                    body = part.get_payload(decode=True).decode('utf-8')
                    break
                else:
                    body=msg.get_payload(decode=True)
            #print(f"Subject: {msg['Subject']}")
            #print(f"From: {msg['From']}")
            #print("\n"+"=" * 40 +"\n")
            inbox.insert("", "end", text=msg['Subject'], values=(msg['From'], msg['Subject'], body))
            
            all_mail_list.append({
                'From': msg['From'],
                'Subject': msg['Subject'],
                'Body': body
            })
            
            if aresponse_state:
                send_autoresponse(msg['From'], msg['Subject'], aresponse_text)


        window.update()

def click_on_email(event):
    selected_item = inbox.selection()
    if selected_item:
        temat = inbox.item(selected_item,'values')[1]
        nadawca = inbox.item(selected_item,'values')[0]
        topic_label.config(text=f"Temat: {temat}")
        from_label.config(text=f"Od: {nadawca}")
        mail_text.delete(1.0, tk.END)
        mail_text.insert(tk.END, inbox.item(selected_item,'values')[2])

        #print(temat, nadawca)
        window.update()

def write_email():
    #print("write email")
    
    write_email_window = tk.Toplevel(window)
    write_email_window.title("Napisz wiadomość")
    write_email_window.geometry("500x560")
    write_email_window.resizable(False, False)

    send_frame =ttk.Frame(master=write_email_window)

    send_header_frame = ttk.Frame(master=send_frame)

    send_email_frame=ttk.Frame(master=send_header_frame)
    send_email = ttk.Entry(master=send_email_frame, width=50)
    send_email.focus()
    send_email_label=ttk.Label(master=send_email_frame, text="Adres email: ")
    send_email_label.pack(side="left")
    send_email.pack(side="right")

    send_topic_frame=ttk.Frame(master=send_header_frame)
    send_topic_label=ttk.Label(master=send_topic_frame, text="Temat: ")
    send_topic = ttk.Entry(master=send_topic_frame, width=50)
    send_topic.pack(side="right")
    send_topic_label.pack(side="left")


    send_email_frame.pack(side="top", pady=5)
    send_topic_frame.pack(side="bottom", pady=5)


    send_body= tk.Text(master=send_frame, wrap="word", height=24, width=50)
    send_header_frame.pack(side="top", pady=5)
    send_body.pack()
    send_button = ttk.Button(master=send_frame, text="Wyślij", width=20, command=lambda: deliver_email(send_email.get(), send_topic.get(), send_body.get(1.0, tk.END), write_email_window))
    send_button.pack(side="bottom", pady=5)
    send_frame.pack(side="top")

def deliver_email(email, topic, body, window):
    # print("Adres email:", email)
    # print("Temat:", topic)
    # print("Treść:", body)

    message = MIMEText(body)
    message["Subject"] = topic
    message["From"] = username
    message["To"] = email

    try:
        # Wysyłanie wiadomości e-mail
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(username, password)
            server.sendmail(username, [email], message.as_string())

        print("E-mail został wysłany pomyślnie.")

    except Exception as e:
        print(f"Błąd podczas wysyłania lub odbierania wiadomości: {e}")
    window.destroy()


def autoresponder():
    #print("autoresponder")
    
    autoresponse_window = tk.Toplevel(window)
    autoresponse_window.title("Autoresponder")
    autoresponse_window.geometry("500x560")
    autoresponse_window.resizable(False, False)
    aresponse_header_frame = ttk.Frame(master=autoresponse_window)
    aresponse_body= tk.Text(master=autoresponse_window, wrap="word", height=24, width=50)
    aresponse_bottom_frame =ttk.Frame(master=autoresponse_window)

    check_label = "Włącz"
    aresponse_check = ttk.Checkbutton(master=aresponse_bottom_frame, text=check_label, onvalue=1, offvalue=0)
    aresponse_check.pack(side="left", padx=15)
    
    aresponse_button= ttk.Button(master=aresponse_bottom_frame, text="Zapisz", width=20, command=lambda:autoresponse_set(aresponse_check.instate(['selected']), aresponse_body.get(1.0, tk.END),autoresponse_window))
    aresponse_button.pack(side="right")
    aresponse_header_frame.pack()
    aresponse_body.pack(side="top", pady=15)
    aresponse_bottom_frame.pack(side="bottom", pady=5)
    aresponse_body.pack()

def autoresponse_set(state, text, autoresponse_window):
    global aresponse_state, aresponse_text, mutex
    with mutex:
        #print("autoresponse_set")
        if state:
            print("Autoresponder włączony")
            aresponse_state = 1
            aresponse_text = text
        else:
            print("Autoresponder wyłączony")
            aresponse_state = 0
            aresponse_text = " "

        autoresponse_window.destroy()

        print(aresponse_text, aresponse_state)

def send_autoresponse(sender, subject, message_body):
    global mutex
    with mutex:
        # Wysyłanie automatycznej odpowiedzi
        email_address = username
        smtp_server = "smtp.gmail.com"

        reply_subject = "Automatyczna Odpowiedź: " + subject
        reply_body = "Cześć!\n\n" + message_body + "\nPozdrawiam,\n" + email_address

        # Utwórz obiekt MIMEText dla treści wiadomości
        reply_msg = MIMEText(reply_body)
        reply_msg["Subject"] = reply_subject
        reply_msg["From"] = email_address
        reply_msg["To"] = sender

        # Ustaw połączenie SMTP
        smtp_connection = smtplib.SMTP_SSL(smtp_server)
        smtp_connection.login(email_address, password)

        # Wyślij automatyczną odpowiedź
        smtp_connection.sendmail(email_address, [sender], reply_msg.as_string())
        print("wysłano automatyczą odpowiedź")
        # Zamknij połączenie SMTP
        smtp_connection.quit()    

def refresh_email_periodically():
    while True:
        time.sleep(30)
        print("odswierzenie autoamtyczne")
        read_email()

def search_window():
    # print(search_window)
    search_window_email_window = tk.Toplevel(window)
    search_window_email_window.title("Napisz wiadomość")
    search_window_email_window.geometry("500x460")
    search_window_email_window.resizable(False, False)

    search_frame =ttk.Frame(master=search_window_email_window)
    search_header_frame = ttk.Frame(master=search_frame)
    search_entry=ttk.Entry(master=search_header_frame)


    search_tree = ttk.Treeview(master=search_frame, height=14)
    search_tree["columns"] = ("Od", "Temat", "Tresc")
    search_tree.column("#0", width=0, stretch=tk.NO)
    search_tree.column("Od", anchor=tk.W, width=100)
    search_tree.heading("Od", text="Od", anchor=tk.W)
    search_tree.column("Temat", anchor=tk.W, width=125)
    search_tree.heading("Temat", text="Temat", anchor=tk.W)
    search_tree.column("Tresc", anchor=tk.W, width=225)

    search_button=ttk.Button(master=search_header_frame, text="Szukaj", width=20, command=lambda:search_email(search_entry.get(), search_tree))
    search_entry.pack(side="left")
    search_button.pack(side="right")

    search_header_frame.pack(side='top', pady=10)
    search_tree.pack(side="bottom", pady=5)
    search_frame.pack()

def search_email(search_entry, search_tree_obj):
    global all_mail_list, mutex
    search_tree_obj.delete(*search_tree_obj.get_children())
    sorted_mail_list = []
    with mutex:
        sorted_mail_list = intelligent_search(search_entry, all_mail_list)

    for mail in sorted_mail_list:
        search_tree_obj.insert("", "end", text=mail['Subject'], values=(mail['From'], mail['Subject'], mail['Body']))

def intelligent_search(search_entry, all_mail_list):
    nlp = spacy.load("pl_core_news_sm")
    doc1 = nlp(search_entry)
    frase_list = [element['Body'] for element in all_mail_list]
    podobienstwo=[]

    for frase in frase_list:
        wynik = nlp(frase)
        podobienstwo.append(doc1.similarity(wynik))
    
    sorted_mail_list = [x for _, x in sorted(zip(podobienstwo, all_mail_list), key=lambda pair: pair[0], reverse=True)]
    return sorted_mail_list



#glowne okno
window = tk.Tk()
window.title("Email client")
window.geometry("900x350")
window.resizable(False, False)

menu_bar = tk.Menu(window)
window.config(menu=menu_bar)

option_menu = tk.Menu(menu_bar, tearoff=0)
menu_bar.add_cascade(label="Opcje", menu=option_menu)
option_menu.add_command(label="Odśwież", command=read_email)
option_menu.add_command(label="Napisz nowy", command=write_email)
option_menu.add_separator()
option_menu.add_command(label="Autoresponder", command=autoresponder)
option_menu.add_command(label="Wyszukaj", command=search_window)

#inbox
inbox = ttk.Treeview(master=window, height=14)
inbox["columns"] = ("Od", "Temat", "Tresc")
inbox.column("#0", width=0, stretch=tk.NO)
inbox.column("Od", anchor=tk.W, width=100)
inbox.heading("Od", text="Od", anchor=tk.W)
inbox.column("Temat", anchor=tk.W, width=125)
inbox.heading("Temat", text="Temat", anchor=tk.W)
inbox.column("Tresc", anchor=tk.W, width=225)
inbox.heading("Tresc", text="Treść", anchor=tk.W)
inbox.bind("<Double-1>", click_on_email)
inbox.pack(side='left')

#przycisk do odświeżania i pobierania poczty
button_frame = ttk.Frame(master=window)
refresh_button = ttk.Button(master=button_frame, text="Odśwież", width=20, command=read_email)
new_email_button=ttk.Button(master=button_frame, text="Napisz nowy", width=20, command=write_email)
new_email_button.pack(side="right")
refresh_button.pack(side="left", padx=5)
button_frame.pack(side='top')

#wyswietlanie treści maila
email_section=ttk.Frame(master=window)
header_frame = ttk.Frame(master=email_section)
topic_label = ttk.Label(master=header_frame, text="Temat: ",anchor="center",justify="center")
from_label = ttk.Label(master=header_frame, text="Od: ",anchor="center",justify="center")
topic_label.pack(side='bottom')
from_label.pack(side='top')

mail_frame = ttk.Frame(master=email_section, height=460, width=300)
mail_text = tk.Text(master=mail_frame, wrap="word", height=15, width=48)
mail_text.pack(side="left")
header_frame.pack(side="top")
mail_frame.pack(side="bottom")
email_section.pack(side='right')

if __name__ == "__main__":
    first_read_email()
    threading.Thread(target=refresh_email_periodically, daemon=True).start()
    window.mainloop()
