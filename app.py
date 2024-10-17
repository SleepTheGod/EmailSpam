from flask import Flask, request
import smtplib
from email.mime.text import MIMEText
from faker import Faker
import threading

app = Flask(__name__)

# SMTP server configuration
SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 587
EMAIL = 'your_email@gmail.com'
PASSWORD = 'your_email_password'

fake = Faker()

# Function to send a single email
def send_single_email(subject, body, recipient):
    try:
        fake_email = fake.email()

        # Create the email content
        msg = MIMEText(f"From: {fake_email}\n\n{body}")
        msg['Subject'] = subject
        msg['From'] = fake_email
        msg['To'] = recipient

        # Connect to SMTP server
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(EMAIL, PASSWORD)

        # Send email
        server.sendmail(fake_email, recipient, msg.as_string())
        server.quit()

    except Exception as e:
        print(f"Error sending email to {recipient}: {str(e)}")

# Function to send emails in parallel
def send_emails(subject, body, recipients, num_emails):
    threads = []
    for _ in range(num_emails):
        for recipient in recipients:
            thread = threading.Thread(target=send_single_email, args=(subject, body, recipient))
            thread.start()
            threads.append(thread)

    # Wait for all threads to complete
    for thread in threads:
        thread.join()

@app.route('/')
def index():
    return '''
        <form action="/send" method="POST">
            <label>Recipients (comma-separated):</label><br>
            <input type="text" name="recipients" placeholder="example1@gmail.com, example2@gmail.com"><br><br>
            <label>Subject:</label><br>
            <input type="text" name="subject" placeholder="Spam Subject"><br><br>
            <label>Body:</label><br>
            <textarea name="body" rows="5" cols="50" placeholder="Spam Body"></textarea><br><br>
            <label>Number of Emails:</label><br>
            <input type="number" name="num_emails" min="1" max="1000" value="1"><br><br>
            <button type="submit">Send Spam Emails</button>
        </form>
    '''

@app.route('/send', methods=['POST'])
def send_email():
    subject = request.form['subject']
    body = request.form['body']
    recipients = request.form['recipients'].split(',')
    num_emails = int(request.form['num_emails'])

    # Call the function to send emails in parallel
    threading.Thread(target=send_emails, args=(subject, body, recipients, num_emails)).start()

    return f"Started sending {num_emails} emails to {', '.join(recipients)}. Check your inboxes!"

if __name__ == '__main__':
    app.run(debug=True)
