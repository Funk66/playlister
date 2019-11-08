class A(list):
    columns = ['a', 'b']

    def __init__(self, a, b = None):
        super().__init__([a, b])

    def __getattr__(self, key):
        try:
            return self[self.columns.index(key)]
        except ValueError:
            raise AttributeError(f'{key} is not an attribute of A')

    def __setattr__(self, key, value):
        try:
            self[self.columns.index(key)] = value
        except ValueError:
            raise AttributeError(f'{key} is not an attribute of A')

    # def __iter__(self):
        # for i in [self.a, self.b]:
            # yield i


a = A(1)
print(a)
a.b = 2
print(a)
print(a.b)
