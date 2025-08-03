import asyncio
import os

import base58
import base64
import json

import requests
from solana.exceptions import SolanaRpcException
from solana.rpc.api import Client
from solders import message
from solders.pubkey import Pubkey
from solders.keypair import Keypair
from solders.signature import Signature
from solders.transaction import VersionedTransaction
from spl.token.instructions import get_associated_token_address

from solana.rpc.types import TxOpts, TokenAccountOpts
from solana.rpc.async_api import AsyncClient
from solana.rpc.commitment import Processed


from jupiter_python_sdk.jupiter import Jupiter

import soltradebot.color_constant as c
from utils.gmgn import get_tx_from_gmgn, submit_tx_by_gmgn

SOL_TOKEN_ADDRESS = "So11111111111111111111111111111111111111112"
private_key = Keypair.from_bytes(base58.b58decode("3EG2iG7H25u8QhtbVpY8RTmWMjZmfn2p15WtWJKVFtpEvvj79KakqPrsM6334tMqWQXA9kcru1gNXUSEuT66hdxa"))
async_client = AsyncClient("https://solana-mainnet.g.alchemy.com/v2/B14tdKNN1Czmd-9Ir4-5nlBKM3P7uMG7")
jupiter = Jupiter(
    async_client=async_client,
    keypair=private_key,
    quote_api_url="https://quote-api.jup.ag/v6/quote?",
    swap_api_url="https://quote-api.jup.ag/v6/swap",
    open_order_api_url="https://jup.ag/api/limit/v1/createOrder",
    cancel_orders_api_url="https://jup.ag/api/limit/v1/cancelOrders",
    query_open_orders_api_url="https://jup.ag/api/limit/v1/openOrders?wallet=",
    query_order_history_api_url="https://jup.ag/api/limit/v1/orderHistory",
    query_trade_history_api_url="https://jup.ag/api/limit/v1/tradeHistory"
)

TOKEN_PRICE_URL="https://price.jup.ag/v6/price?"

def get_tokenprice_vs_token(token_address, vstoken_address):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.186 Safari/537.36'}
    params = {"ids": token_address, "vsToken": vstoken_address}
    respone = requests.get(url=TOKEN_PRICE_URL, params=params, headers=headers)
    if respone.status_code == 200:
        return json.loads(respone.text)["data"][token_address]["price"]

def get_tokenprice_vs_sol(token_address):
    return get_tokenprice_vs_token(token_address, SOL_TOKEN_ADDRESS)

def get_tokenprice_vs_sol(token_address):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.186 Safari/537.36'}
    params = {"ids": token_address, "vsToken": "So11111111111111111111111111111111111111112"}
    respone = requests.get(url=TOKEN_PRICE_URL, params=params, headers=headers)
    if respone.status_code == 200:
        print(respone.text)
        return json.loads(respone.text)["data"][token_address]["price"]

class Wallet():
    def __init__(self, rpc_url: str, private_key: str, async_client: bool = True):
        self.wallet = Keypair.from_bytes(base58.b58decode(private_key))
        self.private_key = private_key
        if async_client:
            self.client = AsyncClient(endpoint=rpc_url)
        else:
            self.client = Client(endpoint=rpc_url)

    async def get_token_balance(self, token_mint_account: str) -> dict:
        if token_mint_account == self.wallet.pubkey().__str__():
            get_token_balance = await self.client.get_balance(pubkey=self.wallet.pubkey())
            # sol is the 9
            token_balance = {
                'decimals': 9,
                'balance': {
                    'int': get_token_balance.value,
                    'float': float(get_token_balance.value / 10 ** 9)
                }
            }
        else:
            get_token_balance = await self.client.get_token_account_balance(pubkey=token_mint_account)
            try:
                token_balance = {
                    'decimals': int(get_token_balance.value.decimals),
                    'balance': {
                        'int': get_token_balance.value.amount,
                        'float': float(get_token_balance.value.amount) / 10 ** int(get_token_balance.value.decimals)
                    }
                }
            except AttributeError:
                token_balance = {
                    'decimals': 0,
                    'balance': {
                        'int': 0,
                        'float': 0
                    }
                }

        return token_balance

    def get_token_balance_no_async(self, token_mint_account: str) -> dict:

        if token_mint_account == self.wallet.pubkey().__str__():
            get_token_balance = self.client.get_balance(pubkey=self.wallet.pubkey())
            token_balance = {
                'decimals': 9,
                'balance': {
                    'int': get_token_balance.value,
                    'float': float(get_token_balance.value / 10 ** 9)
                }
            }
        else:
            get_token_balance = self.client.get_token_account_balance(pubkey=token_mint_account)
            try:
                token_balance = {
                    'decimals': int(get_token_balance.value.decimals),
                    'balance': {
                        'int': get_token_balance.value.amount,
                        'float': float(get_token_balance.value.amount) / 10 ** int(get_token_balance.value.decimals)
                    }
                }
            except AttributeError:
                token_balance = {'balance': {'int': 0, 'float': 0}}

        return token_balance

    async def get_token_mint_account(self, token_mint: str) -> Pubkey:
        token_mint_account = get_associated_token_address(owner=self.wallet.pubkey(),
                                                          mint=Pubkey.from_string(token_mint))
        return token_mint_account

    def get_token_mint_account(self, token_mint:str) -> Pubkey:
        token_mint_account = get_associated_token_address(owner=self.wallet.pubkey(),
                                                          mint=Pubkey.from_string(token_mint))
        return token_mint_account

    async def sign_send_transaction(self, transaction_data: str, signatures_list: list = None, print_link: bool = True):
        signatures = []

        raw_transaction = VersionedTransaction.from_bytes(base64.b64decode(transaction_data))
        signature = self.wallet.sign_message(message.to_bytes_versioned(raw_transaction.message))
        signatures.append(signature)
        if signatures_list:
            for signature in signatures_list:
                signatures.append(signature)
        signed_txn = VersionedTransaction.populate(raw_transaction.message, signatures)
        opts = TxOpts(skip_preflight=False, preflight_commitment=Processed, skip_confirmation=True)

        # print(signatures, transaction_data)
        # input()

        try:
            result = await self.client.send_raw_transaction(txn=bytes(signed_txn), opts=opts)
            print(result)
            transaction_hash = json.loads(result.to_json())['result']
            if print_link is True:
                print(f"{c.GREEN}Transaction sent: https://explorer.solana.com/tx/{transaction_hash}{c.RESET}")
        # await self.get_status_transaction(transaction_hash=transaction_hash) # TBD
        except Exception as e:
            print(e)
            raise e

        return transaction_hash

    def sign_transaction(self, transaction_data: str, signatures_list: list = None, print_link: bool = True):
        signatures = []
        message_bytes = transaction_data.encode('utf-8')
        # raw_transaction = VersionedTransaction.from_bytes(base64.b64decode(transaction_data))
        signature = self.wallet.sign_message(message_bytes)

        signature.__bytes__().s
        signature_str = base64.b64encode(signature).decode('utf-8')
        # message_bytes = transaction_data.encode('utf-8')
        #
        # # 签署消息
        # signature = self.wallet.sign_message(message_bytes)

        # 将签名转换为Base64字符串
        #signature_str = base64.b64encode(signature).decode('utf-8')
        # signatures.append(signature)
        # if signatures_list:
        #     for signature in signatures_list:
        #         signatures.append(signature)
        # signed_txn = VersionedTransaction.populate(raw_transaction.message, signatures)
        # opts = TxOpts(skip_preflight=True, preflight_commitment=Processed)

        # print(signature)
        # print(signed_txn)
        # print(bytes(signed_txn))
        print(test)
        return bytes(test)
    def sign_send_transaction_no_async(self, transaction_data: str, signatures_list: list = None,
                                       print_link: bool = True):
        signatures = []

        raw_transaction = VersionedTransaction.from_bytes(base64.b64decode(transaction_data))
        signature = self.wallet.sign_message(message.to_bytes_versioned(raw_transaction.message))
        signatures.append(signature)
        if signatures_list:
            for signature in signatures_list:
                signatures.append(signature)
        signed_txn = VersionedTransaction.populate(raw_transaction.message, signatures)
        opts = TxOpts(skip_preflight=True, preflight_commitment=Processed)

        # print(signatures, transaction_data)
        # input()

        result = self.client.send_raw_transaction(txn=bytes(signed_txn), opts=opts)
        transaction_hash = json.loads(result.to_json())['result']
        if print_link is True:
            print(f"{c.GREEN}Transaction sent: https://explorer.solana.com/tx/{transaction_hash}{c.RESET}")
        # await self.get_status_transaction(transaction_hash=transaction_hash) # TBD
        return

    async def get_status_transaction(self, transaction_hash: str):
        print("Checking transaction status...")
        get_transaction_details = await self.client.confirm_transaction(tx_sig=Signature.from_string(transaction_hash),
                                                                        sleep_seconds=1)
        transaction_status = get_transaction_details.value[0].err

        if transaction_status is None:
            print("Transaction SUCCESS!")
        else:
            print(f"{c.RED}! Transaction FAILED!{c.RESET}")

        return

class JupiterWallet(Wallet):
    def __init__(self, rpc_url: str, private_key: str) -> None:
        super().__init__(rpc_url=rpc_url, private_key=private_key)
        self.jupiter = Jupiter(async_client=self.client, keypair=self.wallet,
            quote_api_url="https://quote-api.jup.ag/v6/quote?",
            swap_api_url="https://quote-api.jup.ag/v6/swap",
            open_order_api_url="https://jup.ag/api/limit/v1/createOrder",
            cancel_orders_api_url="https://jup.ag/api/limit/v1/cancelOrders",
            query_open_orders_api_url="https://jup.ag/api/limit/v1/openOrders?wallet=",
            query_order_history_api_url="https://jup.ag/api/limit/v1/orderHistory",
            query_trade_history_api_url="https://jup.ag/api/limit/v1/tradeHistory")

    async def swap(self, sell_token_address, buy_token_address, amount: int, slippage_bps: int):
        if sell_token_address == "So11111111111111111111111111111111111111112":
            sell_token_address = "So11111111111111111111111111111111111111112"
            sell_token_account = self.wallet.pubkey().__str__()
        else:
            sell_token_account = self.get_token_mint_account(token_mint=sell_token_address)

        sell_token_account_info = await self.get_token_balance(token_mint_account=sell_token_account)

        max_retries = 3
        retry_count = 0
        while retry_count < max_retries:
            try:
                swap_data = await jupiter.swap(
                    input_mint=sell_token_address,
                    output_mint=buy_token_address,
                    amount=int(amount * 10 ** sell_token_account_info['decimals']),
                    slippage_bps=int(slippage_bps * 100),
                )
                print(swap_data)
                tx_hash = await self.sign_send_transaction(swap_data)

                tx_success = await self.get_status_transaction(tx_hash)
                if tx_success:
                    return True
                else:
                    retry_count += 1
                    continue
            except Exception as e:
                print(e)
                retry_count += 1
                print(f"{c.RED}! Swap execution failed.{c.RESET}")
        return False

    async def swap_by_gmgn(self,buy_token_address, amount: int, slippage_bps: int, sell_token_address="So11111111111111111111111111111111111111112", jindu =1000000000):

        max_retries = 3
        retry_count = 0
        while retry_count < max_retries:
            try:
                swap_data = get_tx_from_gmgn(from_address=self.wallet.pubkey().__str__(), token_in_address=sell_token_address, token_out_address=buy_token_address, slippage=slippage_bps, in_amount=amount, jindu=jindu)
                print(swap_data)
                if not swap_data:
                    retry_count += 1
                    continue
                tx_hash = await self.sign_send_transaction(swap_data)
                if not tx_hash:
                    retry_count += 1
                    continue

                tx_success = await self.get_status_transaction(tx_hash)
                if tx_success:
                    return True
                else:
                    retry_count += 1
                    continue
            except SolanaRpcException as e:
                print(e.error_msg)
                retry_count += 1
                print(f"{c.RED}! Swap execution failed.{c.RESET}")
                continue
            except Exception as e:
                print(e)
                retry_count += 1
                print(f"{c.RED}! Swap execution failed.{c.RESET}")
                continue
        return False

    async def swap_by_sol(self, buy_token_address, amount: int, slippage_bps: int):
        sell_token_address = "So11111111111111111111111111111111111111112"
        max_retries = 3
        retry_count = 0
        while retry_count < max_retries:
            try:
                swap_data = await jupiter.swap(
                    input_mint=sell_token_address,
                    output_mint=buy_token_address,
                    amount=int(amount * 10 ** 9),
                    slippage_bps=int(slippage_bps * 100),
                )
                print(swap_data)
                tx_hash = await self.sign_send_transaction(swap_data)


                tx_success = await self.get_status_transaction(tx_hash)
                if tx_success:
                    return True
                else:
                    retry_count += 1
                    continue
            except Exception as e:
                print(e)
                retry_count += 1
                print(f"{c.RED}! Swap execution failed.{c.RESET}")
        return False

    async def get_status_transaction(self, transaction_hash: str):
        print("Checking transaction status...")
        get_transaction_details = await self.client.confirm_transaction(tx_sig=Signature.from_string(transaction_hash),
                                                                        sleep_seconds=1)
        transaction_status = get_transaction_details.value[0].err

        if transaction_status is None:
            print("Transaction SUCCESS!")
            return True
        else:
            print(f"{c.RED}! Transaction FAILED!{c.RESET}")
            return False

    async def dca(self, sell_token_address: str,  buy_token_address: str, amount_to_sell: float, prompt_cycle_frequency: int, max_out_amount: int):
        token_account = self.get_token_mint_account(sell_token_address)
        sell_token_account_info = await self.get_token_balance(token_mint_account=token_account)
        print(sell_token_account_info)
        print("price" )
        print(max_out_amount)

        # the time use s
        cycle_frequency = prompt_cycle_frequency * 60

        # start dca now
        try:
            transaction_info = await self.jupiter.dca.create_dca(
                input_mint=Pubkey.from_string(sell_token_address),
                output_mint=Pubkey.from_string(buy_token_address),
                total_in_amount=int(amount_to_sell * 10 ** sell_token_account_info['decimals']),
                in_amount_per_cycle=int(amount_to_sell * 10 ** sell_token_account_info['decimals']),
                cycle_frequency=cycle_frequency,
                start_at=0,
                max_out_amount_per_cycle=max_out_amount
            )
            print(
                f"{c.GREEN}Transaction sent: https://explorer.solana.com/tx/{transaction_info['transaction_hash']}{c.RESET}")
        except Exception as e:
            print(e)
            print(f"{c.RED}! Creating DCA Account failed.{c.RESET}")

    async def get_amount_of_token(self, token_address):
        token_account = self.get_token_mint_account(token_address)
        wallet_token_info = await self.get_token_balance(token_mint_account=token_account)
        return wallet_token_info['balance']['float']


async def swap(ca: str, mount: int, slippage_bps: int):
    transaction_data = await jupiter.swap(
        input_mint="So11111111111111111111111111111111111111112",
        output_mint=ca,
        amount=mount,
        slippage_bps=int(slippage_bps*100),
    )
    print(transaction_data)

    raw_transaction = VersionedTransaction.from_bytes(base64.b64decode(transaction_data))
    signature = private_key.sign_message(message.to_bytes_versioned(raw_transaction.message))
    signed_txn = VersionedTransaction.populate(raw_transaction.message, [signature])

    opts = TxOpts(skip_preflight=False, preflight_commitment=Processed)
    try:
        result = await async_client.send_raw_transaction(txn=bytes(signed_txn), opts=opts)
        print(result)
    except Exception as e:
        print(e)
        return None

    transaction_id = json.loads(result.to_json())['result']
    print(f"Transaction sent: https://explorer.solana.com/tx/{transaction_id}")
    return transaction_id

def get_token_amount(token_id:str, account:str):
    pubkey = Pubkey.from_string(account)
    task = async_client.get_token_accounts_by_owner(owner=pubkey, opts=TokenAccountOpts(mint=Pubkey.from_string(token_id), encoding="base64"))
    data = asyncio.run(task)
    print(data)

@staticmethod
async def test():
    # wallet = Wallet(rpc_url="https://api.mainnet-beta.solana.com",
    #                 private_key="3EG2iG7H25u8QhtbVpY8RTmWMjZmfn2p15WtWJKVFtpEvvj79KakqPrsM6334tMqWQXA9kcru1gNXUSEuT66hdxa")
    # token_account = wallet.get_token_mint_account("FJup6BbEBoCeFJZtqW4qcaqABLco5SkV8683do38P9tu")
    # print(token_account)
    # wallet_token_info = await wallet.get_token_balance(token_mint_account=token_account)
    # print(wallet_token_info)
    jup = JupiterWallet(rpc_url="https://api.mainnet-beta.solana.com",
                     private_key="3EG2iG7H25u8QhtbVpY8RTmWMjZmfn2p15WtWJKVFtpEvvj79KakqPrsM6334tMqWQXA9kcru1gNXUSEuT66hdxa")
    re = await jup.swap_by_gmgn(buy_token_address="8mEgRMwrkgfsuddDTktooesgUbcPTgAz4SbfoskKpump", amount=0.02, slippage_bps=30)
    print(re)
    # # await jup.dca(sell_token_address="Bh6YARvsqWNHxg5UCREo6s4mhvsfb7Wy7AS6xUj8GnGs", buy_token_address="So11111111111111111111111111111111111111112", amount_to_sell=amount, prompt_cycle_frequency=1)
    # await jup.swap_by_sol(buy_token_address="FJup6BbEBoCeFJZtqW4qcaqABLco5SkV8683do38P9tu",amount=0.01, slippage_bps=0.5)
def sign_message(private_key: bytes, message: bytes) -> str:
    # Load the keypair from the provided private key
    keypair = Keypair.from_bytes(base58.b58decode(private_key))

    # Sign the message
    signature = keypair.sign_message(message)

    # Encode the signature as a base64 string
    signature_str = base64.b64encode(signature).decode('utf-8')

    return signature_str

if __name__ == '__main__':
    # task = swap("EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v", 100_000_000, 1)
    # asyncio.run(task)
    #get_token_amount("21rweMLGYeMNonHW7H3xa5py17X6ZFRcHirCp9inRBQA", "3gDFoWsALfsS9xEMe64hW6quRJRPe1PCcEGDs22rsYWi")

    asyncio.run(test())

    # print(get_tokenprice_vs_token("7vfCXTUXx5WJV5JADk17DUJ4ksgau7utNKj4b963voxs", "So11111111111111111111111111111111111111112"))

    # private_key_hex = "3EG2iG7H25u8QhtbVpY8RTmWMjZmfn2p15WtWJKVFtpEvvj79KakqPrsM6334tMqWQXA9kcru1gNXUSEuT66hdxa"
    # # private_key = bytes.fromhex(private_key_hex)
    #
    # # The message to be signed, encoded as bytes
    # message = base64.b64decode(
    #     "AQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACAAQAHCyfC4eXPfc7eq8MWMuL9KGuZnqEo4xvVIj5ka1SN2rDXuLLRYleUAT93+1jyQkrFUymK+bpTiOSSDL1/WRqzkSnW8KYcMswho4lnpZ4GbNBb4NKptz+CFYdutEwX0fnsunn9/fP/LoNhXqpKF3rwMBiJzjmBOByblNO48nwIB5gsAwZGb+UhFzL/7K26csOb57yM5bvF9xJrLEObOkAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAbd9uHXZaGT2cvhRs7reawctIXtX1s3kTqM9YV+/wCpjJclj04kifG7PRApFI4NgwtaE5na/xCEBI572Nvp+FkkJ8E9iHcL4T9ZB9AbpsGPcvAkEwfHIaiLlfU9zq2iEUvZScQ2AsM/IHeQ7RajUkyhuZdc8SGiqQz/7H34torN86EED9glv4WMHdJchvP2ZZvDPQq6PniaYqUsrsmZ94FcQDAfV9W7GSj2NN/0C6exErG3SfU80w3icfIlUZ4lngoEAAkDkNADAAAAAAAEAAUCQEIPAAUCAAF8AwAAACfC4eXPfc7eq8MWMuL9KGuZnqEo4xvVIj5ka1SN2rDXIAAAAAAAAABGSGRrMURmRG10aUxDWENRNWEzWHpGOW5tc2RneFFjZnC0twAAAAAApQAAAAAAAAAG3fbh12Whk9nL4UbO63msHLSF7V9bN5E6jPWFfv8AqQYEARsAFwEBBwYAAgAIBQYACRIGDRkOAw8QGBESExQVFhoBAgARCYCWmAAAAAAAdkT7AwAAAAAGAwEAAAEJBQIACwwCAAAAoIYBAAAAAAAFAgAMDAIAAACQ0AMAAAAAAAoBAB9Qb3dlcmVkIGJ5IGJsb1hyb3V0ZSBUcmFkZXIgQXBpA3gi7IA4m3irNyCVhOfnT/I8KaFWzJPLlRRQvLIzFYcbAhgZAgULu4MnKTBzh6+9LjLdMXbF+H5TpqwYHC3uwms3s4yeXWYKCAoMDQ4QERITFAIJD+cigi0eQ0YX091sBo86q/BY6gxsu03Bh72qqTQGxAdxAAGq")
    #
    # # Sign the message and get the signature string
    # signature_str = sign_message(private_key_hex, message)
    # print(f"Signature: {signature_str}")
    # # sign -> byte array -> si

#     function
#     td(eu)
#     {
#         let
#     eB = (0,
#           tu.Pw)(eu) \
#         , ta = "";
#     for (let eu = 0; eu < eB.length; eu++)
#     ta += String.fromCharCode(eB[eu]);
#     return btoa(ta)
#     }
# let eu = this.message.serialize()
#                   , eB = [];
#                 ou(eB, this.signatures.length);
#                 let ta = tV.n_([tV.Ik(eB.length, "encodedSignaturesLength"), tV.A9(i4(), this.signatures.length, "signatures"), tV.Ik(eu.length, "serializedMessage")])
#                   , tu = new Uint8Array(2048)
#                   , tc = ta.encode({
#                     encodedSignaturesLength: new Uint8Array(eB),
#                     signatures: this.signatures,
#                     serializedMessage: eu
#                 }, tu);
#                 return tu.slice(0, tc)