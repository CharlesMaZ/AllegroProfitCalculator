import requests
from config import Config
import json

class AllegroAPI:
    def __init__(self, config: Config):
        self.config = config
        self.base_url = config.data['api']['base_url']
        self.access_token = config.data['api']['access_token']

    def get_headers(self) -> dict:
        return {
            'Authorization': f'Bearer {self.access_token}',
            'Accept': 'application/vnd.allegro.public.v1+json',
            'Content-Type': 'application/json'
        }

    def fetch_orders(self, limit: int = 50, offset: int = 0) -> list[dict]:
        """
        Pobiera zamówienia z API Allegro
        https://developer.allegro.pl/documentation/#tag/Order-management
        """
        url = f"{self.base_url}/order/checkout-forms"

        params = {
            'limit': limit,
            'offset': offset
        }

        try:
            response = requests.get(url, headers=self.get_headers(), params=params)
            response.raise_for_status()

            data = response.json()
            orders = data.get('checkoutForms', [])

            print(f"✓ Pobrano {len(orders)} zamówień z API")
            return orders

        except requests.exceptions.RequestException as e:
            print(f"✗ Błąd pobierania z API: {e}")
            return []

    def update_order_status_api(self, order_id: str, new_status: str) -> bool:
        """
        Aktualizuje status zamówienia w API Allegro
        W rzeczywistości używa się różnych endpointów zależnie od akcji
        """
        # To jest przykład - w prawdziwym API może być inaczej
        url = f"{self.base_url}/order/checkout-forms/{order_id}/fulfillment"

        try:
            response = requests.put(
                url,
                headers=self.get_headers(),
                json={'status': new_status}
            )
            response.raise_for_status()
            print(f"✓ Zaktualizowano status w API: {order_id} -> {new_status}")
            return True

        except requests.exceptions.RequestException as e:
            print(f"✗ Błąd aktualizacji w API: {e}")
            return False
