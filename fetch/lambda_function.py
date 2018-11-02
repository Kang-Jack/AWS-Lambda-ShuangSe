from fetch_new_lottery_info import saveNewData2DB
import boto3
import os
import json
from datetime import datetime
from urllib.request import Request, urlopen
import cuckoo

num = os.environ['num']  # URL of the site to check, stored in the site environment variable
snsArn = os.environ['sns_arn']

def lambda_handler(event, context):
    print('Fetching lottery at {}...'.format(event['time']))
    try:
        rs = saveNewData2DB(num)
        if (rs == [] ):
            cuckoo.handler({'resources':['error_reminder']}, 'context')
            raise Exception('Validation failed')
        else:
            print (rs)
            cuckoo.handler({'resources':['records_updated']},rs)
            sns = boto3.client('sns')
            message = 'Fetching done!'
            print(message)
            response = sns.publish(
                TargetArn = snsArn,
                Message = json.dumps({
                    'default' :  json.dumps(message)
                }),
                MessageStructure = 'json'
                )
            return event['time']
    except:
        print('Fetching failed!')
        raise
    finally:
        print('Fetching complete at {}'.format(str(datetime.now())))
