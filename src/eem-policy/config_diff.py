::cisco::eem::event_register_syslog pattern "CONFIG_I" maxrun 60
# this is an example of an EEM policy trigger
'''
need to have the following config in IOS
event manager directory user policy flash:gs_script/eem-policy
event manager policy config_diff.py
'''
import cli
cli.cli('send log "hello world"')
