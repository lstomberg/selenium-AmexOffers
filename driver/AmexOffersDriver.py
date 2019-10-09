from . import WebDriver
from .model import Amex
import re
import time

#
# ==> change to subclass WebDriver.Base for debugging
#


class AmexOffersDriver(WebDriver.Base):

    @classmethod
    def configureChromeOptions(self, chrome_options):
        super().configureChromeOptions(chrome_options)
        chrome_options.add_argument('window-size=1400x1142')
    #
    # Initialize
    #

    def __init__(self, account, **kwargs):
        super().__init__(**dict(kwargs))
        self.account = account
        self.accounts_visible = False

    ######################
    # PRIMARY PUBLIC API #
    ######################

    LOGIN_URL = 'https://www.americanexpress.com/'
    INPUT_USERNAME = '//*[@id="login-user"]'
    INPUT_PASSWORD = '//*[@id="login-password"]'
    SUBMIT = '//*[@id="login-submit"]'

    # SHOW_ACCOUNTS_BUTTONS = '//button[contains(@class, "axp-account-switcher")]'
    SHOW_ACCOUNTS_BUTTONS = '//*[@class="card-stack"]/button'
    SHOW_ACCOUNTS_VIEWALL_BUTTON = '//a[contains(@title, "View All")]'

    # two <p> tags per card for 2 different layouts
    # ACCOUNT_NAME_IDS = '//*[@id="accounts"]//p[contains(@class, "heading-2") and @title != "Working Capital Terms"]'
    ACCOUNT_NAME_IDS = '//*[@id="accounts"]//p[contains(@class, "heading-2") and @title != "Working Capital Terms" and not(./following-sibling::p[contains(@class, "canceled")])]'

    # OFFERS_TAB_ELIGIBLE = '//*[@id="offers"]//a[@data-view-name="ELIGIBLE"]'
    # OFFERS_TAB_ENROLLED = '//*[@id="offers"]//a[contains(@href,"/offers/enrolled")]'
    # OFFERS = '//*[@id="offers"]//section[contains(@class, "offers-list")]//div[contains(@id,"offer-")]'
    # OFFERS_VIEWALL_BUTTON = '//*[@id="offers"]//a[text()="View All"]'

    OFFERS_TAB_ELIGIBLE = '//a[@data-view-name="ELIGIBLE"]'
    OFFERS_TAB_ENROLLED = '//a[@data-view-name="ENROLLED"]'
    # //a[contains(@class, "btn")]/span[text()="View All"]
    OFFERS_VIEWALL_BUTTON = '//*[@id="offers"]//a[.//text()="View All"]'

    OFFERS = '//section[contains(@class, "offers-list")]//div[contains(@id,"offer-")]'
    # elmt 0 - description, 1 - site
    OFFER_DESCRIPTION_SITE = './/*[contains(@class, "offer-info")]/*'
    OFFER_EXPIRES = './/*[contains(@class, "offer-expires")]/span'

    OFFERS_ADD_TO_CARDS = '//button[contains(@title,"Add to Card")]'

    #
    # Login
    #

    def login(self):
        print(f"Logging in {self.account.username}")
        return self.get_url(self.LOGIN_URL)\
            .get(self.INPUT_USERNAME).enter(self.account.username)\
            .get(self.INPUT_PASSWORD).enter(self.account.password)\
            .get(self.SUBMIT).click()

    #
    # ACCOUNT LIST
    #

    def _open_accounts_list(self):
        if self.accounts_visible:
            return self

        iter = 0
        # can take a few seconds for it to appear
        while not any(self.gets(self.SHOW_ACCOUNTS_BUTTONS, filter_invisible=True)):
            iter += 1
            time.sleep(1)
            assert (iter < 25)

        # Had an issue once where we were too fast and it caused offers to not appear
        # This is likely headless and not important to finish asap so lets add 4 second delay
        time.sleep(4)

        # there are two buttons (compact and full layouts) with only 1 visible at a time
        # we used to filter invisible but for some reason that would cause issues in headless for the 4th card account
        # so now we just ignore click exceptions but check that at least 1 button succeeded
        # self.gets(self.SHOW_ACCOUNTS_BUTTONS, filter_invisible=True)
        buttons = self.gets(self.SHOW_ACCOUNTS_BUTTONS)
        for elmt in buttons:
            try:
                # trying this because getting exception that single button found is unclickable
                self.execute_script(
                    "return arguments[0].scrollIntoView();", elmt)
                elmt.click()
                FLAG_ELEMENT_CLICKED = 1
            except Exception:
                # print(f"""LWS-TODO.  Why can this be not clickable?
                #     There are {len(buttons)} buttons possible.
                #     Here is the exception we are skipping
                #     -------------------------------------
                #     {ex}
                #     -------------------------------------""")
                pass

        if FLAG_ELEMENT_CLICKED != 1:
            raise Exception("""LWS-TODO.  Why was no button clickable?""")

        self.accounts_visible = True
        return self

    def _click_view_all_accounts(self):
        if getattr(self, 'clicked_view_all_accounts', None) is None:
            self._open_accounts_list()
            try:
                self.get(self.SHOW_ACCOUNTS_VIEWALL_BUTTON,
                         pause_on_except=False).click()
            except:
                print("Skipping Button.  Wont exist for accounts with 4 or fewer cards.")

        self.clicked_view_all_accounts = True
        return self

    def _get_accounts(self):
        return self._open_accounts_list()\
            ._click_view_all_accounts()\
            .gets(self.ACCOUNT_NAME_IDS, filter_invisible=True)

    def select_card_at_index(self, index):
        cards = self._get_accounts()
        # print(f"Index: {index}\nCards: {cards}")
        cards[index].click()
        self.accounts_visible = False
        return self

    # parse account info
    def _parse_account(self, elmt):
        name = elmt.get_attribute("title")
        identifier = re.sub(r'[^0-9\-]', '', elmt.text)
        return Amex.Card(name, identifier)

    def list_cards(self):
        cards = []
        for elmt in self._get_accounts():
            cards.append(self._parse_account(elmt))
        # print(f"Cards in list_cards: {cards}")
        return cards

    #
    # OFFERS
    #

    def _click_view_all_offers(self):
        try:
            if getattr(self, 'clicked_view_all_offers', None) is None:
                viewAllButton = self.get(
                    self.OFFERS_VIEWALL_BUTTON, wait=4, pause_on_except=False)
                viewAllButton.scroll_into_view().click()
            self.clicked_view_all_offers = True
        except Exception as ex:
            print(f"""Failed to click ViewAll button.
            --------------------
            {ex}
            --------------------
            """)

        return self

    def _get_offers(self):
        return self._click_view_all_offers()\
            .gets(self.OFFERS, filter_invisible=True)

    def add_offers_to_card(self):
        self._click_eligible_offers_tab() \
            .sleep(1.0)

        buttons = self.gets(self.OFFERS_ADD_TO_CARDS, filter_invisible=True)
        for button in buttons:
            try:
                button.click()
            except Exception as ex:
                print(ex)

        # 70 buttons sleeps for 7 seconds
        self.sleep(0.1 * len(buttons))\
            ._click_enrolled_offers_tab() \
            .sleep(1.0) \
            ._click_eligible_offers_tab()
        return self

    def _click_eligible_offers_tab(self):
        try:
            self.get(self.OFFERS_TAB_ELIGIBLE).scroll_into_view().click()
        except Exception:
            pass
        return self

    def _click_enrolled_offers_tab(self):
        try:
            self.get(self.OFFERS_TAB_ENROLLED).scroll_into_view().click()
        except Exception:
            pass
        return self

    # parse offer info
    def _parse_offer(self, elmt):
        try:
            elmts = elmt.find_elements_by_xpath(self.OFFER_DESCRIPTION_SITE)
            description = elmts[0].text
            site = elmts[1].text
            expires = None
            try:
                # Amex special offers dont have expire element
                expires = elmt.find_element_by_xpath(
                    self.OFFER_EXPIRES).text  # 1/31/2019 or #expires in X days #3/1/2019
            except:
                pass
            return Amex.Offer(site, description, expires)
        except Exception:
            pass
        return None

    def list_offers(self):
        offers = []
        # self.add_offers_to_card()

        self._click_eligible_offers_tab().sleep(0.5)
        # this has returned 0 sometimes due to async loading of offers
        # wait extra 5 seconds if necessary
        offer_elements = self._get_offers()
        if len(offer_elements) == 0:
            offer_elements = self.sleep(5)._get_offers()

        # loop over and append offers
        for elmt in self._get_offers():
            offer = self._parse_offer(elmt)
            if offer is not None:
                offers.append(offer)
        eligableCount = len(offers)

        self._click_enrolled_offers_tab().sleep(0.5)
        # this has returned 0 sometimes due to async loading of offers
        # wait extra 5 seconds if necessary
        offer_elements = self._get_offers()
        if len(offer_elements) == 0:
            offer_elements = self.sleep(5)._get_offers()

        # loop over and append offers
        for elmt in self._get_offers():
            offer = self._parse_offer(elmt)
            if offer is not None:
                offers.append(offer)

        print(
            f"{len(offers)} found: {eligableCount} eligable, {len(offers)-eligableCount} added")

        return offers
