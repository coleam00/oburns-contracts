from brownie import network, config, interface
from brownie.network.contract import Contract
from scripts.helpers import get_account
from pathlib import Path
from web3 import Web3
import math
import csv

# OBURN address on BSC
OBURN_ADDRESS = "0x76E45C89254907bA5dd6558be3Dd78fD0A0320F3"

SET_BALANCES = True

def move_tokens_to_bsc(oburnAddress=None):
    account = get_account()

    currNetwork = network.show_active()

    if not oburnAddress:
        oburnAddress = OBURN_ADDRESS

    OBURN = interface.IERC20(oburnAddress)

    print(f"Account BNB balance is currently: {account.balance()}")

    totalBalance = 0

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
                    balances.append(float(holder[1]))
                    tokenBalance += float(holder[1])

        assert len(accounts) == len(balances)
        
        if SET_BALANCES:
            for i in range(len(accounts)):
                print(f"Sending {Web3.toWei(balances[i], 'ether')} OBURN to {accounts[i]}")
                OBURN.transfer(accounts[i], Web3.toWei(balances[i], "ether"), {"from": account})
        else:
            print(f"\nHolder information for {token}:\n")
            # print(accounts)
            # print(balances)
            print(f"Number of holders: {len(accounts)}")
            print(f"Sum of all account balances for {token} is: {sum(balances)}")
            totalBalance += sum(balances)

    if not SET_BALANCES:
        print(f"Final total balance is: {totalBalance}")

    print(f"\nAccount BNB balance is currently: {account.balance()}")

def main():
    move_tokens_to_bsc()