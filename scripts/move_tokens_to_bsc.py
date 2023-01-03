from brownie import network, config, interface
from brownie.network.contract import Contract
from scripts.helpers import get_account
from pathlib import Path
from web3 import Web3
import math
import csv

# TBURN address on BSC
TBURN_ADDRESS = "0x005dAd50D38245f764C3C4f127E72acB9b5ebb6B"
# OBURN address on BSC
OBURN_ADDRESS = "0xdbb1b2226528bc4751a91000df4ee938886d660e"

SET_BALANCES = True

def move_tokens_to_bsc(tburnAddress=None, oburnAddress=None):
    account = get_account()

    currNetwork = network.show_active()

    if not tburnAddress:
        tburnAddress = TBURN_ADDRESS

    if not oburnAddress:
        oburnAddress = OBURN_ADDRESS

    TBURN = interface.IERC20(tburnAddress)
    OBURN = interface.IERC20(oburnAddress)

    print(f"Account BNB balance is currently: {account.balance()}")

    for token in ["TBURN", "OBURN"]:
        accounts = []
        balances = []
        tokenBalance = 0

        filePath = Path(__file__).parent.parent
        with open(f'{filePath}/data/{token}Holders.csv', 'r') as holderDataFile:
            holderData = csv.reader(holderDataFile, delimiter=',')

            for holder in holderData:
                if holder[0] != "HolderAddress":
                    accounts.append(holder[0])
                    balances.append(int(float(holder[1])))
                    tokenBalance += int(float(holder[1]))

        assert len(accounts) == len(balances)
        
        if SET_BALANCES:
            for i in range(len(accounts)):
                if token == "TBURN":
                    print(f"Sending {Web3.toWei(balances[i], 'ether')} TBURN to {accounts[i]}")
                    # TBURN.transfer(accounts[i], Web3.toWei(balances[i], "ether"), {"from": account})
                elif token == "OBURN":
                    print(f"Sending {Web3.toWei(balances[i], 'ether')} OBURN to {accounts[i]}")
                    # OBURN.transfer(accounts[i], Web3.toWei(balances[i], "ether"), {"from": account})
        else:
            print(f"\nHolder information for {token}:\n")
            # print(accounts)
            # print(balances)
            print(f"Number of holders: {len(accounts)}")
            print(f"Sum of all account balances for {token} is: {sum(balances)}")

    print(f"\nAccount BNB balance is currently: {account.balance()}")

def main():
    move_tokens_to_bsc()