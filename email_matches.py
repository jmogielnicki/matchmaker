
from __future__ import print_function
import base64
import googleapiclient.errors as errors
import httplib2
import os
import utils

from apiclient import discovery
from consts import OFFICE_LIST_RANGE_NAME, OPT_OUT_RANGE_NAME, OUTPUT_RANGE_NAME, SPREADSHEET_ID
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage
from email.mime.text import MIMEText


try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/gmail-python-quickstart.json
# SCOPES = 'https://www.googleapis.com/auth/gmail.readonly'
SCOPES = 'https://www.googleapis.com/auth/gmail.send'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Gmail API Python Quickstart'


def get_credentials():
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'gmail-python-quickstart.json')

    store = Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else: # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials

def create_message(sender, to, subject, message_text):
  """Create a message for an email.

  Args:
    sender: Email address of the sender.
    to: Email address of the receiver.
    subject: The subject of the email message.
    message_text: The text of the email message.

  Returns:
    An object containing a base64url encoded email object.
  """
  message = MIMEText(message_text, 'html')
  message['to'] = to
  message['from'] = sender
  message['subject'] = subject
  message['reply-to'] = 'no-reply-seattle-knit@pinterest.com'
  return {'raw': base64.urlsafe_b64encode(message.as_string())}


def send_message(service, user_id, message):
  """Send an email message.

  Args:
    service: Authorized Gmail API service instance.
    user_id: User's email address. The special value "me"
    can be used to indicate the authenticated user.
    message: Message to be sent.

  Returns:
    Sent Message.
  """
  try:
    message = (service.users().messages().send(userId=user_id, body=message)
               .execute())
    print('Message Id: %s' % message['id'])
    return message
  except errors.HttpError, error:
    print('An error occurred: %s' % error)


def get_recipients_str(data):
    recipients = []
    for recipient in data:
        recipients.append(recipient['ldap'] + '@pinterest.com')
    return ', '.join(recipients)

def get_recipient_names(data):
    recipients = []
    for recipient in data:
        recipients.append(recipient['name'])
    return ', '.join(recipients)


def email_pairs(service, recipients_dict):
    for recipients_list in recipients_dict.values():
        subject = 'Seattle Knitting Match for Week of 9/4'
        sender = 'Seattle Knitting <knit-seattle@pinterest.com>'
        # message_text = 'Hi all,\n\nCongratulations! Here is your Seattle Knitting match for this week: '
        # message_text += get_recipient_names(recipients_list)
        # message_body = "\nAll of you are in this email thread, so just hit \"Reply All\" to start a conversation and coordinate a time to meet up this week. " \
        # + "Feel free to go for a walk, grab a coffee, or sit and chat in the lunch area! Here are a few conversation starters that you may find useful: " \
        # + "https://w.pinadmin.com/display/SEAT/Seattle+Knitting. \n\nCheers,\nSeattle Knitting Association (SKA)"
        html = """\
        <html>
        <head></head>
        <body>
            <p>Hi all,<br><br>
            \n\nCongratulations, you have been matched! Your knitting group this week is: <b>""" \
        + get_recipient_names(recipients_list) + """\
            </b><br><br>
            All of you are in this email thread, so just hit \"Reply All\" to start a conversation and coordinate a time to meet up this week.
            Feel free to go for a walk, grab a coffee, or sit and chat in the lunch area! Here are a few <a href="https://w.pinadmin.com/display/SEAT/Seattle+Knitting">conversation starters</a> that you may find useful.
            </p>
        </body>
        </html>
        """
        recipients = get_recipients_str(recipients_list)
        msg = create_message(sender, recipients, subject, html)
        print("Sending to " + recipients)
        send_message(service=service, user_id='me', message=msg)


def main():
    """Shows basic usage of the Gmail API.

    Creates a Gmail API service object and outputs a list of label names
    of the user's Gmail account.
    """
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('gmail', 'v1', http=http)
    match_list = utils.get_data_from_google_sheets(SPREADSHEET_ID, OUTPUT_RANGE_NAME)
    match_list = utils.convert_sheets_data_to_list_of_dicts(data=match_list)
    recipients = utils.pivot_list_of_dicts_to_nested_dict(match_list, 'match_id')
    print(recipients)
    # recipients = {0: [{'ldap': u'jschlegel', 'match_id': 0, 'name': u'Jason Schlegal', 'team': u''}, {'ldap': u'jmogielnicki', 'match_id': 0, 'name': u'John Mogielnicki', 'team': u'CPX'}]}
    # email_pairs(service, recipients)



if __name__ == '__main__':
    main()
