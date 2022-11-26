#!/usr/bin/python3
from brownie import (
    OnlyBurns,
    config,
    network,
    Contract,
)
from scripts.helpers import get_account, VERIFY_NETWORKS

ROUTER_ADDRESS = "0xa5E0829CaCEd8fFDD4De3c43696c57F7D7A678ff"
ROUTER_ADDRESS_TEST = ""
SERVICE_WALLET = "0x5e1027D4c3e991823Cf30d1f9051E9DB91e2B45C"
SERVICE_WALLET_TEST = ""
USDC_ADDRESS_TEST = "0xe6b8a5CF854791412c1f6EFC7CAf629f5Df1c747"
USDC_ADDRESS = "0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174"

# Set to True when doing production deployments
PROD = False

def deploy_oburn_token(routerAddress=None, serviceWallet=None, usdcAddress=None):
    account = get_account()
    print(f"Deploying to {network.show_active()}")

    if PROD:
        routerAddress = ROUTER_ADDRESS
        serviceWallet = SERVICE_WALLET
        usdcAddress = USDC_ADDRESS
    else:
        if not routerAddress:
            routerAddress = ROUTER_ADDRESS_TEST
        
        if not serviceWallet:
            serviceWallet = SERVICE_WALLET_TEST

        if not usdcAddress:
            usdcAddress = USDC_ADDRESS_TEST

    # Deploys the OBURNS presale contract.
    oburnToken = OnlyBurns.deploy(routerAddress, serviceWallet, usdcAddress, {"from": account}, publish_source=network.show_active() in VERIFY_NETWORKS,)

    return oburnToken

def main():
    deploy_oburn_token()