#!/usr/bin/env python
import sys
import time
import re
from dns import resolver
from dns.resolver import NXDOMAIN
from dns.resolver import NoAnswer
from dns.resolver import NoNameservers
from dns.exception import Timeout
from cli import cli
from cli import configure

ACLNAME = "canary_ip_in"


def log(message, severity):
    '''
    this can also log to spark.  need to check if a token is present
    :param message:
    :param severity:
    :return:
    '''
    cli('send log %d "%s"' % (severity, message))


def dns_lookup(name):
    log("Looking up %s" % name, 5)
    try:
        answers = resolver.query(name, 'A')
        return answers.rrset.ttl, [answer.address for answer in answers]
    except NXDOMAIN:
        pass
    except NoAnswer:
        pass
    except NoNameservers:
        pass
    except Timeout:
        pass


def get_acl_ip():
    '''
    returns a list of IPS found in ACL
    :return:
    '''
    acl = cli("show ip access-list %s" % ACLNAME).split('\n')
    p = re.compile('[\d]+\.[\d\.]+')
    return p.findall(''.join(acl))


# [ConfigResult(success=True, command='', line=1, output='', notes=None),
# ConfigResult(success=True, command='ip access-list extended canary_ip_in', line=2, output='', notes=None),
# ConfigResult(success=True, command='no deny ip any any', line=3, output='', notes=None),
# ConfigResult(success=True, command='permit ip any host 1.1.1.1', line=4, output='', notes=None),
# ConfigResult(success=True, command='deny ip any any', line=5, output='', notes=None)]

def add_acl(ip):
    '''
    add an entry to the ACL.  look at success or not of the commands
    :param ip:
    :return:
    '''
    UPDATE_ACL_COMMANDS = """
ip access-list extended %s
no deny ip any any
remark %s
permit ip any host %s
deny ip any any
"""
    localtime = time.asctime(time.localtime(time.time()))
    remark = "Added %s @%s" % (ip, localtime)
    responses = configure(UPDATE_ACL_COMMANDS % (ACLNAME, remark, ip))
    success = reduce(lambda x, y: x and y, [r.success for r in responses])
    status = "Success" if success else "Fail"
    log("adding IP: %s to ACL: status: %s" % (ip, status), 5)


def reschedule(seconds, *args):
    '''
    set an EEM countdown timer to run the script again
    :param seconds:
    :param *args: the initial args that were passed to the script
    :return:
    '''
    UPDATE_SCRIPT_FIRING_COMMANDS = """
event manager applet DNS_update
    event timer countdown time %s
    action 1.0 cli command "enable"
    action 1.1 cli command "guestshell run python %s
"""

    ### FIXME.. argv[0] will need to be fixedup if there is a bootflash: in it.

    responses = configure(UPDATE_SCRIPT_FIRING_COMMANDS % (seconds, " ".join(args)))
    success = reduce(lambda x, y: x and y, [r.success for r in responses])
    status = "Success" if success else "Fail"
    log("reschedule in : %s seconds: status: %s" % (str(seconds), status), 5)


def main(argv):
    '''
    takes a list of DNS names, resolves them and gets all of the IP addresses as well as TTL
    TTL is used to calculate the next run time.  =min(ttl) +1
    :param argv: domain names to lookup
    :return:
    '''
    acl = get_acl_ip()
    minttl = 30
    for arg in argv[1:]:
        ttl, ips = dns_lookup(arg)
        missing_ip = list(set(ips) - set(acl))

        for ip in missing_ip:
            add_acl(ip)

        if ttl < minttl:
            minttl = ttl

    # update with all the args including argv[0] which is how the script was called.
    reschedule(minttl, *argv)


if __name__ == "__main__":
    if len(sys.argv) == 1:
        print "Usage: %s domain-name ..."
        sys.exit(1)

    main(sys.argv)
