#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from util import clear_screen
from driver.AmexOffersDriver import AmexOffersDriver
from util import Serialization
from driver.model import Account
from driver.model import Amex


def __offers_FILE():
    return Amex.Offer.FILE


def get_offers():
    if 'OFFERS' not in globals():
        global OFFERS
        OFFERS = set(Serialization.load(__offers_FILE()))
    return OFFERS


# set discovered time to earlier time if offer was previously discovered
def update_discovered_date(offer):
    for x in get_offers():
        if x == offer:
            offer.discovered_date = x.discovered_date
            return


def main():
    accounts = Serialization.load(Account.FILE)
    accounts = [x for x in accounts if x.site == "AmericanExpress"]
    if len(accounts) == 0:
        message = f"No accounts defined in {Account.FILE} with site == \"AmericanExpress\".  Use _EditDatabase.py to add an account."
        raise ValueError(message)

    offers = []
    cards = []
    lookup_table = []
    # loop over accounts
    for account in accounts:
        driver = AmexOffersDriver(account)
        driver.login()
        account_cards = driver.list_cards()
        # store cards
        cards += account_cards
        # loop ofer cards
        for index, card in enumerate(account_cards):
            # one time I got 0 offers, which isn't possible, so I added this loop to try to fix it
            for x in range(2):
                # select card
                driver.select_card_at_index(index)
                # get offers
                card_offers = driver.list_offers()
                # one time I got 0 offers, which isn't possible, so I added this loop to try to fix it
                if len(card_offers) != 0:
                    break
            # update discover date from offer history
            for x in card_offers:
                update_discovered_date(x)
            # append to list of offers
            # should be a set but doesnt hurt to keep as list for ease of coding
            offers += card_offers
            # add to card_offer table
            lookup_table += [Amex.CardOffer(card, x) for x in card_offers]
        driver.quit()

    # store all offers only at end
    # otherwise we lose discovered time on offers we hadn't encountered yet if we hit an exception
    store(offers, cards, lookup_table)

#
# store to disk
#


def store(offers, cards, lookup_table):
    offers = list(set(offers))
    Serialization.save(offers, Amex.Offer.FILE)
    Serialization.save(cards, Amex.Card.FILE)
    Serialization.save(lookup_table, Amex.CardOffer.FILE)


#
# Main
#

def print_start():
    import os
    import arrow
    clear_screen(os.path.basename(__file__))
    print(arrow.now().format("MMM DD @ HH:MM A"))


if __name__ == "__main__":
    print_start()
    main()
    print("\nDone\n")

# eof
