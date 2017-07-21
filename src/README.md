#On-Box Python scripts
This is a collection of sample on box-python scripts for Cisco devices.

each can be run standalone.  They illustrate different use cases for on-box Python, namely

- Scale - see pci-tool
- Security - see dns-update
- Autonomy - see eem-policy

Each script uses the Embeded Event Manager (EEM) to launch it in a slightly different way

There is also a utility script that can be schedulled to keep these scripts updated on your device

You need to add the following EEM configuration to your network device.  
This example runs the update_git.sh script at the top and bottom of the hour.  
This requires git to be installed on the device.

```buildoutcfg
event manager applet GIT-sync
 event timer cron cron-entry "0,30 * * * *"
 action 1.0 cli command "enable"
 action 1.1 cli command "guestshell run bootflash/gs_script/src/util/update_git/sh"

```

## Enabling GuestShell
Guestshell is a hosted application on IOS devices.  In order to use it, you require the IOS application hosting
framework called IOX

This needs to be configured:
```buildoutcfg
9300# conf t
9300(config)#iox
```

You can then enable guestshell from exec mode.
```buildoutcfg
9300# guestshell enable
Management Interface will be selected if configured
Please wait for completion

```

It will take a a minute or so to complete.  Once it has you can either run a command 
inline or just open a shell.

```buildoutcfg
9300#guestshell run echo "hello world"
hello world

or 

9300#guestshell
[guestshell@guestshell ~]$ 

```

Python can be run in a similat way:
```buildoutcfg
9300#guestshell run python -c "print 'hello world'"

or 

9300#guestshell
[guestshell@guestshell ~]$python 

```

##Optimizing Python
One of the first things you will want to do is install new python modules.
The guestshell does not have dns setup, so the first thing to do is to edit /etc/resolv.conf

Use you favorite unix editor, or you can just run the following command to update the file.
```buildoutcfg
echo -e "nameserver 8.8.8.8\ndomain cisco.com" > /etc/resolv.conf

```
Now you should have access to the internet.  If your device needs to connect out via a proxy, then you will need to 
update the proxy environment variables.  I normally store these in ~/.bashrc so they persist between guestshell sessions.
```buildoutcfg
export http_proxy=http://proxy.abc.com:80/
export https_proxy=http://proxy.abc.com:80/
export ftp_proxy=http://proxy.abc.com:80/
export no_proxy=.abccom
export HTTP_PROXY=http://proxy.abc.com:80/
export HTTPS_PROXY=http://proxy.abc.com:80/
export FTP_PROXY=http://proxy.abc.com:80/
```
Next you can install some python modules. NOTE: if you are using a proxy you will need to use "sudo -E" 
to use the environment variables above with Pip.  I am installing these into the global library, so I need to "sudo".
I could also use a virtualenv if I wanted to.

```buildoutcfg
[guestshell@guestshell ~]$ sudo -E  pip install netaddr
Collecting netaddr
  Downloading netaddr-0.7.19-py2.py3-none-any.whl (1.6MB)
    100% |################################| 1.6MB 257kB/s 
Installing collected packages: netaddr
Successfully installed netaddr-0.7.19

```
*NOTE:  Catalyst 3k platforms have a limiation in that there is no gcc compiler installed.  You will not (easily) be 
able to install modules that require C compilation*

## Installing Git
Git is an extremely useful tool for sharing, collaborating and updating code.



