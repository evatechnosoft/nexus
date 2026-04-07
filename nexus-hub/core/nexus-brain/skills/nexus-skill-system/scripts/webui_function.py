# Open WebUI Function - Nexus Memory Bridge
# Bu kod, Open WebUI arayüzündeki 'Functions' kısmına yapıştırılmalıdır.

import requests

class Functions:
    def __init__(self):
        self.nexus_api_url = "http://192.168.1.186:4500/ops/memory"

    def get_nexus_memory(self, category: str = "PM") -> str:
        """
        Nexus projesinin hafızasını (PM, ST, LT) oku.
        :param category: Hafıza kategorisi (PM, ST, LT)
        """
        try:
            response = requests.get(f"{self.nexus_api_url}?category={category}")
            if response.status_code == 200:
                return str(response.json())
            return f"Error: Nexus API returned {response.status_code}"
        except Exception as e:
            return f"Error connecting to Nexus API: {str(e)}"
