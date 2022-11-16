#!/usr/bin/python3
from brownie import GenericToken, config, network
from scripts.helpers import get_account, VERIFY_NETWORKS

# Deploys a mock token and mock aggregator for testing on a local blockchain environment.
def deploy_mocks():
    account = get_account()
    print(f"Deploying to {network.show_active()}")

    genericToken1 = GenericToken.deploy({"from": account}, publish_source=network.show_active() in VERIFY_NETWORKS)
    genericToken2 = GenericToken.deploy({"from": account}, publish_source=network.show_active() in VERIFY_NETWORKS)
    genericToken3 = GenericToken.deploy({"from": account}, publish_source=network.show_active() in VERIFY_NETWORKS)

    return genericToken1, genericToken2, genericToken3

def main():
    deploy_mocks()