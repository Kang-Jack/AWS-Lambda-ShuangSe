import datetime
import boto3
from jinja2 import Template
from analyze_blue import analyze_blue
from analyze_red import analyze_red
# Start of some things you need to change
#
#
# Recipient emails or domains in the AWS Email Sandbox must be verified
# You'll want to change this to the email you verify in SES
debug = 0
FROM_ADDRESS='xxxxxx@xxx.com'
REPLY_TO_ADDRESS='xxx@xxx.com'

# You'll also need to change these to email addresses you verify in AWS
CLIENTS = [
    # Format: [email, 'first name', 'last name', 'pet name']
    #['xxx@gmail.com', 'xxx', 'K', 'gmail'],  
    ['xx@xx.com', 'laser', 'K', 'sina']             
]

EMPLOYEES = [
    # Content stored in this order: [email, first_name, last_name]
    # Change to any email you verify in SES
    ['xx@xx.com', 'xx', 'xx']
]

# Change to the bucket you create on your AWS account
TEMPLATE_S3_BUCKET = 'xxx-xxx-xxx'
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

def render_error_reminder_template(employee_first_name):
    subject = 'ShuangSe error Reminder'
    template = get_template_from_s3('come_to_work.html')
    template_vars = {
        'first_name':employee_first_name
    }
    html_email = template.render(template_vars)
    plaintext_email = 'Hello {0}, \nPlease check AWS, there is an error occurred!'.format(employee_first_name)
    return html_email, plaintext_email, subject

def render_red_report_template(client_first_name):
    subject = 'Shuang Se red Report'
    template = get_template_from_s3('shuangse_report.html')
    print(template)
    analyzer = analyze_red()
    if debug == 1: print ('===start===')
    red_matrix_frame = analyzer.get_red_matrix_df ()

    df_indexed =  analyzer.get_indexed_red_matrix(red_matrix_frame)
    
    red_matrix_len =len(df_indexed)
    
    df_r = analyzer.get_historical_rounds (df_indexed)
    
    start = df_r.loc[len(df_r)-1,0].astype(int)+1

    if debug == 1: print (df_r.values.tolist())
    table_r = df_r.values.astype(int).tolist()
    df_r_des = analyzer.get_historical_rounds_describe(df_r)
    
    ls_des= [[]]
    ls_title =['count','mean','std','min','25%','50%','75%','max']
    i=0
    for ls in df_r_des.values.astype(int).tolist():
        ls.append(ls_title[i])
        i=i+1
        ls_des.append(ls)
    if debug == 1: print (ls_des)

    table_r_des = ls_des
    current_red = analyzer.get_current_red_frame(red_matrix_frame,start,red_matrix_len)
    if debug == 1: print(current_red.values.tolist())  
    table_current_red = current_red.values.astype(int).tolist()
    lenRound=red_matrix_len-start
    template_vars = {
        'statisitics':table_r,
        'describes':table_r_des,
        'balls':table_current_red,
        'round':lenRound,
        'balltype':'red'
    }

    html_email = template.render(template_vars)
    
    plaintext_email = 'Hello {0}, \nPlease check the new analyze report on red ball!'.format(client_first_name)
    return html_email, plaintext_email, subject

def render_blue_report_template(client_first_name):
    subject = 'Shuang Se blue Report'
    template = get_template_from_s3('shuangse_report.html')
    print(template)
    analyzer = analyze_blue()
    if debug == 1: print ('===start===')
    blue_matrix_frame = analyzer.get_blue_matrix_df ()

    df_indexed =  analyzer.get_indexed_blue_matrix(blue_matrix_frame)
    
    blue_matrix_len =len(df_indexed)
    
    df_r = analyzer.get_historical_rounds (df_indexed)
    
    start = df_r.loc[len(df_r)-1,0].astype(int)+1

    if debug == 1: print (df_r.values.tolist())
    table_r = df_r.values.astype(int).tolist()
    df_r_des = analyzer.get_historical_rounds_describe(df_r)
    
    ls_des= [[]]
    ls_title =['count','mean','std','min','25%','50%','75%','max']
    i=0
    for ls in df_r_des.values.astype(int).tolist():
        ls.append(ls_title[i])
        i=i+1
        ls_des.append(ls)
    if debug == 1: print (ls_des)

    table_r_des = ls_des
    current_blue = analyzer.get_current_blue_frame(blue_matrix_frame,start,blue_matrix_len)
    if debug == 1: print(current_blue.values.tolist())  
    table_current_blue = current_blue.values.astype(int).tolist()
    lenRound=blue_matrix_len-start
    template_vars = {
        'statisitics':table_r,
        'describes':table_r_des,
        'balls':table_current_blue,
        'round':lenRound,
        'balltype':'blue'
    }

    html_email = template.render(template_vars)
    
    #html_email = template.render('shuangse_report.html', statisitics=table_r,describes=table_r_des,balls=table_current_blue,round=lenRound,balltype='blue')
    plaintext_email = 'Hello {0}, \nPlease check the new analyze report on blue ball!'.format(client_first_name)
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
    if 'error_reminder' in event_trigger:
        for employee in EMPLOYEES:
            email = []
            email.append(employee[0])
            employee_first_name = employee[1]
            html_email, plaintext_email, subject = render_error_reminder_template(employee_first_name)
            send_email(html_email, plaintext_email, subject, email)
    elif 'red_report' in event_trigger:
        for client in CLIENTS:
            email = []
            email.append(client[0])
            client_first_name = client[1]
            html_email, plaintext_email, subject = render_red_report_template(client_first_name)
            send_email(html_email, plaintext_email, subject, email)
    elif 'blue_report' in event_trigger:
        for client in CLIENTS:
            email = []
            email.append(client[0])
            client_first_name = client[1]
            html_email, plaintext_email, subject = render_blue_report_template(client_first_name)
            send_email(html_email, plaintext_email, subject, email)
    else:
        return 'No template for this trigger!'

