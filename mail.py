import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# Define email parameters
gmail_user = "roymanit2004@gmail.com"  # Replace with your Gmail address
app_password = "wuhn wxdj uzej nyxc"    # Replace with your App Password

def send_email(to_email, subject, message):
    # Create the email
    msg = MIMEMultipart()
    msg['From'] = gmail_user
    msg['To'] = to_email
    msg['Subject'] = subject

    # Attach the message body to the email
    msg.attach(MIMEText(message, 'plain'))

    try:
        # Set up the server
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()  # Enable security
        server.login(gmail_user, app_password)  # Log in to your Gmail account

        # Send the email
        server.send_message(msg)
        server.quit()  # Disconnect from the server

        print("Email sent successfully!")
    except Exception as e:
        print(f"Error sending email: {e}")

# Example usage
# send_email(
#     to_email="manit.roy@research.iiit.ac.in",  # Replace with recipient's email
#     subject="Test Email",
#     message="This is a test email sent from Python!"
# )