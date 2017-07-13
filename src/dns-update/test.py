import sys
import os
#change path to allow import from parent directory
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir))
from utils.spark_utils import getRoomId, postMessage
print "hello"