#!/usr/bin/env python
from __future__ import print_function
import jtextfsm as textfsm
from cli import cli, configure
import re
import time
from argparse import ArgumentParser
import sys
import os
#change path to allow import from parent directory
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir))
from utils.spark_utils import getRoomId, postMessage



def is_idle_value(string):
    # can be 'never' or 00:00:00 or 7d23h etc
    match = re.match(r'([n]+)d.*|(never)', string)
    if match:
        if int(match.group(1) >= 7) or string == "never":
            return True
    else:
        return False


def is_idle(input_time, output_time):
    return is_idle_value(input_time) and is_idle_value(output_time)

def log(message, severity):
    print(message)
    cli('send log %d "%s"' % (severity, message))

def spark(message):
    sparktoken = os.environ.get("SPARKTOKEN")
    if sparktoken is not None:
        roomId = getRoomId("PCI", sparktoken)
        postMessage('\n```\n' + message +'\n```', roomId, sparktoken)

def apply_commands(commands):
    response = configure(commands)
    for r in response:
        log(r.__str__(), 5)
    if len(response) > 1:
        spark('\n'.join([r.__str__() for r in response]))

def process(re_table, apply_change):
    exec_commands = []
    re_table.Reset()

    output = cli("show int | inc Last in|line pro")
    print (output)
    localtime = time.asctime(time.localtime(time.time()))
    description = "description PCIShutdown: %s" % localtime
    fsm_results = re_table.ParseText(output)
    for interface in fsm_results:
        # skip non Ethernet
        if is_idle(interface[2], interface[3]) and ("Ethernet" in interface[0]):
            if interface[1] != "administratively":
                if apply_change:
                    exec_commands.extend(['interface ' + interface[0], description, 'shutdown'])
                else:
                    print("(testmode) would have SHUT %s (%s,%s)" % (interface[0], interface[2], interface[3]))

    print('Commands to run:')
    print(exec_commands)
    apply_commands(exec_commands)


if __name__ == "__main__":
    parser = ArgumentParser(description='Select PCI-TOOL args:  reads a list of devices and credentials from STDIN')
    parser.add_argument('-a', '--apply', action='store_true',
                   help="Apply commands to device.  no longer run in testing mode.")

    args = parser.parse_args()
    template = open("/flash/gs_script/src/pci-tool/show_int.textfsm")
    re_table = textfsm.TextFSM(template)
    process(re_table, args.apply)