
#
# Equatability (just override uniquekey)
#


class equatable():
    # taken from https://stackoverflow.com/a/2909119/5744185
    def uniquekey(self):
        return ()

    def __eq__(self, other):
        assert(isinstance(other, type(self)))
        return self.uniquekey() == other.uniquekey()

    # note, if two elements are equal (__eq__) then their hashes MUST also be equal
    def __hash__(self):
        return hash(self.uniquekey())
