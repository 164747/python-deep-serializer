Python Deep Serializer
======================


Package provides for 

 * Serializing nested Python objects. That is creating a nested dictionary from a nested Python object.

 * Deserializing nested Python objects, that is initializing nested Python objects with a nested dictionary.
 
 One use case is when you have a web api and users post nested json which you use to initialize (nested) Python objects.


**Example** 
```python
from pprint import pprint

import datetime
import typing

from deep_serializer import des
from deep_serializer.ser import ToDictEnabled


class Person(ToDictEnabled):

    @des.cast  # casting input
    def __init__(self, name: str, age: int):
        self.name = name
        self.age = age


class Car(ToDictEnabled):

    @des.cast  # casting input
    def __init__(self, model: str, owner: Person, color: str, registration_date: datetime.datetime,
                 passengers: typing.List[Person] = (), miles: typing.Dict[datetime.datetime, float] = None):
        self.miles = miles
        self.model = model
        self.owner = owner
        self.color = color
        self.registration_date = registration_date
        self.passengers = passengers
        self.__private_variable = 'secret'  # private attribute not serialized by todict

    @property
    def color_and_owner(self) -> str:  # property not serialized by todict
        return '%s-%s' % (self.color, self.owner.name)


if __name__ == '__main__':
    car_dict = {
        'color': 'blue',
        'model': 'Volvo',
        'owner': {'age': '22', 'name': 'Bob'},
        'passengers': [{'age': 20, 'name': 'Alice'}, {'age': 19, 'name': 'Joe'}],
        'registration_date': '2015-01-01 12:00.00',
        'miles': {'2015-01-01 12:00.00': 0, '2016-01-01 12:00.00': '1000'}
    }

    print('\n\nInput')
    pprint(car_dict)

    car = Car(**car_dict)
    print('\n\nCar object:\n%s' % car)

    print('\n\nCar as dict')
    pprint(car.todict(), indent=4)
```

**Note that**
 * The `ToDictEnabled` adds the `todict` method which enables deep serialization.
 * The `@des.init` property tries to cast input variables according to their type hints before actual init is run.
 * The `@color_and_owner` property is not serialized.
 * The `__private_variable` attribute is not serialized.
 
 

Running main yields
```
Input
{'color': 'blue',
 'miles': {'2015-01-01 12:00.00': 0, '2016-01-01 12:00.00': '1000'},
 'model': 'Volvo',
 'owner': {'age': '22', 'name': 'Bob'},
 'passengers': [{'age': 20, 'name': 'Alice'}, {'age': 19, 'name': 'Joe'}],
 'registration_date': '2015-01-01 12:00.00'}


Car object:
<__main__.Car object at 0x7f4972796cf8>


Car as dict
{   'color': 'blue',
    'miles': {   datetime.datetime(2015, 1, 1, 12, 0): 0.0,
                 datetime.datetime(2016, 1, 1, 12, 0): 1000.0},
    'model': 'Volvo',
    'owner': {'age': 22, 'name': 'Bob'},
    'passengers': [{'age': 20, 'name': 'Alice'}, {'age': 19, 'name': 'Joe'}],
    'registration_date': datetime.datetime(2015, 1, 1, 12, 0)}
```


**Caveats**
- Code is virtually untested, except on a few minor private projects. 

- Casting is far from complete. For example, the `typing.Tuple[]` type hinting does not work, and those input variables will not be casted.

- Only works with Python3, only tested with Python3.6 and Python3.7.

- `todict` method will not serialize attributes starting with `__` and not serialize properties.
