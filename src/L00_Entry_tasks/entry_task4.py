from decimal import Decimal
a, b = input().split(" ")
d = Decimal(a) + Decimal(b)
print("{:.{}f}".format(d, 20))
