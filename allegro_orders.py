from allegro_api import AllegroAPI
from database import Database

class AllegroOrders:
    def __init__(self, api: AllegroAPI, db: Database):
        self.api = api
        self.db = db

    def sync_orders(self):
        #GET /order/checkout-forms?lineItems.boughtAt.gte=2025-10-01T00:00:00Z
        offset = 0
        total = 0

        while True:
            orders = self.api.fetch_orders(limit=50, offset=offset)
            if not orders:
                break
            for order in orders:
                self.db.save_order(order)

            total += len(orders)
            offset += 50