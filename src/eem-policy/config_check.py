::cisco::eem::event_register_syslog pattern "CONFIG_I" maxrun 60
# this is an example of an EEM policy trigger
# think there is a permissions isssue in ios.  need to create directory in IOs, but then cannot update it with git
# need to copy the script to flash:
'''
!need to have the following config in IOS
event manager directory user policy flash:
event manager policy config_check.py
'''

import eem
eem.action_syslog("helloWorld")
