class A:
    def __init__(self):
        self.a = 0


a = []
for i in range(3):
    a.append(A())

b = a[:]
for i in range(3):
    b[i].a += 2

print(",,,")