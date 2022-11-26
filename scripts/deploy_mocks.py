#!/usr/bin/python3
from brownie import MockToken, MockUniswapV2Factory, MockUniswapV2Router02, config, network
from scripts.helpers import get_account, VERIFY_NETWORKS

# Deploys mock tokens and mock Uniswap contracts for testing.
def deploy_mocks():
    account = get_account()
    print(f"Deploying to {network.show_active()}")

    genericToken1 = MockToken.deploy({"from": account}, publish_source=network.show_active() in VERIFY_NETWORKS)
    genericToken2 = MockToken.deploy({"from": account}, publish_source=network.show_active() in VERIFY_NETWORKS)
    genericToken3 = MockToken.deploy({"from": account}, publish_source=network.show_active() in VERIFY_NETWORKS)

    mockUniswapV2Factory = MockUniswapV2Factory.deploy({"from": account}, publish_source=network.show_active() in VERIFY_NETWORKS)
    mockUniswapV2Router02 = MockUniswapV2Router02.deploy(mockUniswapV2Factory.address, {"from": account}, publish_source=network.show_active() in VERIFY_NETWORKS)

    return genericToken1, genericToken2, genericToken3, mockUniswapV2Factory, mockUniswapV2Router02

def main():
    deploy_mocks()