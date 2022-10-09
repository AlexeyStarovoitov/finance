import pandas as pd
import requests
import numpy

class dcf_calculation:
    def __init__(self, url=None):
        response = requests.get(url)
        target_csv_path = "input.csv"
        with open(target_csv_path, "wb") as self.f:
            self.f.write(response.content)
            
        self.asset_db = pd.read_csv(target_csv_path)


