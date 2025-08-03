import asyncio
import json

import requests

from mangodb_ops.orm_ops import get_ca_by_address_db

url = "https://gmgn.ai/defi/quotation/v1/tokens/sol/search?"
headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.186 Safari/537.36'}

TX_URL = "https://gmgn.ai/defi/router/v1/sol/tx/get_swap_route?"

DEXSCREEN_URL="https://api.dexscreener.com/latest/dex/pairs/solana/"

GMGN_SUBMIT_TX_URL = "https://gmgn.ai/defi/router/v1/sol/tx/submit_signed_transaction"

GMGM_WALLET_PROFILE = "https://gmgn.ai/defi/quotation/v1/wallet/sol/holdings/{0}?orderby=last_active_timestamp&direction=desc&showsmall=true&sellout=false&limit=50&tx1d=true"
def get_token_info(CA):
    params = {'q' : CA}

    respone = requests.get(url=url, params=params, headers=headers)
    if respone.status_code == 200 and respone.json()['code'] == 0:
        print(respone.json())
        return respone.json()['data']['tokens'][0]


def get_token_price_by_gmgn(CA):
    params = {'q': CA}

    respone = requests.get(url=url, params=params, headers=headers)
    if respone.status_code == 200 and respone.json()['code'] == 0:
        print(respone.json())
        return respone.json()['data']['tokens'][0]['price']

def get_tx_from_gmgn(from_address:str, slippage:int,token_in_address:str, token_out_address:str,in_amount:float,fee=0.002,is_anti_mev="false", jindu=1000000000):
    params = {
        "token_in_chain": "sol",
        "token_out_chain": "sol",
        "from_address": from_address,
        "slippage": slippage,
        "token_in_address": token_in_address,
        "token_out_address": token_out_address,
        "in_amount": int(in_amount * jindu),
        "fee": fee,
        "is_anti_mev": is_anti_mev
    }
    print(token_out_address)
    rp = requests.get(url=TX_URL, params=params, headers=headers)
    if rp.status_code == 200:
        print(rp.json())
        return rp.json()['data']['raw_tx']['swapTransaction']
    return None

def get_tx_from_gmgn(from_address:str, slippage:int,token_in_address:str, token_out_address:str,in_amount:float,fee=0.002,is_anti_mev="false", jindu=1000000000):
    params = {
        "token_in_chain": "sol",
        "token_out_chain": "sol",
        "from_address": from_address,
        "slippage": slippage,
        "token_in_address": token_in_address,
        "token_out_address": token_out_address,
        "in_amount": int(in_amount * jindu),
        "fee": fee,
        "is_anti_mev": is_anti_mev
    }
    print(token_out_address)
    rp = requests.get(url=TX_URL, params=params, headers=headers)
    if rp.status_code == 200:
        print(rp.json())
        return rp.json()['data']['raw_tx']['swapTransaction']
    return None

def submit_tx_by_gmgn(tx:str):
    body = {"signed_tx": tx}
    rp = requests.post(url=GMGN_SUBMIT_TX_URL, data=body)
    jp = json.loads(rp.text)
    print(rp.text)
    if rp.status_code == 200:
        err = jp["data"]["resArr"][0]["err"]
        if err != None:
            return None
        return jp['data']['hash']

def get_tokenprice_vs_sol_by_dexscreen(token_address):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.186 Safari/537.36'}
    respone = requests.get(url=DEXSCREEN_URL+token_address, headers=headers)
    if respone.status_code == 200:
        print(respone.text)
        return json.loads(respone.text)["pairs"][0]["priceNative"]


def get_wallet_profile(wallet_address):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.186 Safari/537.36'}
    print(GMGM_WALLET_PROFILE.format(wallet_address))
    respone = requests.get(url=GMGM_WALLET_PROFILE.format(wallet_address), headers=headers)
    if respone.status_code == 200:
        print(respone.text)
        return json.loads(respone.text)["data"]["holdings"]

async def test():
    jup = JupiterWallet(rpc_url="https://api.mainnet-beta.solana.com",
                        private_key="3EG2iG7H25u8QhtbVpY8RTmWMjZmfn2p15WtWJKVFtpEvvj79KakqPrsM6334tMqWQXA9kcru1gNXUSEuT66hdxa")
    re = await jup.swap_by_gmgn(buy_token_address="3S8qX1MsMqRbiwKg2cQyx7nis1oHMgaCuc9c4VfvVdPN", amount=0.01,
                                slippage_bps=10)
if __name__ == '__main__':

    jsonoi = '''{
    "code": 0,
    "msg": "success",
    "data": {
        "hash": "2iGmLpaKFUf1atQbaUiK1V4F9z1Rn9VoiToLBa2WNDQcXYhFMPfAYzRRqph3j97fkWoGZdnNjgb5TjiPqgJ5x2td",
        "resArr": [
            {
                "hash": "2iGmLpaKFUf1atQbaUiK1V4F9z1Rn9VoiToLBa2WNDQcXYhFMPfAYzRRqph3j97fkWoGZdnNjgb5TjiPqgJ5x2td",
                "err": null
            },
            {
                "hash": "2iGmLpaKFUf1atQbaUiK1V4F9z1Rn9VoiToLBa2WNDQcXYhFMPfAYzRRqph3j97fkWoGZdnNjgb5TjiPqgJ5x2td",
                "err": null
            },
            {
                "hash": "2iGmLpaKFUf1atQbaUiK1V4F9z1Rn9VoiToLBa2WNDQcXYhFMPfAYzRRqph3j97fkWoGZdnNjgb5TjiPqgJ5x2td",
                "err": null
            },
            {
                "hash": "2iGmLpaKFUf1atQbaUiK1V4F9z1Rn9VoiToLBa2WNDQcXYhFMPfAYzRRqph3j97fkWoGZdnNjgb5TjiPqgJ5x2td",
                "err": null
            },
            {
                "hash": "2iGmLpaKFUf1atQbaUiK1V4F9z1Rn9VoiToLBa2WNDQcXYhFMPfAYzRRqph3j97fkWoGZdnNjgb5TjiPqgJ5x2td",
                "err": null
            }
        ]
    }
}
    '''
    # asyncio.run(test)
    # print(re)
    # print(json.loads(jsonoi))
    # print(get_tokenprice_vs_sol_by_dexscreen("HctjAgcQTdz5pRBGMsqGGMhZTSFGZfuH4VnvxFjkTFxw"))
    print(get_wallet_profile("3gDFoWsALfsS9xEMe64hW6quRJRPe1PCcEGDs22rsYWi"))