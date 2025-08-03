import re


def find_ca(tweet_text):
    return re.findall("[1-9A-HJ-NP-Za-km-z]{32,44}", tweet_text, re.M)

if __name__ == '__main__':
    print(find_ca("pump.fun/8gevADWP5aNTkRXpLDMU39S791muhehYPrXddPCPLuA2"))