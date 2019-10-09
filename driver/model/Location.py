
class Location(object):
    FILE = "driver/model/locations.jl"

    def __init__(self, name, to, line1, line2, city, state, state_abvr, zip):
        self.name = name
        self.to = to
        self.line1 = line1
        self.line2 = line2
        self.city = city
        self.state = state
        self.state_abvr = state_abvr
        self.zip = zip

    def __str__(self):
        return "<{}: {} {}>".format(self.__class__.__name__, self.to, self.line1)
