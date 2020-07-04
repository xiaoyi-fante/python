class Typed:
    def __init__(self, type):
        self.type = type

    def __get__(self, instance, owner):
        pass

    def __set__(self, instance, value):
        print('T.set', self, instance, value)
        if not isinstance(value, self.type):
            raise ValueError(value)



import inspect
class typeassert:
    def __init__(self, cls):
        self.cls = cls
        params = inspect.signature(self.cls).parameters
        print(params)
        for name,param in params.items():
            print(name, param.annotation)
            if param.annotation != param.empty:
                setattr(self.cls, name, Typed(param.annotation))
        print(self.cls.__dict__)

    def __call__(self, name, age):
        p = self.cls(name, age)
        return p


@typeassert
class Person:
    # name = Typed('name', str)
    # age = Typed('age', int)

    def __init__(self, name:str, age:int):
        self.name = name
        self.age = age


#p = Person('tom', '12')
p1 = Person('tom', 12)
print(id(p1))

p2 = Person('tom', 20)
print(id(p2))