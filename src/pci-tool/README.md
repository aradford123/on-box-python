#pci-check

This is a PCI-compliance use case.  The desired outcome is that any switch ports that have been inactive for > 7 days should be 
administratively shutdown.

This script will check the interface status on all switch ports.  Those that have not been active for > 7 days
and are not administratively disabled, will be administratively shutdown.

This script can be installed to run 15 mins past the hour with the following Embedded Event Manager (EEM)
configuration on your switch

```buildoutcfg
event manager applet PCI-check
 event timer cron cron-entry "15 * * * 1-5"
 action 1.0 cli command "enable"
 action 1.1 cli command "guestshell run python bootflash:gs_script/src/pci-tool/pci_check.py --apply"

```

The script can be run in "test" mode by leaving off the "--apply" flag

The script will log to syslog on box as well as Cisco SparkRoom.  In order to send to a sparkroom, you need to 
define the name of the room and insert a SPARKTOKEN into the environment variables in the guest shell

A simple way of making this persist is to edit the file "~/.bashrc" and add the following line:

```buildoutcfg
export SPARKTOKEN="Bearer XXXXXXXXXXX
```
To install required libraries (you need -E if you have proxy settings in your environment variables):

```buildoutcfg
sudo -E pip install dnspython

```
