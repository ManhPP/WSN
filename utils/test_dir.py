import os
from pathlib import Path

print(Path(__file__).parent.parent)
print(__file__)
print(__name__)

a = [1,2,3]
for i in range(len(a)-1):
    for j in range(i+1,len(a)):
        print(a[i],a[j])
        print(a[j],a[i])