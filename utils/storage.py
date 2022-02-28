from decimal import Decimal
from geniusweb.issuevalue.Bid import Bid

class Storage:
    def __init__(self):
        self.received_bids = []
        self.sent_bids
        self.weights: Dict[str, Decimal] = []

    def getIssuesAgentCanIgnore(self):
        # TODO return a list of issues that can be ignored by the agent
        pass

    def addReceivedBid(self, bid: Bid):
        self.received_bids.append(bid)

    def addSentBid(self, bid: Bid):
        self.sent_bids.append(bid)
