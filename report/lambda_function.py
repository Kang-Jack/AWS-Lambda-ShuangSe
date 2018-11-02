import os
from datetime import datetime
from urllib.request import Request, urlopen
import cuckoo

def lambda_handler(event, context):
    print('blue and red ball report generate at {}...'.format(str(datetime.now())))
    try:
        cuckoo.handler({'resources':['blue_report']},'context')
        print('Blue report generated at {}'.format(str(datetime.now())))
        cuckoo.handler({'resources':['red_report']},'context')
        print('Red report generated at {}'.format(str(datetime.now())))
    except:
        print('Generating failed!')
        raise
    finally:
        print('Report Processing done at {}'.format(str(datetime.now())))
