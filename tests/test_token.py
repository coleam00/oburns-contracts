from scripts.helpers import get_account
from scripts.deploy_token import deploy_oburn_token
from scripts.deploy_mocks import deploy_mocks
from brownie import network, accounts, exceptions, chain
from web3 import Web3
import pytest
import time

# Tests to make sure users can transfer oburn
def test_users_can_transfer_oburn():
    # Arrange
    account = get_account()
    account2 = get_account(2)
    account3 = get_account(3)

    _, _, USDC, mockUniswapV2Factory, mockUniswapV2Router02 = deploy_mocks()
    oburn = deploy_oburn_token(mockUniswapV2Router02.address, account2.address, USDC.address)

    # Act
    transferAmount = 10000000000
    oburn.transfer(account3.address, transferAmount, {"from": account})
    oburn.enableTrading({"from": account})
    oburn.transfer(account.address, transferAmount / 2, {"from": account3})

    # Assert
    assert oburn.balanceOf(account.address) == oburn.totalSupply() - transferAmount / 2
    assert oburn.balanceOf(account3.address) == transferAmount / 2

# Tests to make sure owner can blacklist users from trading
def test_owner_can_blacklist_users():
    # Arrange
    account = get_account()
    account2 = get_account(2)
    account3 = get_account(3)

    _, _, USDC, mockUniswapV2Factory, mockUniswapV2Router02 = deploy_mocks()
    oburn = deploy_oburn_token(mockUniswapV2Router02.address, account2.address, USDC.address)

    # Act / Assert
    transferAmount = 10000000000
    oburn.transfer(account3.address, transferAmount, {"from": account})
    oburn.enableTrading({"from": account})
    oburn.transfer(account.address, transferAmount / 4, {"from": account3})

    oburn.blacklistOrUnblacklistUser(account3.address, True, {"from": account})

    with pytest.raises(exceptions.VirtualMachineError) as ex:
        oburn.transfer(account.address, transferAmount / 4, {"from": account3})
    assert "Sender is blacklisted from trading." in str(ex.value)  

    with pytest.raises(exceptions.VirtualMachineError) as ex:
        oburn.transfer(account3.address, transferAmount, {"from": account})
    assert "Recipient is blacklisted from trading." in str(ex.value)  

    oburn.blacklistOrUnblacklistUser(account3.address, False, {"from": account})

    oburn.transfer(account.address, transferAmount / 4, {"from": account3})

    assert oburn.balanceOf(account.address) == oburn.totalSupply() - transferAmount / 2
    assert oburn.balanceOf(account3.address) == transferAmount / 2    

# Tests to make sure owner can disable  and enable DEX trading
def test_owner_can_disable_and_enable_dex_trading():
    # Arrange
    account = get_account()
    account2 = get_account(2)
    account3 = get_account(3)

    _, _, USDC, mockUniswapV2Factory, mockUniswapV2Router02 = deploy_mocks()
    oburn = deploy_oburn_token(mockUniswapV2Router02.address, account2.address, USDC.address)

    # Act / Assert
    transferAmount = 1000000000000000
    oburn.transfer(account3.address, transferAmount, {"from": account})
    oburn.enableTrading({"from": account})

    # Factory is also the pair for testing purposes
    with pytest.raises(exceptions.VirtualMachineError) as ex:
        oburn.transfer(mockUniswapV2Factory.address, transferAmount / 4, {"from": account3})
    assert "DEX Trading is currently disabled. You must trade directly through the Only Burns DApp." in str(ex.value)  

    # Someone excluded from fees like the owner can still trade on the DEX
    oburn.transfer(mockUniswapV2Factory.address, transferAmount, {"from": account})

    with pytest.raises(exceptions.VirtualMachineError) as ex:
        oburn.transfer(account3.address, transferAmount / 4, {"from": mockUniswapV2Factory})
    assert "DEX Trading is currently disabled. You must trade directly through the Only Burns DApp." in str(ex.value)      

    oburn.enableOrDisableDEXTrading(True, {"from": account})

    oburn.transfer(mockUniswapV2Factory.address, transferAmount / 2, {"from": account3})  

    sellFee = (transferAmount / 2 * 10) / pow(10, 10)
    assert oburn.balanceOf(account.address) == oburn.totalSupply() - transferAmount * 2 + sellFee
    assert oburn.balanceOf(account3.address) == transferAmount / 2
    assert oburn.balanceOf(mockUniswapV2Factory.address) == transferAmount * 3 / 2 - sellFee