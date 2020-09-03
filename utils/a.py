#!/bin/python3

import math
import os
import random
import re
import sys



#
# Complete the 'compareStrings' function below.
#
# The function is expected to return a STRING.
# The function accepts following parameters:
#  1. STRING firstString
#  2. STRING secondString
#  3. STRING thirdString
#

def compareStrings(firstString, secondString, thirdString):
    # Write your code here
    listStrings = list([firstString, secondString, thirdString].sort())
    return "".join(listStrings)

if __name__ == '__main__':
    s1 = "a"
    s2 = "bc"
    s3 = "abc"
