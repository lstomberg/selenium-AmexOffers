#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from util import Serialization, clear_screen
from driver.model import Amex
import itertools
import sys


def visible_offers():
    offers = Serialization.load(Amex.Offer.FILE)
    if "-v" in sys.argv:
        return offers
    ignored = Serialization.load(Amex.Offer.IGNOREDFILE)
    visible = [x for x in offers if x not in ignored]
    return visible


def main():
    if "-v" in sys.argv:
        verboseprint()
        return
    defaultprint()


def verboseprint():
    offers = Serialization.load(Amex.Offer.FILE)
    printlist = sorted([repr(x) for x in offers], key=str)
    Serialization.print_list(printlist)


def defaultprint():
    lookup_table = Serialization.load(Amex.CardOffer.FILE)
    cards = Serialization.load(Amex.Card.FILE)
    offers = sorted(visible_offers(), key=lambda x: x.discovered_date)

    groups = itertools.groupby(offers, key=lambda x: x.discovered_date)
    index = 0
    for date, elmts in groups:
        index += 1
        prefix = f"{index} "
        print("\n"*15)
        print("-----------------------")
        print(f" Discovered: {date}")
        print(f"{prefix}")

        for x in sorted(elmts, key=lambda x: x.site.lower()):
            print_offer(prefix, x, lookup_table, cards)


def print_offer(prefix, offer, lookup_table, cards):
    exp = (offer.expires_string or "").lower()
    if exp.startswith("expires "):
        exp = exp[8:]

    print(f"{prefix}\n{prefix} {offer.site}\n{prefix}  {offer.description}\n{prefix}  Expires {exp}")

    card_uniquekeys_with_offer = [
        x.card for x in lookup_table if x.offer == offer]
    cards_with_offer = [c for c in cards if c in card_uniquekeys_with_offer]

    def format_card(c): return f"{prefix}    {c}"
    card_strings = [format_card(c) for c in cards_with_offer]
    print(f"\n".join(card_strings))


    #
    # Main
    #
if __name__ == "__main__":
    clear_screen("AmexOffers.py")
    main()
    print("\nDone\n")
