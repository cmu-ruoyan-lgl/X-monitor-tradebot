import asyncio

from soltradebot.tradebot import JupiterWallet


async def test():
    jup = JupiterWallet(rpc_url="https://api.mainnet-beta.solana.com",
                        private_key="3EG2iG7H25u8QhtbVpY8RTmWMjZmfn2p15WtWJKVFtpEvvj79KakqPrsM6334tMqWQXA9kcru1gNXUSEuT66hdxa")

    await jup.swap_by_gmgn(buy_token_address="37uXTBceR4TrS59hG35SBCzCJWLAZp9qtL9KZFSCdAPJ", amount=0.3,
                          slippage_bps=10)
if __name__ == '__main__':
    asyncio.run(test())