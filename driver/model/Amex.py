from datetime import date
from .Equatable import equatable

# Offer


class Offer(equatable):
    FILE = "driver/model/amex-offers.jl"
    IGNOREDFILE = "driver/model/amex-offers-ignored.jl"

    DISCOVERED_DATE = date.today()

    def __init__(self, site, description, expires_string):
        self.site = site
        self.description = description
        self.expires_string = expires_string
        self.discovered_date = self.DISCOVERED_DATE

    def __str__(self):
        return "\n{}\n  {} - expires {}".format(self.description, self.site,  self.expires_string or "")

    def __repr__(self):
        return "Offer:  {:<40} | {:<50} | {}".format(self.site, self.description, self.expires_string or "")

    def uniquekey(self):
        return (self.site, self.description)

    @property
    def discovered_time(self):
        pass

    @discovered_time.setter
    def discovered_time(self, value):
        self.discovered_date = value.date()


# Card


class Card(equatable):
    FILE = "driver/model/amex-cards.jl"

    def __init__(self, name, card_identifier):
        if isinstance(card_identifier, int):
            card_identifier = str(card_identifier)
        self.card_identifier = card_identifier
        self.name = name

    def __repr__(self):
        return "{} ({})".format(self.name, self.card_identifier)

    def uniquekey(self):
        return (self.name, self.card_identifier)


class CardOffer(equatable):
    FILE = "driver/model/amex-cardoffers.jl"

    def __init__(self, card, offer):
        assert (isinstance(card, Card))
        assert (isinstance(offer, Offer))
        self.cardkey = card.uniquekey()
        self.offerkey = offer.uniquekey()

    def __repr__(self):
        return "<Card {} to Offer {}>".format(self.card, self.offer)

    def uniquekey(self):
        return (self.card, self.offer)

    @property
    def card(self):
        # unfortunate hard coding right now
        return Card(self.cardkey[0], self.cardkey[1])

    @property
    def offer(self):
        # unfortunate hard coding right now
        return Offer(self.offerkey[0], self.offerkey[1], "")
