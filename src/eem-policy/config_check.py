::cisco::eem::event_register_syslog pattern "CONFIG_I" maxrun 60
# this is an example of an EEM policy trigger
# think there is a permissions isssue in ios.  need to create directory in IOs, but then cannot update it with git
# need to copy the script to flash:
'''
!need to have the following config in IOS
event manager directory user policy flash:gs_script/src/eem-policy
event manager directory user policy flash:
event manager policy config_check.py
'''

import eem
import os
import sys
sys.path.append("/flash/gs_script/src")
from utils.spark_utils import getRoomId, postMessage

def logSpark(message):
    sparktoken = os.environ.get("SPARKTOKEN")
    if sparktoken is not None:
        roomId = getRoomId("Sanity", sparktoken)
        postMessage(message, roomId, sparktoken)


eem.action_syslog("helloWorld")
logSpark("helloWorld")
