import logging
from typing import cast

from geniusweb.actions.Accept import Accept
from geniusweb.actions.Action import Action
from geniusweb.actions.Offer import Offer
from geniusweb.bidspace.AllBidsList import AllBidsList
from geniusweb.inform.ActionDone import ActionDone
from geniusweb.inform.Finished import Finished
from geniusweb.inform.Inform import Inform
from geniusweb.inform.Settings import Settings
from geniusweb.inform.YourTurn import YourTurn
from geniusweb.issuevalue.Bid import Bid
from geniusweb.party.Capabilities import Capabilities
from geniusweb.party.DefaultParty import DefaultParty
from geniusweb.profileconnection.ProfileConnectionFactory import (
    ProfileConnectionFactory,
)
from geniusweb.progress.ProgressRounds import ProgressRounds


# Agent Gosho e div selqnin i pravi nqkvi shano oferti koito ne rabotqt
# osven ako drugiq agent ne e po prost selqnin ot Gosho

class AgentGosho(DefaultParty):
    """
    Template agent that offers random bids until a bid with sufficient utility is offered.
    """

    def __init__(self):
        super().__init__()
        self.getReporter().log(logging.INFO, "party is initialized")
        self._profile = None
        self._last_received_bid: Bid = None
        self.latest_bid: Bid = None
        self.all_bids = []
        self.opponent_preferences = []
        self.opponent_value_count = {}
        self.all_good_bids = []

    def notifyChange(self, info: Inform):
        """This is the entry point of all interaction with your agent after is has been initialised.

        Args:
            info (Inform): Contains either a request for action or information.
        """

        # a Settings message is the first message that will be send to your
        # agent containing all the information about the negotiation session.
        if isinstance(info, Settings):
            self._settings: Settings = cast(Settings, info)
            self._me = self._settings.getID()

            # progress towards the deadline has to be tracked manually through the use of the Progress object
            self._progress: ProgressRounds = self._settings.getProgress()

            # the profile contains the preferences of the agent over the domain
            self._profile = ProfileConnectionFactory.create(
                info.getProfile().getURI(), self.getReporter()
            )
        # ActionDone is an action send by an opponent (an offer or an accept)
        elif isinstance(info, ActionDone):
            action: Action = cast(ActionDone, info).getAction()

            # if it is an offer, set the last received bid
            if isinstance(action, Offer):
                self._last_received_bid = cast(Offer, action).getBid()
        # YourTurn notifies you that it is your turn to act
        elif isinstance(info, YourTurn):
            # execute a turn
            self._myTurn()

            # log that we advanced a turn
            self._progress = self._progress.advance()

        # Finished will be send if the negotiation has ended (through agreement or deadline)
        elif isinstance(info, Finished):
            # terminate the agent MUST BE CALLED
            self.terminate()
        else:
            self.getReporter().log(
                logging.WARNING, "Ignoring unknown info " + str(info)
            )

    # lets the geniusweb system know what settings this agent can handle
    # leave it as it is for this course
    def getCapabilities(self) -> Capabilities:
        return Capabilities(
            set(["SAOP"]),
            set(["geniusweb.profile.utilityspace.LinearAdditive"]),
        )

    # terminates the agent and its connections
    # leave it as it is for this course
    def terminate(self):
        self.getReporter().log(logging.INFO, "party is terminating:")
        super().terminate()
        if self._profile is not None:
            self._profile.close()
            self._profile = None

    #######################################################################################
    ########## THE METHODS BELOW THIS COMMENT ARE OF MAIN INTEREST TO THE COURSE ##########
    #######################################################################################

    # give a description of your agent
    def getDescription(self) -> str:
        return "Template agent for Collaborative AI course"

    def update_opponent_counts(self):
        lrb = self._last_received_bid
        domain = self._profile.getProfile().getDomain()
        # for issue in lrb.getIssues():
        #     self.opponent_value_count[issue][lrb.getValue(issue)] += 1

    # execute a turn
    def _myTurn(self):
        profile = self._profile.getProfile()

        # Initial setup
        if self._progress.get(0) == 0:
            issues = profile.getDomain().getIssues()
            for issue in issues:
                self.opponent_value_count[issue] = {}
                for value in profile.getDomain().getValues(issue):
                    self.opponent_value_count[issue][value] = 0

        if self._last_received_bid is not None:
            self.update_opponent_counts()

        print(self.is_opponent_repeating_bids())

        if self._progress.get(0) == 0.5:
            print('halfway there', self.opponent_value_count)
        # check if the last received offer if the opponent is good enough
        if self._isGood(self._last_received_bid):
            # if so, accept the offer
            action = Accept(self._me, self._last_received_bid)
        else:
            # if not, find a bid to propose as counter offer
            if self._last_received_bid is not None:
                self.all_bids.append((self._last_received_bid, profile.getUtility(self._last_received_bid)))

            bid = self._findBid()
            action = Offer(self._me, bid)
            self.latest_bid = bid
            if self._last_received_bid is not None:
                self.all_bids.append((self._last_received_bid, profile.getUtility(self._last_received_bid)))

        # send the action
        self.getConnection().send(action)

    # method that checks if we would agree with an offer
    def _isGood(self, bid: Bid) -> bool:
        if bid is None:
            return False

        if self.latest_bid is None:
            self.latest_bid = self.get_highest_bid()

        profile = self._profile.getProfile()
        progress = self._progress.get(0)

        if profile.getUtility(bid) > 0.9:
            return True

        if progress > 0.6:
            if profile.getUtility(bid) > 0.95 - 0.3 * progress:
                return True
        elif self._last_received_bid is not None and (0.8 - float(profile.getUtility(self._last_received_bid))*0.1 <= profile.getUtility(bid) or profile.getUtility(bid) >= 0.7):
                return True
        return False

    def find_all_good_bids(self):
        domain = self._profile.getProfile().getDomain()
        all_bids = AllBidsList(domain)

        for bid in all_bids:
            if self._isGood(bid):
                self.all_good_bids.append(bid)

    def _findBid(self) -> Bid:
        progress = self._progress.get(0)
        opponent_desired_bid = self.get_opponent_info()

        # All utility values
        utilities = self._profile.getProfile().getUtilities()

        not_important_issues, middle_issues = self.not_important_issues()
        # print(not_important_issues, "Not important issues")
        # print(middle_issues, "Middle issues")

        if self._last_received_bid is not None:

            if len(self.opponent_preferences) == 0:
                self.get_opponent_preference()

            # Values for issues
            opponent_issues = self._last_received_bid.getIssueValues()
            last_values = self.latest_bid.getIssueValues()
            bid_issues = last_values

            for issue in last_values:
                # get the value for issue
                # value = opponent_issues.get(issue)
                # float(utilities.get(issue).getUtility(opponent_issues.get(issue))) < 0.5:

                if issue in not_important_issues and opponent_desired_bid is not None:
                    bid_issues[issue] = opponent_desired_bid[issue]
                else:
                    suggested_val = (1 - progress / 3) * float(utilities.get(issue).getUtility(last_values.get(issue)))
                    prev_bid_issue_value = bid_issues[issue]
                    bid_issues[issue] = self.search_for_value(suggested_val, issue)
                    if not self._isGood(Bid(bid_issues)):
                        bid_issues[issue] = prev_bid_issue_value
            # print(bid_issues, "Bidding")
            bid = Bid(bid_issues)
            print("Bid utility------------", self._profile.getProfile().getUtility(bid))
        # When we have not received a bid, offer highest preference
        else:
            self.latest_bid = self.get_highest_bid()
            bid = self.get_highest_bid()

        return bid

    def is_opponent_repeating_bids(self):
        if len(self.all_bids) >= 5:
            for i in range(1, 5):
                if self.all_bids[-i] != self.all_bids[-i - 1]:
                    return False
            return True
        return False

    def get_highest_bid(self):
        domain = self._profile.getProfile().getDomain()
        all_bids = AllBidsList(domain)

        bids_with_utility = []

        for bid in all_bids:
            bids_with_utility.append((bid, self._profile.getProfile().getUtility(bid)))

        bids_with_utility = sorted(bids_with_utility, key=lambda item: -item[1])
        return bids_with_utility[0][0]

    def search_for_value(self, suggeseted_value_utility, issue):
        max_val = 1
        desired_value = ""
        utilities = self._profile.getProfile().getUtilities()
        all_values_for_issue = self._profile.getProfile().getDomain().getValues(issue)

        for v in all_values_for_issue:
            value_utility = utilities.get(issue).getUtility(v)
            if suggeseted_value_utility <= value_utility and value_utility <= max_val:
                desired_value = v
                max_val = value_utility
        return desired_value

    def get_opponent_preference(self):
        first_bid = self.all_bids[0][0]

        for issue in first_bid.getIssues():
            self.opponent_preferences.append((issue, first_bid.getValue(issue)))

    def get_opponent_info(self):
        prev_bids = self.all_bids
        if len(prev_bids) < 2:
            return None

        # prev_bids.sort(key=lambda x: x[1])
        issues = self._last_received_bid.getIssues()

        demanded_best_offer = {}
        for issue in issues:
            issue_value_opponent = {}
            for i in range(len(prev_bids)):
                bid = prev_bids[i][0]
                val = bid.getValue(issue)
                if val in issue_value_opponent:
                    issue_value_opponent[val] = issue_value_opponent[val] + 1
                else:
                    issue_value_opponent[val] = 1

            sorted_dict = dict(sorted(issue_value_opponent.items(), key=lambda item: item[1]))
            opponent_val = list(sorted_dict.keys())[-1]
            demanded_best_offer[issue] = opponent_val

        return demanded_best_offer

    def not_important_issues(self):
        domain = self._profile.getProfile().getDomain()
        issues = domain.getIssues()
        weights = []
        not_important_issues = []
        middle_issues = []

        for issue in issues:
            # Weight by issue
            weights.append(self._profile.getProfile().getWeight(issue))

        for issue in issues:
            w = self._profile.getProfile().getWeight(issue)
            if w < 0.15 * float(max(weights)):
                not_important_issues.append(issue)
            elif w < 0.5 * float(max(weights)):
                middle_issues.append(issue)

        return not_important_issues, middle_issues
