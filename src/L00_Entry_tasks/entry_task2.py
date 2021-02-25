import math
X = input().split(" ")
P = input().split(" ")
M, M2 = 0, 0
for x, p in zip(X, P):
    M += float(x)*float(p)
    M2 += float(x)*float(x)*float(p)
print("{:.{}f} ".format(M, 2) + "{:.{}f} ".format(math.sqrt(M2 - M*M), 2) + "{:.{}f}".format(M2 - M*M, 2))
