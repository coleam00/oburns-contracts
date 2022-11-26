from scripts.helpers import get_account
from scripts.deploy import deploy_presale_and_exchange
from scripts.deploy_mocks import deploy_mocks
from brownie import network, accounts, exceptions, chain
from web3 import Web3
import pytest
import time

# Tests to make sure the presale and OBURN exchange contracts can be deployed successfully.
def test_deployments():
    # Arrange
    account = get_account()
    account2 = get_account(2)

    # Act
    TBURN, OBURN, USDC, _, _ = deploy_mocks()
    oburnTokenPresale, oburnExchange = deploy_presale_and_exchange(TBURN.address, OBURN.address, account2.address, USDC.address)

    # Assert
    assert oburnTokenPresale.token() == OBURN.address
    assert oburnExchange._tburn() == TBURN.address
    assert oburnExchange._oburn() == OBURN.address

# Tests to make sure users can purchase OBURN in the presale with USDC during the whitelist sale.
def test_user_can_purchase_OBURN_in_whitelist_presale():
    # Arrange
    account = get_account()
    account2 = get_account(2)

    TBURN, OBURN, USDC, _, _ = deploy_mocks()
    oburnTokenPresale, oburnExchange = deploy_presale_and_exchange(TBURN.address, OBURN.address, account.address, USDC.address)

    presaleOburnAmount = Web3.toWei(1000000000000000, "ether")
    USDCAmount = 1000000
    OBURN.transfer(oburnTokenPresale.address, presaleOburnAmount, {"from": account})
    USDC.transfer(account2.address, USDCAmount, {"from": account})

    oburnTokenPresale.lockSaleParameters({"from": account})
    oburnTokenPresale.setWhitelistSaleActive(True, {"from": account})
    oburnTokenPresale.addAddressToWhitelist(account2.address, {"from": account})

    # Act
    USDC.approve(oburnTokenPresale.address, USDCAmount, {"from": account2})
    oburnTokenPresale.buyTokens(account2.address, USDCAmount, {"from": account2})

    # Assert
    whitelistSaleRate = 500000
    expectedOburnAmount = USDCAmount * whitelistSaleRate * pow(10, 12)
    assert OBURN.balanceOf(account2.address) == expectedOburnAmount
    assert oburnTokenPresale.singleAddressCheckOburnAmountPurchased({"from": account2}) == expectedOburnAmount
    assert oburnTokenPresale.singleAddressCheckOburnAmountAvailable({"from": account2}) == oburnTokenPresale.getMaxOburnPerAddress() - expectedOburnAmount
    assert USDC.balanceOf(account2.address) == 0
    assert oburnTokenPresale.usdcRaised() == USDCAmount

# Tests to make sure users can purchase OBURN in the presale with USDC during the public sale.
def test_user_can_purchase_OBURN_in_public_presale():
    # Arrange
    account = get_account()
    account2 = get_account(2)

    TBURN, OBURN, USDC, _, _ = deploy_mocks()
    oburnTokenPresale, oburnExchange = deploy_presale_and_exchange(TBURN.address, OBURN.address, account.address, USDC.address)

    presaleOburnAmount = Web3.toWei(1000000000000000, "ether")
    USDCAmount = 3000000
    OBURN.transfer(oburnTokenPresale.address, presaleOburnAmount, {"from": account})
    USDC.transfer(account2.address, USDCAmount, {"from": account})

    oburnTokenPresale.lockSaleParameters({"from": account})
    oburnTokenPresale.setWhitelistSaleActive(True, {"from": account})
    oburnTokenPresale.setPublicSaleActive(True, {"from": account})

    # Act
    USDC.approve(oburnTokenPresale.address, USDCAmount, {"from": account2})
    oburnTokenPresale.buyTokens(account2.address, USDCAmount, {"from": account2})

    # Assert
    publicSaleRate = 250000
    expectedOburnAmount = USDCAmount * publicSaleRate * pow(10, 12)
    assert OBURN.balanceOf(account2.address) == expectedOburnAmount
    assert oburnTokenPresale.singleAddressCheckOburnAmountPurchased({"from": account2}) == expectedOburnAmount
    assert oburnTokenPresale.singleAddressCheckOburnAmountAvailable({"from": account2}) == oburnTokenPresale.getMaxOburnPerAddress() - expectedOburnAmount
    assert USDC.balanceOf(account2.address) == 0
    assert oburnTokenPresale.usdcRaised() == USDCAmount

# Tests to make sure the owner can change parameters before starting the presale.
def test_owner_can_update_parameters_for_presale():
    # Arrange
    account = get_account()
    account2 = get_account(2)
    account3 = get_account(3)

    TBURN, OBURN, USDC, _, _ = deploy_mocks()
    oburnTokenPresale, oburnExchange = deploy_presale_and_exchange(TBURN.address, OBURN.address, account.address, USDC.address)

    presaleOburnAmount = Web3.toWei(1000000000000000, "ether")
    USDCAmount = 10000000
    OBURN.transfer(oburnTokenPresale.address, presaleOburnAmount, {"from": account})
    USDC.transfer(account2.address, USDCAmount, {"from": account})
    USDC.transfer(account3.address, USDCAmount, {"from": account})

    # Act
    saleRateMultAmount = 5
    whiteListSaleRate = oburnTokenPresale.getWhitelistSaleRate()
    oburnTokenPresale.setWhitelistSaleRate(whiteListSaleRate * saleRateMultAmount, {"from": account})

    publicSaleRate = oburnTokenPresale.getPublicSaleRate()
    oburnTokenPresale.setPublicSaleRate(publicSaleRate * saleRateMultAmount, {"from": account})

    oburnTokenPresale.setMaxOburnPerAddress(presaleOburnAmount, {"from": account})
    oburnTokenPresale.setWhitelistSaleOburnCap(presaleOburnAmount, {"from": account})
    oburnTokenPresale.setPublicSaleOburnCap(presaleOburnAmount, {"from": account})

    oburnTokenPresale.lockSaleParameters({"from": account})
    oburnTokenPresale.setWhitelistSaleActive(True, {"from": account})
    oburnTokenPresale.addAddressToWhitelist(account2.address, {"from": account})

    USDC.approve(oburnTokenPresale.address, USDCAmount, {"from": account2})
    oburnTokenPresale.buyTokens(account2.address, USDCAmount, {"from": account2})

    oburnTokenPresale.setPublicSaleActive(True, {"from": account})

    USDC.approve(oburnTokenPresale.address, USDCAmount, {"from": account3})
    oburnTokenPresale.buyTokens(account3.address, USDCAmount, {"from": account3})

    # Assert
    whitelistSaleRate = 500000 * saleRateMultAmount
    publicSaleRate = 250000 * saleRateMultAmount
    expectedOburnAmountWhitelist = USDCAmount * whitelistSaleRate * pow(10, 12)
    expectedOburnAmountPublic = USDCAmount * publicSaleRate * pow(10, 12)
    assert OBURN.balanceOf(account2.address) == expectedOburnAmountWhitelist
    assert OBURN.balanceOf(account3.address) == expectedOburnAmountPublic
    assert oburnTokenPresale.singleAddressCheckOburnAmountPurchased({"from": account2}) == expectedOburnAmountWhitelist
    assert oburnTokenPresale.singleAddressCheckOburnAmountPurchased({"from": account3}) == expectedOburnAmountPublic
    assert oburnTokenPresale.singleAddressCheckOburnAmountAvailable({"from": account2}) == oburnTokenPresale.getMaxOburnPerAddress() - expectedOburnAmountWhitelist
    assert oburnTokenPresale.singleAddressCheckOburnAmountAvailable({"from": account3}) == oburnTokenPresale.getMaxOburnPerAddress() - expectedOburnAmountPublic
    assert USDC.balanceOf(account2.address) == 0
    assert USDC.balanceOf(account3.address) == 0

# Tests to make sure the owner can end the sale and users cant purchase OBURN afterwards.
def test_owner_can_end_sale():
    # Arrange
    account = get_account()
    account2 = get_account(2)

    TBURN, OBURN, USDC, _, _ = deploy_mocks()
    oburnTokenPresale, oburnExchange = deploy_presale_and_exchange(TBURN.address, OBURN.address, account.address, USDC.address)

    presaleOburnAmount = Web3.toWei(1000000000000000, "ether")
    USDCAmount = 1000000
    OBURN.transfer(oburnTokenPresale.address, presaleOburnAmount, {"from": account})
    USDC.transfer(account2.address, USDCAmount, {"from": account})

    oburnTokenPresale.lockSaleParameters({"from": account})
    oburnTokenPresale.setWhitelistSaleActive(True, {"from": account})
    oburnTokenPresale.addAddressToWhitelist(account2.address, {"from": account})

    # Act
    USDC.approve(oburnTokenPresale.address, USDCAmount * 100, {"from": account2})
    oburnTokenPresale.buyTokens(account2.address, USDCAmount, {"from": account2})
    oburnTokenPresale.setPublicSaleActive(True, {"from": account})

    initialOBURNBalance = OBURN.balanceOf(account.address)
    oburnTokenPresale.endSale({"from": account})

    # Assert
    whitelistSaleRate = 500000
    expectedOburnAmount = USDCAmount * whitelistSaleRate * pow(10, 12)
    assert OBURN.balanceOf(account.address) == initialOBURNBalance + presaleOburnAmount - expectedOburnAmount

    with pytest.raises(exceptions.VirtualMachineError) as ex:
        oburnTokenPresale.buyTokens(account2.address, USDCAmount, {"from": account2})
    assert "Whitelist sale and public sale are both not active" in str(ex.value)

# Tests to make sure users have to approve the contract to spend USDC before purchasing OBURN in the presale.
def test_user_must_approve_usdc():
    # Arrange
    account = get_account()
    account2 = get_account(2)

    TBURN, OBURN, USDC, _, _ = deploy_mocks()
    oburnTokenPresale, oburnExchange = deploy_presale_and_exchange(TBURN.address, OBURN.address, account.address, USDC.address)

    presaleOburnAmount = Web3.toWei(1000000000000000, "ether")
    USDCAmount = 1000000
    OBURN.transfer(oburnTokenPresale.address, presaleOburnAmount, {"from": account})
    USDC.transfer(account2.address, USDCAmount, {"from": account})

    oburnTokenPresale.lockSaleParameters({"from": account})
    oburnTokenPresale.setWhitelistSaleActive(True, {"from": account})
    oburnTokenPresale.addAddressToWhitelist(account2.address, {"from": account})

    # Act / Assert
    with pytest.raises(exceptions.VirtualMachineError) as ex:
        oburnTokenPresale.buyTokens(account2.address, USDCAmount, {"from": account2})
    assert "Sender hasn't allowed this contract to spend enough USDC for this presale purchase." in str(ex.value)    

# Tests to make sure users can't purchase above the purchase caps.
def test_user_cant_purchase_above_cap():
    # Arrange
    account = get_account()
    account2 = get_account(2)

    TBURN, OBURN, USDC, _, _ = deploy_mocks()
    oburnTokenPresale, oburnExchange = deploy_presale_and_exchange(TBURN.address, OBURN.address, account.address, USDC.address)

    presaleOburnAmount = Web3.toWei(1000000000000000, "ether")
    USDCAmount = Web3.toWei(1000000000000, "ether")
    OBURN.transfer(oburnTokenPresale.address, presaleOburnAmount, {"from": account})
    USDC.transfer(account2.address, USDCAmount, {"from": account})

    oburnTokenPresale.lockSaleParameters({"from": account})
    oburnTokenPresale.setWhitelistSaleActive(True, {"from": account})
    oburnTokenPresale.addAddressToWhitelist(account2.address, {"from": account})

    USDC.approve(oburnTokenPresale.address, USDCAmount, {"from": account2})

    # Act / Assert
    with pytest.raises(exceptions.VirtualMachineError) as ex:
        oburnTokenPresale.buyTokens(account2.address, USDCAmount, {"from": account2})
    assert "Exceeds whitelist sale cap" in str(ex.value)    

    oburnTokenPresale.setPublicSaleActive(True, {"from": account})

    with pytest.raises(exceptions.VirtualMachineError) as ex:
        oburnTokenPresale.buyTokens(account2.address, USDCAmount, {"from": account2})
    assert "Exceeds public sale cap" in str(ex.value)    

    USDCAmount = 5000000501

    with pytest.raises(exceptions.VirtualMachineError) as ex:
        oburnTokenPresale.buyTokens(account2.address, USDCAmount, {"from": account2})
    assert "Exceeds maximum tokens per address" in str(ex.value)    

# Tests to make sure the owner cant change parameters after starting the presale.
def test_owner_cant_update_parameters_after_presale_starts():
    # Arrange
    account = get_account()
    account2 = get_account(2)
    account3 = get_account(3)

    TBURN, OBURN, USDC, _, _ = deploy_mocks()
    oburnTokenPresale, oburnExchange = deploy_presale_and_exchange(TBURN.address, OBURN.address, account.address, USDC.address)

    presaleOburnAmount = Web3.toWei(1000000000000000, "ether")
    USDCAmount = 10000000
    OBURN.transfer(oburnTokenPresale.address, presaleOburnAmount, {"from": account})
    USDC.transfer(account2.address, USDCAmount, {"from": account})
    USDC.transfer(account3.address, USDCAmount, {"from": account})

    # Act

    oburnTokenPresale.lockSaleParameters({"from": account})
    oburnTokenPresale.setWhitelistSaleActive(True, {"from": account})
    oburnTokenPresale.addAddressToWhitelist(account2.address, {"from": account})

    USDC.approve(oburnTokenPresale.address, USDCAmount, {"from": account2})
    oburnTokenPresale.buyTokens(account2.address, USDCAmount, {"from": account2})

    oburnTokenPresale.setPublicSaleActive(True, {"from": account})

    USDC.approve(oburnTokenPresale.address, USDCAmount, {"from": account3})
    oburnTokenPresale.buyTokens(account3.address, USDCAmount, {"from": account3})

    # Act / Assert
    saleRateMultAmount = 5
    whiteListSaleRate = oburnTokenPresale.getWhitelistSaleRate()
    
    with pytest.raises(exceptions.VirtualMachineError) as ex:
        oburnTokenPresale.setWhitelistSaleRate(whiteListSaleRate * saleRateMultAmount, {"from": account})
    assert "Sale parameters are locked" in str(ex.value)    

    publicSaleRate = oburnTokenPresale.getPublicSaleRate()

    with pytest.raises(exceptions.VirtualMachineError) as ex:
        oburnTokenPresale.setPublicSaleRate(publicSaleRate * saleRateMultAmount, {"from": account})
    assert "Sale parameters are locked" in str(ex.value)        

    with pytest.raises(exceptions.VirtualMachineError) as ex:
        oburnTokenPresale.setMaxOburnPerAddress(presaleOburnAmount, {"from": account})
    assert "Sale parameters are locked" in str(ex.value)    

    with pytest.raises(exceptions.VirtualMachineError) as ex:
        oburnTokenPresale.setWhitelistSaleOburnCap(presaleOburnAmount, {"from": account})
    assert "Sale parameters are locked" in str(ex.value)    

    with pytest.raises(exceptions.VirtualMachineError) as ex:
        oburnTokenPresale.setPublicSaleOburnCap(presaleOburnAmount, {"from": account})
    assert "Sale parameters are locked" in str(ex.value)                
