# app for mint atomicassets/nefty NFTs

"""
drop examples

(MAINNET) AtomicHub:
not wl:
    free:
        https://wax.atomichub.io/drops/63079
        https://wax.bloks.io/transaction/38bb8f1a1dbd0c27e4491c816f204ce970a72c61828e9a11be9487895a1a0178
    not free:

wl:
    free:

    not free:



(TESTNET) Nefty:
not wl:
    free:
        https://test.neftyblocks.com/c/abuztest1111/drops/2020
        https://wax-test.bloks.io/transaction/85b37ba2fbf42c0fe381a790d121e7e6d19e6ef1ffd71d6e4d934bc1be4efe49
    
    not free:
        https://test.neftyblocks.com/c/abuztest1111/drops/2022
        https://wax-test.bloks.io/transaction/fb924fd652c48a643384a12abc04178397f527146f40006161896b5edf0a3ffd


wl:
    free:
        https://test.neftyblocks.com/c/abuztest1111/drops/2021
        https://wax-test.bloks.io/transaction/8feccdc3f0c35dd9fb88b384a3547f0c644e952627937dad4b5914687d9344de
    
    not free:
        https://test.neftyblocks.com/c/abuztest1111/drops/2023
        https://wax-test.bloks.io/transaction/d5410269c50d1c320cc0b6c59cadfdb68a8aae49ddcf6efb034ad153649388b4

how nefty pay for cpu?
MAINNET POST https://cpu.neftyblocks.com/
TESTNET POST https://cpu-test.neftyblocks.com/


accept: application/json
accept-encoding: gzip, deflate, br
accept-language: ru-RU,ru;q=0.9
cache-control: no-cache
content-length: 411
content-type: application/json
dnt: 1
origin: https://test.neftyblocks.com
pragma: no-cache
referer: https://test.neftyblocks.com/
sec-ch-ua: "Chromium";v="106", "Google Chrome";v="106", "Not;A=Brand";v="99"
sec-ch-ua-mobile: ?0
sec-ch-ua-platform: "Windows"
sec-fetch-dest: empty
sec-fetch-mode: cors
sec-fetch-site: same-site
user-agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36

json={
    "tx": "ac8c526347fe13be28390000000003e04dc5ea1e9f979a00000000e88abca901e04dc5ea1e9f979a00000000a8ed323200903044341e9f979a001472b7e6ab303601d00d57c9dcfcf53100000000a8ed323220e4070000000000000000000000000000004e554c4c000000004e554c4c000000903044341e9f979a0000a8f426e94c4401d00d57c9dcfcf53100000000a8ed323233d00d57c9dcfcf531e4070000000000000100000000000000000000000b4e65667479426c6f636b73024742004e554c4c00000000"
}


"""
from litewax import Client, Payers
import cloudscraper
from dotenv import dotenv_values

ENV = dotenv_values(".env")

# try to get free cpu from neftyblocks
client = Client(private_key=ENV["PVT_KEY_TESTNET"], node=ENV["NODE"])

trx = client.Transaction(
    client.Contract("neftyblocksd").claimdrop(
        claimer=client.name,
        drop_id=2020,
        amount=1,
        intended_delphi_median=0,
        referrer="NeftyBlocks",
        country="GB",
        currency="0,NULL"
    ),
    client.Contract("neftyblocksd").assertprice(
        drop_id=2020,
        listing_price="0 NULL",
        settlement_symbol="0,NULL"
    ),
    client.Contract("neftybrespay").paycpu()
)

trx.pay_with(Payers.NEFTY).push()