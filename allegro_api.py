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
        https://developer.allegro.pl/tutorials/jak-obslugiwac-zamowienia-GRaj0qyvwtR
        https://developer.allegro.pl/documentation/#tag/Order-management

        Lista zamówień
        GET /order/checkout-forms - pozwoli ci pobrać listę zamówień. W takiej formie zapytanie zwróci maksymalnie 100 najnowszych zamówień. Lista zawiera zamówienia z ostatnich 12 miesięcy, z takim samym zestawem danych, jakie możesz zobaczyć w szczegółach zamówienia.


        Dane zawracane w response sortujemy na podstawie daty z pola "boughtAt". Jeśli użytkownik zapłaci za zakupione towary później informacja o takim zamówieniu nie pojawi się jako najnowsza, tylko zgodnie z datą zakupu. Dlatego korzystaj z dziennika zdarzeń, by monitorować sprzedaż i poprawnie pobierać informacje o najnowszych zamówieniach.

        Możesz również pobrać listę zamówień dostosowaną do twoich potrzeb używając parametrów:

        limit - określ liczbę zamówień, jaką mamy zwrócić w odpowiedzi (przyjmuje wartości w zakresie 1-100),
        offset - wskaż miejsce, od którego chcesz pobrać kolejną porcję danych (przyjmuje wartości od 0 do liczba zamówień -1).

        np. GET /order/checkout-forms?limit=10&offset=9 - zwróci listę 10 zamówień od podanego punktu. Suma offset i limit nie może przekroczyć 10 000.

        Skorzystaj z filtrów:

        Status zamówienia - może zawierać jedną lub więcej wartości, np. GET /order/checkout-forms?status=BOUGHT&status=FILLED_IN;
        Status realizacji - może zawierać jedną lub więcej wartości, np. GET /order/checkout-forms?fulfillment.status=NEW&fulfillment.status=PROCESSING;
        Identyfikator płatności - GET /order/checkout-forms?payment.id=682c64b2-3108-11e9-b62a-6d16ee003b16;
        Identyfikator dopłaty - GET /order/checkout-forms?surcharges.id=21f96ba2-714f-11e9-a1f2-5b017850bf22;
        Data zamówienia - zakres czasu przekazujesz zgodnie z przyjętym standardem, ale chcąc przekazać datę w url, pamiętaj, aby wykorzystać encode, np. GET /order/checkout-forms?lineItems.boughtAt.lte=2018-07-31T08%3A48%3A14.889Z&lineItems.boughtAt.gte=2018-07-31T08%3A48%3A14.888Z;
        Data ostatniej zmiany zamówienia - np. GET /order/checkout-forms?updatedAt.lte=2018-07-31T08%3A48%3A14.889Z&updatedAt.gte=2018-07-31T08%3A48%3A14.888Z;
        Informacja o załączonych numerach przesyłek - np. GET /order/checkout-forms?fulfillment.shipmentSummary.lineItemsSent=ALL - zwróci zamówienia, gdzie dla wszystkich przedmiotów, które wchodzą w jego skład, dodano numer przesyłki;
        Serwis, w którym złożone zostało zamówienie - np. GET /order/checkout-forms?marketplace.id=allegro-pl.
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
