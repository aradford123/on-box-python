#!/usr/bin/env python
import sys
import time
from dns import reversename, resolver
from dns.resolver import NXDOMAIN
from dns.resolver import NoAnswer
from dns.resolver import NoNameservers
from dns.exception import Timeout
from cli import cli
from cli import configure


'''
This code is executed as a daemon and takes no parameters.
It periodically fetch all object-groups starting with FQDN-*
and sync it up with the corresponding IPs, respecting records TTL

IOS-XE does not allow creation of empty object-groups, so addition
of new FQDN based objects can be done as the following:

  object-group network FQDN-<host.domain.com>
    host 127.0.0.1

After the first iteration 127.0.0.1 will be replaced by the resolved IP(s)
'''



DEBUG = False


def log(message, severity):
    cli('send log %d "%s"' % (severity, message))


def dns_lookup(name):
    if DEBUG:
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


def object_group_lookup(fqdn):
    ips = cli("show object-group name FQDN-%s | i host" % (fqdn)).split('\n')
    return [x.split("host ")[1] for x in ips if x]


def object_group_configure(fqdn,ip,template,action):
    localtime = time.asctime(time.localtime(time.time()))
    remark = "Added %s @%s" % (ip,localtime)
    responses = configure(template % (fqdn,ip))
    success = reduce (lambda x, y : x and y, [r.success for r in responses])
    status = "Success" if success else "Fail"
    log("RESOLVER(%s): %s IP: %s - status: %s" % (fqdn, action, ip, status), 5)


def main(argv):
    MIN_TTL = 30

    OBJECT_GROUP_ADD = """object-group network FQDN-%s\n host %s\n"""
    OBJECT_GROUP_DEL = """object-group network FQDN-%s\n no host %s\n"""

    while True:

        # Fetch current FQDN object groups
        object_groups = cli("show object-group | i FQDN-").split('\n')
        fqdns = [x.split("FQDN-")[1] for x in object_groups if x]

        for fqdn in fqdns:
            # DNS Lookup
            ttl, resolved_ips = dns_lookup(fqdn)

            # Polling interval should consider the minimum original TTL
            if ttl < MIN_TTL:
                MIN_TTL = ttl + 1

            # Compare resolved IPs vs. object group IPs
            object_group_ips  = object_group_lookup(fqdn)
            include           = list(set(resolved_ips) - set(object_group_ips))
            exclude           = list(set(object_group_ips) - set(resolved_ips))

            # Synchronize config based on DNS Lookup IPs
            for ip in include:
                object_group_configure(fqdn,ip,OBJECT_GROUP_ADD,"adding")

            for ip in exclude:
                object_group_configure(fqdn,ip,OBJECT_GROUP_DEL,"removing")

        # Sleep for minimum record TTL -- NEED FIX: answers.rrset.ttl = time for resolver cache to expire, not original TTL
        print("Sleeping %s" % (MIN_TTL))
        time.sleep(MIN_TTL)


if __name__ == "__main__":
    main(sys.argv[1:])
