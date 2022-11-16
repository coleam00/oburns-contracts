#!/usr/bin/python3
from brownie import (
    OburnTokenPresale,
    OburnExchange,
    config,
    network,
    Contract,
)
from scripts.helpers import get_account, VERIFY_NETWORKS

TBURN_ADDRESS = "0x005dAd50D38245f764C3C4f127E72acB9b5ebb6B"
TBURN_ADDRESS_TEST = ""
OBURN_ADDRESS = ""
OBURN_ADDRESS_TEST = ""
PRESALE_WALLET_ADDRESS = ""
PRESALE_WALLET_ADDRESS_TEST = ""
USDC_ADDRESS_TEST = "0xe6b8a5CF854791412c1f6EFC7CAf629f5Df1c747"
USDC_ADDRESS = "0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174"

# Set to True when doing production deployments
PROD = False

def deploy_presale_and_exchange(tburnAddress=None, oburnAddress=None, preSaleWalletAddress=None, usdcAddress=None):
    account = get_account()
    print(f"Deploying to {network.show_active()}")

    # If PROD is set to True, use the production TBURN, OBURN, presale wallet, and USDC addresses
    if PROD:
        tburnAddress = TBURN_ADDRESS
        oburnAddress = OBURN_ADDRESS
        preSaleWalletAddress = PRESALE_WALLET_ADDRESS
        usdcAddress = USDC_ADDRESS
    # Otherwise, check if the addresses aren't set as function parameters and use the test
    # addresses if they aren't. The function parameters are set when testing the smart contracts,
    # but not during production or testnet deployments.
    else:
        if not tburnAddress:
            tburnAddress = TBURN_ADDRESS_TEST
        if not oburnAddress:
            oburnAddress = OBURN_ADDRESS_TEST
        if not preSaleWalletAddress:
            preSaleWalletAddress = PRESALE_WALLET_ADDRESS_TEST
        if not usdcAddress:
            usdcAddress = USDC_ADDRESS_TEST


    # Deploys the OBURNS presale contract.
    oburnTokenPresale = OburnTokenPresale.deploy(
        preSaleWalletAddress,
        oburnAddress,
        usdcAddress,
        {"from": account},
        publish_source=network.show_active() in VERIFY_NETWORKS,
    )

    print(f"OBURN PreSale deployed to {oburnTokenPresale}")

    # Deploys the TBURN to OBURN exchange contract.
    oburnExchange = OburnExchange.deploy(
        tburnAddress,
        oburnAddress,
        {"from": account},
        publish_source=network.show_active() in VERIFY_NETWORKS,
    )

    print(f"TBURN to ORBURN exchange deployed to {oburnExchange}")

    return oburnTokenPresale, oburnExchange

def main():
    deploy_presale_and_exchange()