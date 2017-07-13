#!/usr/bin/env python
import sys
import time
from dns import reversename, resolver
from dns.resolver import NXDOMAIN
from dns.resolver import NoAnswer
from dns.resolver import NoNameservers
from dns.exception import Timeout

ACLNAME = "canary_ip_in"

# this is the command string to add an ACE to the ACL
UPDATE_ACL_COMMANDS = """
ip access-list extended canary_ip_in
no deny ip any any
remark %s
permit ip any host %s
deny ip any any
"""

UPDATE_SCRIPT_FIRING_COMMANDS = """
event manager applet DNS_update
 event timer countdown time %s
 action 1.0 cli command "enable"
 action 1.1 cli command "guestshell run python bootflash:flash/gs_script/src/dns-update %s
"""

from cli import cli
from cli import configure

# yes this is a global... should change this
ACL = cli("show ip access-list %s" % ACLNAME).split('\n')

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
        # we might need ttl
        print "TTL", answers.rrset.ttl
        return answers.rrset.ttl, [answer.address for answer in answers]

    except NXDOMAIN:
        pass

    except NoAnswer:
        pass
    except NoNameservers:
        pass
    except Timeout:
        pass

#[ConfigResult(success=True, command='', line=1, output='', notes=None),
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
    localtime = time.asctime(time.localtime(time.time()))
    remark = "Added %s @%s" % (ip,localtime)
    responses = configure(UPDATE_ACL_COMMANDS % (remark,ip))
    success = reduce (lambda x, y : x and y, [r.success for r in responses])
    status = "Success" if success else "Fail"
    log("adding IP: %s to ACL: status: %s" % (ip, status), 5)

def lookup(ip, acl=ACL):
    '''
    looks up the ip address in the ACL.  ACL is global in this case
    :param ip:
    :param acl:
    :return:
    '''
    for ace in acl:
        if ip in ace:
            return True
    return False

def check_acl(ips):
    '''
    checks to see if the IP is in the ACL, otherwise adds it
    :param ips:
    :return:
    '''
    for ip in ips:
        if not lookup(ip):
            add_acl(ip)

def reschedule(seconds, *args):
    '''
    set an EEM countdown timer to run the script again
    :param seconds:
    :param *args: the initial args that were passed to the script
    :return:
    '''
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
    all_ips = []
    ttls = []
    for arg in argv:
        ttl, ips = dns_lookup(arg)
        all_ips.extend(ips)
        ttls.append(ttl)
    try:
        minttl = min(ttls)
    except ValueError:
        log("failed to get TTL", 7)
    print "All IPs", all_ips
    print "minTTL", min(ttls)
    print "ACL was", ACL
    check_acl(all_ips)
    reschedule(min(ttls), *argv)


if __name__ == "__main__":
    if len(sys.argv) == 1:
        print "Usage: %s domain-name ..."
    else:
        main(sys.argv[1:])