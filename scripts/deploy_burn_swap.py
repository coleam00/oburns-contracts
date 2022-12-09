#!/usr/bin/python3
from brownie import (
    BurnSwap,
    config,
    network,
    Contract,
)
from scripts.helpers import get_account, VERIFY_NETWORKS

OBURN_ADDRESS = ""
OBURN_ADDRESS_TEST = "0x90a603fa876980B38cB6415C0328aeeC6C33C3f4"
USDC_ADDRESS = "0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174"
USDC_ADDRESS_TEST = "0x7F8754f9CC58A8FfA69C755ae425e84B55bB3a0d"
PAIR_ADDRESS = ""
PAIR_ADDRESS_TEST = "0xc1A2C05C4FbD1758401c6f11876b5AC741f069C8"
ROUTER_ADDRESS = "0xa5E0829CaCEd8fFDD4De3c43696c57F7D7A678ff"
ROUTER_ADDRESS_TEST = "0x9Ac64Cc6e4415144C455BD8E4837Fea55603e5c3"

# Set to True when doing production deployments
PROD = False

def deploy_burn_swap(oburnAddress=None, usdcAddress=None, pairAddress=None, routerAddress=None):
    account = get_account()
    print(f"Deploying to {network.show_active()}")

    # If PROD is set to True, use the production addresses
    if PROD:
        oburnAddress = OBURN_ADDRESS
        usdcAddress = USDC_ADDRESS
        pairAddress = PAIR_ADDRESS
        routerAddress = ROUTER_ADDRESS
    # Otherwise, check if the addresses aren't set as function parameters and use the test
    # addresses if they aren't. The function parameters are set when testing the smart contracts,
    # but not during production or testnet deployments.
    else:
        if not oburnAddress:
            oburnAddress = OBURN_ADDRESS_TEST
        if not usdcAddress:
            usdcAddress = USDC_ADDRESS_TEST
        if not pairAddress:
            pairAddress = PAIR_ADDRESS_TEST
        if not routerAddress:
            routerAddress = ROUTER_ADDRESS_TEST

    # Deploys the Burn Swap contract.
    burnSwap = BurnSwap.deploy(
        routerAddress,
        pairAddress,
        oburnAddress,
        usdcAddress,
        {"from": account},
        publish_source=network.show_active() in VERIFY_NETWORKS,
    )

    print(f"Burn Swap deployed to {burnSwap}")

    return burnSwap

def main():
    deploy_burn_swap()