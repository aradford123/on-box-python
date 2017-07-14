::cisco::eem::event_register_syslog pattern "CONFIG_I" maxrun 60
# this is an example of an EEM policy trigger
# think there is a permissions isssue in ios.  need to create directory in IOs, but then cannot update it with git
# need to copy the script to flash:
'''
!need to have the following config in IOS
event manager directory user policy flash:
event manager directory user policy flash:gs_script/src/eem-policy

do guestshell run bootflash:gs_script/utils/update_git.sh

do copy flash:gs_script/src/eem-policy/config_check.py flash:

Y
no event manager policy config_check.py
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

def main():
    eem.action_syslog("config changed")
    logSpark("config changed")

if __name__ == "__main__":
    main()