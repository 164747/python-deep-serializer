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
