from scripts.helpers import get_account
from scripts.deploy import deploy_presale_and_exchange
from scripts.deploy_mocks import deploy_mocks
from brownie import network, accounts, exceptions, chain
from web3 import Web3
import pytest
import time

# Tests to make sure users can exchange TBURN for OBURN.
def test_users_can_exchange():
    # Arrange
    account = get_account()
    account2 = get_account(2)

    TBURN, OBURN, USDC, _, _ = deploy_mocks()
    oburnTokenPresale, oburnExchange = deploy_presale_and_exchange(TBURN.address, OBURN.address, account2.address, USDC.address)

    tburnAmount = Web3.toWei(100, "ether")
    OBURN.transfer(oburnExchange.address, tburnAmount, {"from": account})
    TBURN.transfer(account2.address, tburnAmount, {"from": account})

    # Act
    TBURN.approve(oburnExchange.address, tburnAmount, {"from": account2})
    oburnExchange.OBURNExchange(tburnAmount, {"from": account2})

    # Assert
    assert TBURN.balanceOf(account2.address) == 0
    assert TBURN.balanceOf(oburnExchange.address) == tburnAmount
    assert OBURN.balanceOf(account2.address) == tburnAmount
    assert OBURN.balanceOf(oburnExchange.address) == 0

# Tests to make sure the owner can withdraw TBURN and OBURN from the contract.
def test_owner_can_withdraw_tburn_and_oburn():
    # Arrange
    account = get_account()
    account2 = get_account(2)

    TBURN, OBURN, USDC, _, _ = deploy_mocks()
    oburnTokenPresale, oburnExchange = deploy_presale_and_exchange(TBURN.address, OBURN.address, account2.address, USDC.address)

    tburnAmount = Web3.toWei(100, "ether")
    OBURN.transfer(oburnExchange.address, tburnAmount * 3, {"from": account})
    TBURN.transfer(account2.address, tburnAmount, {"from": account})

    # Act
    TBURN.approve(oburnExchange.address, tburnAmount, {"from": account2})
    oburnExchange.OBURNExchange(tburnAmount, {"from": account2})

    initialTBURNBalance = TBURN.balanceOf(account.address)
    initialOBURNBalance = OBURN.balanceOf(account.address)

    oburnExchange.withdrawSpecifiedTBURN(tburnAmount / 2, {"from": account})
    oburnExchange.withdrawSpecifiedOBURN(tburnAmount, {"from": account})
    oburnExchange.withdrawAllTBURN({"from": account})
    oburnExchange.withdrawAllOBURN({"from": account})

    # Assert
    assert TBURN.balanceOf(account.address) == initialTBURNBalance + tburnAmount
    assert OBURN.balanceOf(account.address) == initialOBURNBalance + tburnAmount * 2

# Tests to make sure the owner can rescue any tokens.
def test_owner_can_rescue_tokens():
    # Arrange
    account = get_account()
    account2 = get_account(2)

    TBURN, OBURN, USDC, _, _ = deploy_mocks()
    oburnTokenPresale, oburnExchange = deploy_presale_and_exchange(TBURN.address, OBURN.address, account2.address, USDC.address)

    usdcAmount = Web3.toWei(100, "ether")
    USDC.transfer(account2.address, usdcAmount, {"from": account})
    USDC.transfer(oburnExchange.address, usdcAmount, {"from": account2})

    # Act
    initialUSDCBalance = USDC.balanceOf(account.address)
    oburnExchange.rescueFundsWithAmount(USDC.address, usdcAmount / 5)
    oburnExchange.rescueFunds(USDC.address)

    # Assert
    assert USDC.balanceOf(oburnExchange.address) == 0
    assert USDC.balanceOf(account.address) == initialUSDCBalance + usdcAmount
    
# Tests to make sure the owner can pause and unpause exchanging.
def test_owner_can_pause_and_unpause_exchange():
    # Arrange
    account = get_account()
    account2 = get_account(2)

    TBURN, OBURN, USDC, _, _ = deploy_mocks()
    oburnTokenPresale, oburnExchange = deploy_presale_and_exchange(TBURN.address, OBURN.address, account2.address, USDC.address)

    tburnAmount = Web3.toWei(655, "ether")
    OBURN.transfer(oburnExchange.address, tburnAmount, {"from": account})
    TBURN.transfer(account2.address, tburnAmount, {"from": account})

    # Act / Assert
    TBURN.approve(oburnExchange.address, tburnAmount, {"from": account2})
    oburnExchange.OBURNExchange(tburnAmount / 5, {"from": account2})

    oburnExchange.pauseExchange({"from": account})

    with pytest.raises(exceptions.VirtualMachineError) as ex:
        oburnExchange.OBURNExchange(tburnAmount / 5, {"from": account2})
    assert "Pausable: paused" in str(ex.value)    

    oburnExchange.unpauseExchange({"from": account})

    oburnExchange.OBURNExchange(tburnAmount * 4 / 5, {"from": account2})

    assert TBURN.balanceOf(account2.address) == 0
    assert TBURN.balanceOf(oburnExchange.address) == tburnAmount
    assert OBURN.balanceOf(account2.address) == tburnAmount
    assert OBURN.balanceOf(oburnExchange.address) == 0

# Tests to make sure users need to approve the exchange contract to spend TBURN before exchanging for OBURN.
def test_users_must_approve_tburn():
    # Arrange
    account = get_account()
    account2 = get_account(2)

    TBURN, OBURN, USDC, _, _ = deploy_mocks()
    oburnTokenPresale, oburnExchange = deploy_presale_and_exchange(TBURN.address, OBURN.address, account2.address, USDC.address)

    tburnAmount = Web3.toWei(100, "ether")
    OBURN.transfer(oburnExchange.address, tburnAmount, {"from": account})
    TBURN.transfer(account2.address, tburnAmount, {"from": account})

    # Act / Assert
    
    with pytest.raises(exceptions.VirtualMachineError) as ex:
        oburnExchange.OBURNExchange(tburnAmount, {"from": account2})
    assert "You must first approve this contract to spend your TBURN to exchange it for OBURN." in str(ex.value)    