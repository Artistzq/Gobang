class A:
    def __init__(self, a="a"):
        print(a)


class B:
    def __init__(self, b="b"):
        print(b)


class C(A, B):
    def __init__(self, a, b):
        super(C, self).__init__(a)
        super(C, self).__init__(b)

if __name__ == '__main__':
    C(1, 2)