operand = input()
st1 = input().split(' ')
st2 = input().split(' ')
x1, y1, z1, x2, y2, z2 = float(st1[0]), float(st1[1]), float(st1[2]), float(st2[0]), float(st2[1]), float(st2[2])
if operand == "+":
    res = (x1+x2, y1+y2, z1+z2)
elif operand == "-":
    res = (x1-x2, y1-y2, z1-z2)
elif operand == "@":
    res = (x1*x2, y1*y2, z1*z2)
else:
    res = (float(y1*z2-y2*z1), float(-x1*z2+x2*z1), float(x1*y2-x2*y1))
print("%.2f %.2f %.2f" % res)
