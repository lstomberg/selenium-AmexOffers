#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from util import Serialization, clear_screen
from driver.model import Amex


def main():
    print("\nIgnoring offers:")
    ignored = Serialization.load(Amex.Offer.IGNOREDFILE)
    printlist = [repr(x) for x in ignored]
    Serialization.print_list(printlist)


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
if __name__ == "__main__":
    clear_screen("AmexOffers_ignore_print.py")
    try:
        main()
    except:
        quit()
    print("\nDone\n")

# eof
