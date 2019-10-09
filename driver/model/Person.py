from util import Serialization


class Person(object):
    FILE = "driver/model/people.jl"

    def __init__(self, first_name, last_name, phone, home_name):
        self.first_name = first_name
        self.last_name = last_name
        self.phone = phone
        self.home_name = home_name

    def __str__(self):
        return "<{}: {} {}>".format(self.__class__.__name__, self.first_name, self.last_name)

    @classmethod
    def with_name(cls, fname, lname):
        people = Serialization.load(cls.FILE)
        for p in people:
            if p.first_name.lower() == fname.lower() and p.last_name.lower() == lname.lower():
                return p
        return None
