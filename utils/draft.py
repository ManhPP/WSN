def test(c):
    for i in range(len(c)):
        c[i] += 2
    return c


a = [1, 2, 3]

b = test(a[:])

print(a)
print(b)
