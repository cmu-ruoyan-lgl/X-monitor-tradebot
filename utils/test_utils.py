import time

from mangodb_ops.orm_ops import get_tweet_since_time
from utils.gmgn import get_token_info
from utils.regex_utils import find_ca
import mangodb_ops.connect
from base64 import b64encode
from solders.message import Message
from solders.transaction import Transaction
from solders.keypair import Keypair
from solders.instruction import Instruction
from solders.pubkey import Pubkey
from solders.system_program import TransferParams, SystemProgram

# 创建发送者的密钥对
sender_keypair = Keypair()

# 接收者的公钥
receiver_pubkey = Pubkey("69hJsXcgBEe6bJeaTnJmDUVZFwonbSQJoUjWFposzwuQ")

# 交易金额（以 lamports 为单位）
amount = 1000000  # 1 SOL = 1,000,000,000 lamports

# 最近的区块哈希
recent_blockhash = "9KohuoDPF9FgQs8ajkDsDx8ztB3jkcw5ub3G6oQWdbA7"

# 创建转账指令
transfer_instruction = SystemProgram.transfer(TransferParams(
    from_pubkey=sender_keypair.pubkey(),
    to_pubkey=receiver_pubkey,
    lamports=amount
))

# 创建消息对象
message = Message([transfer_instruction], sender_keypair.pubkey())

# 创建交易对象
transaction = Transaction(message, recent_blockhash)

# 使用发送者的密钥对对交易进行签名
transaction.sign([sender_keypair])

# 序列化交易
serialized_transaction = transaction.serialize()

# 将序列化后的交易转换为 Base64 编码形式
base64_encoded_transaction = b64encode(serialized_transaction).decode('utf-8')

print("Base64 编码后的交易:", base64_encoded_transaction)

if __name__ == '__main__':
    text = '''今天是哥布林两周年，社群成员推出 sol meme 将会对哥布林holder 进行空投
    $dollur
    频道开盘之前发合约（喂饭）
    频道入口：https://t.me/cryptomole0
    
    8aUxPSbmPUybinzLFpJVxu64DopPMEmCWBb3k1p8USf5
    '''

    # ca = find_ca(text)[0]
    # print(ca)
    # ca_info = get_token_info(ca)
    # print(ca_info)
    # print(ca_info['price'])

    #print(get_tweet_since_time(171626753600))

    # test 3
    # ca = find_ca(text)[0]
    # print(get_ca_info(ca))