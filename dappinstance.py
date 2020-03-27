import logging

class DAppInstance:
    def __init__(self, dapp, args, db):
        self.args = args
        self.context = {}
        self.dapp = dapp
        self.db = db
    
    def init(self):
        self.dapp.init(self.args, self.context, self.db)
        return self

    def run(self, receipts):
        logging.getLogger('DAppInstance.run').debug('Received %d receipts', len(receipts))
        return (self.dapp.name(), self.dapp.run(self.args, self.context, self.db, receipts))
    