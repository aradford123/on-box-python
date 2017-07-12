This python script runs on a Cisco IOS-XE guestshell and will monitor DNS name to keep an ACL updated.

To install required libraries:

```buildoutcfg
sudo -E pip install dnspython

```

install the script in the /flash directory

Run as (the domain names below are just examples):
```buildoutcfg
/flash/DNS_update.py cisco.com amazon.com
```

The script will update an named access-list called "canary_ip_in" (this can be changed)

It assumes the ACL already exists.  By default you should create it as:

```buildoutcfg
ip access-list extended canary_ip_in
 deny   ip any any
```
The script will look for the lowest TTL in the DNS responses and use that to rechedulle the next time it runs.  
An EEM countdown timer is used for schedulling

