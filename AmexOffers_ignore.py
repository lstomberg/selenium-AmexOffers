#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from util import Serialization, clear_screen, query_yes_no
from driver.model import Amex


def main():
    keep_running = True
    while keep_running is True:
        print("\nPick an offer to ignore")
        offers = Serialization.load(Amex.Offer.FILE)
        ignored = Serialization.load(Amex.Offer.IGNOREDFILE)
        visible = [x for x in offers if x not in ignored]
        printlist = [repr(x) for x in visible]
        _, index = Serialization.pick_from_list(printlist, sort=True)
        item = visible[index]

        if query_yes_no("\nAdd to ignore list?"):
            ignored.append(item)
            Serialization.save(ignored, Amex.Offer.IGNOREDFILE)
        print("Added\n")


#
# Main
#
if __name__ == "__main__":
    clear_screen("AmexOffers_ignore.py")
    try:
        main()
    except:
        quit()
    print("\nDone\n")

# eof
