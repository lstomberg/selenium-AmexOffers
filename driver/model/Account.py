from .Equatable import equatable


class Account(equatable):
    FILE = "driver/model/accounts.jl"

    def __init__(self, site, username, password):
        self.username = username
        self.password = password
        self.site = site

    def uniquekey(self):
        return (self.site, self.username)

    def __lt__(self, other):
        return self.username < other.username

    def __str__(self):
        return "<{}: {}, username={}>".format(self.__class__.__name__, self.site, self.username)
