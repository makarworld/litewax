from cloudscraper import create_scraper


def get_median_price():
    s = create_scraper()
    
    r = s.post("https://wax.greymass.com/v1/chain/get_table_rows", json={
        "json": True,
        "code": "delphioracle",
        "scope": "waxpusd",
        "table": "datapoints",
        "lower_bound": None,
        "upper_bound": None,
        "index_position": 1,
        "key_type": "",
        "limit": "10",
        "reverse": False,
        "show_payer": True
    }).json()

    return r['rows'][0]['data']['median']

if __name__ == "__main__":
    r = get_median_price()
    print(r)