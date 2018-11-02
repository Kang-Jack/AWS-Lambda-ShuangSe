import datetime
import boto3
from jinja2 import Template

# Start of some things you need to change
#
#
# Recipient emails or domains in the AWS Email Sandbox must be verified
# You'll want to change this to the email you verify in SES
FROM_ADDRESS='arixxxse.xxx@gmail.com'
REPLY_TO_ADDRESS='xxx.xxx@gmail.com'

# You'll also need to change these to email addresses you verify in AWS
CLIENTS = [
    # Format: [email, 'first name', 'last name', 'pet name']
    ['xxx@xxx.com', 'Zoe', 'Washburne', 'Firefly II'],
    ['xxx.xxx@xxx.com', 'Fernando', 'Medina Corey', 'Riley']                
]

EMPLOYEES = [
    # Content stored in this order: [email, first_name, last_name]
    # Change to any email you verify in SES
    ['xxx@xxx.com', 'Homer', 'Simpson']
]

# Change to the bucket you create on your AWS account
TEMPLATE_S3_BUCKET = 'xx-xx-xxx'
#
#
# End of things you need to change

def get_template_from_s3(key):
    """Loads and returns html template from Amazon S3"""
    s3 = boto3.client('s3')
    s3_file = s3.get_object(Bucket = TEMPLATE_S3_BUCKET, Key = key)
    try:
        template = Template(s3_file['Body'].read().decode('utf-8'))
    except Exception as e:
        print ('Failed to load template')
        raise e
    return template

def render_come_to_work_template(employee_first_name):
    subject = 'Work Schedule Reminder'
    template = get_template_from_s3('come_to_work.html')
    html_email = template.render(first_name = employee_first_name)
    plaintext_email = 'Hello {0}, \nPlease remember to be into work by 8am'.format(employee_first_name)
    return html_email, plaintext_email, subject

def render_daily_tasks_template(sqls):
    subject = 'ShuangSe update records'

    records=[[]]
    for sql in sqls:
        startI=sql.find('VALUES (')+8
        if startI < 1:
            continue
        else :
            strT = sql[startI:]
            endI = strT.find(')')
            strT = strT =strT[:endI]
            records.append(strT.split(','))

    template = get_template_from_s3('daily_tasks.html')
    tasks = {
        'Monday': '1. New lottery record update\n',
        'Tuesday': '1. Lottery day!\n',
        'Wednesday': '1. New lottery record update\n',
        'Thursday': '1. Lottery day!\n',
        'Friday': '1. New lottery record update\n',
        'Saturday': '1. Relax!\n2. Play with the pets! It\'s the weekend!\n',
        'Sunday': '1. Lottery day!\n'
    }
    # Gets an integer value from 0 to 6 for today (Monday - Sunday)
    # Keep in mind this will run in GMT and you will need to adjust runtimes accordingly 
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    today = days[datetime.date.today().weekday()]
    html_email = template.render(day_of_week = today, daily_tasks = tasks[today], records = records, sqls = sqls)
    plaintext_email = (
        "Remember of day:\n"
        "1. Monday: '1. New lottery record update\n"
        "2. Tuesday: '1. Lottery day!\n"
        "3. Wednesday: '1. New lottery record update\n"
        "4. Thursday: '1. Lottery day!\n"
        "5. Friday: '1. New lottery record update\n"
        "6. Saturday': '1. Relax!\n2. Play with the pets! It\'s the weekend!\n",
        "7. Sunday: '1. Lottery day!\n"
        "And:\n"
        "{0}".format(tasks[today])
    )
    return html_email, plaintext_email, subject

def render_pickup_template(client_first_name, client_pet_name):
    subject = 'Pickup Reminder'
    template = get_template_from_s3('pickup.html')
    html_email = template.render(first_name = client_first_name, pet_name = client_pet_name)
    plaintext_email = 'Hello {0}, \nPlease remember to pickup {1} by 7pm!'.format(client_first_name, client_pet_name)
    return html_email, plaintext_email, subject

def send_email(html_email, plaintext_email, subject, recipients):
    try:
        ses = boto3.client('ses',region_name='us-east-1')
        response = ses.send_email(
            Source=FROM_ADDRESS,
            Destination={
                'ToAddresses': recipients,
                'CcAddresses': [],
                'BccAddresses': []
            },
            Message={
                'Subject': {
                    'Data': subject,
                },
                'Body': {
                    'Text': {
                        'Data': plaintext_email
                    },
                    'Html': {
                        'Data': html_email
                    }
                }
            },
            ReplyToAddresses=[
                REPLY_TO_ADDRESS,
            ]
        )
    except Exception as e:
        print ('Failed to send message via SES')
        print (e.message)
        raise e

def handler(event,context):
    event_trigger = event['resources'][0]
    print ('event triggered by ' + event_trigger)
    if 'records_updated' in event_trigger:
        for employee in EMPLOYEES:
            email = []
            email.append(employee[0])
            html_email, plaintext_email, subject = render_daily_tasks_template(context)
            send_email(html_email, plaintext_email, subject, email)
    else:
        return 'No template for this trigger!'

