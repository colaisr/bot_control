import configparser
import smtplib
import ssl

config = configparser.ConfigParser()
config.read('config.ini')

port = 465  # For SSL
password = config['Mail']['pass']
email = config['Mail']['mail']
recepient = config['Mail']['notifyTo']


def send_email(message):
    try:

        print('started')
        # Create a secure SSL context
        context = ssl.create_default_context()
        print('context set')
        test = """New Appointment from Bot- check callendar"""

        with smtplib.SMTP_SSL("smtp.gmail.com", port, context=context) as server:
            print('within')
            server.login(email, password)
            print('loged in')
            server.sendmail(email, recepient, test)
            print('sent')
    except Exception as e:
        print(e)


if __name__ == '__main__':
    send_email("hello test")
