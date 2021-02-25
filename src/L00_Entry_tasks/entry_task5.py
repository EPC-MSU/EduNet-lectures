def determinant(matrix, mul):
    width = len(matrix)
    if width == 1:
        return mul * matrix[0][0]
    else:
        sign = -1
        sum = 0
        for i in range(width):
            m = []
            for j in range(1, width):
                buff = []
                for k in range(width):
                    if k != i:
                        buff.append(matrix[j][k])
                m.append(buff)
            sign *= -1
            sum += mul * determinant(m, sign * matrix[0][i])
        return sum

if __name__ == '__main__': 
    X = []
    dim1 = input().split(' ')
    n0, m0 = int(dim1[0]), int(dim1[1])
    for m in range(int(m0)):
        n = input().split(" ")
        n = [int(n[i]) for i in range(len(n))]
        X.append(n)

    Y = []
    dim2 = input().split(' ')
    n1, m1 = int(dim2[0]), int(dim2[1])
    for m in range(int(m1)):
        n = input().split(" ")
        n = [int(n[i]) for i in range(len(n))]
        Y.append(n)

    matrix = [[sum(a*b for a,b in zip(X_row,Y_col)) for Y_col in zip(*Y)] for X_row in X]
    for i in range(len(matrix)):
        for j in range(len(matrix[0])):
            matrix[i][j] = int(matrix[i][j])

    print(determinant(matrix, 1))