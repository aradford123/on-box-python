This python script runs on a Cisco IOS-XE guestshell and will monitor DNS name to keep an ACL updated.

To install required libraries:

```buildoutcfg
sudo -E pip install dnspython

```

install the script in the /flash/gs_script/src/dns_update directory.
If you are doing a git clone, this is easy.
```buildoutcfg
git clone https://github.com/aradford123/on-box-python.git /flash/gs_script
```

Run as (the domain names below are just examples):
```buildoutcfg
/flash/gs_script/src/dns-update/DNS_update.py cisco.com amazon.com
```

The script will update an named access-list called "canary_ip_in" (this can be changed)

It assumes the ACL already exists.  By default you should create it as:

```buildoutcfg
ip access-list extended canary_ip_in
 deny   ip any any
```
The script will look for the lowest TTL in the DNS responses and use that to rechedulle the next time it runs.  
An EEM countdown timer is used for schedulling

```buildoutcfg
9300#show run | sec canary
ip access-list extended canary_ip_in
 remark Added 72.163.4.161 @Wed Jul 12 11:44:11 2017
 permit ip any host 72.163.4.161
 remark Added 54.239.25.208 @Wed Jul 12 11:44:11 2017
 permit ip any host 54.239.25.208
 remark Added 54.239.17.6 @Wed Jul 12 11:44:11 2017
 permit ip any host 54.239.17.6
 remark Added 54.239.26.128 @Wed Jul 12 11:44:11 2017
 permit ip any host 54.239.26.128
 remark Added 54.239.17.7 @Wed Jul 12 11:44:11 2017
 permit ip any host 54.239.17.7
 remark Added 54.239.25.200 @Wed Jul 12 11:44:11 2017
 permit ip any host 54.239.25.200
 remark Added 54.239.25.192 @Wed Jul 12 11:44:11 2017
 permit ip any host 54.239.25.192
 deny   ip any any
```

This is the log information
```
show logging
*Jul 12 11:44:11.174: %SYS-5-USERLOG_NOTICE: Message from tty4(user id: ): "Looking up cisco.com"
*Jul 12 11:44:11.253: %SYS-5-USERLOG_NOTICE: Message from tty4(user id: ): "Looking up amazon.com"
*Jul 12 11:44:11.341: %SYS-5-USERLOG_NOTICE: Message from tty4(user id: ): "adding IP: 72.163.4.161 to ACL: status: Success"
*Jul 12 11:44:11.351: %SYS-5-USERLOG_NOTICE: Message from tty4(user id: ): "adding IP: 54.239.25.208 to ACL: status: Success"
*Jul 12 11:44:11.360: %SYS-5-USERLOG_NOTICE: Message from tty4(user id: ): "adding IP: 54.239.17.6 to ACL: status: Success"
*Jul 12 11:44:11.370: %SYS-5-USERLOG_NOTICE: Message from tty4(user id: ): "adding IP: 54.239.26.128 to ACL: status: Success"
*Jul 12 11:44:11.379: %SYS-5-USERLOG_NOTICE: Message from tty4(user id: ): "adding IP: 54.239.17.7 to ACL: status: Success"
*Jul 12 11:44:11.389: %SYS-5-USERLOG_NOTICE: Message from tty4(user id: ): "adding IP: 54.239.25.200 to ACL: status: Success"
*Jul 12 11:44:11.398: %SYS-5-USERLOG_NOTICE: Message from tty4(user id: ): "adding IP: 54.239.25.192 to ACL: status: Success"
*Jul 12 11:44:11.407: %SYS-5-USERLOG_NOTICE: Message from tty4(user id: ): "reschedule in : 5 seconds: status: Success"
*Jul 12 11:44:17.431: %SYS-5-USERLOG_NOTICE: Message from tty5(user id: ): "Looking up cisco.com"
*Jul 12 11:44:17.509: %SYS-5-USERLOG_NOTICE: Message from tty5(user id: ): "Looking up amazon.com"
*Jul 12 11:44:17.605: %SYS-5-USERLOG_NOTICE: Message from tty5(user id: ): "reschedule in : 56 seconds: status: Success"
```

```buildoutcfg
9300#show run | sec even
event manager applet DNS_update
 event timer countdown time 57
 action 1.0 cli command "enable"
 action 1.1 cli command "guestshell run python bootflash:DNS_update.py cisco.com amazon.com"
```