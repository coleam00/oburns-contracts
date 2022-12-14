from scripts.helpers import get_account
from brownie import network, accounts, exceptions, chain, BurnSwap, MockToken
from brownie.network.contract import Contract, InterfaceContainer
from web3 import Web3
import pytest
import time

BURNSWAP_ADDRESS_TEST = "0xb14ebE9405B76509cF0b67B6340f5287f7d53F4E"
MOCK_USDC_ADDRESS_TEST = "0x7f8754f9cc58a8ffa69c755ae425e84b55bb3a0d"
MOCK_OBURN_ADDRESS_TEST = "0x90a603fa876980b38cb6415c0328aeec6c33c3f4"
ROUTER_ADDRESS_TEST = "0x9Ac64Cc6e4415144C455BD8E4837Fea55603e5c3"
DEAD_WALLET = "0x000000000000000000000000000000000000dEaD"

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Buy Tests ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ 

# Tests to make sure users can buy OBURN with USDC with the Burn Swap contract.
def test_user_can_buy_oburn(interface):
    # Arrange
    account = get_account()
    
    burnSwapABI = BurnSwap.abi
    burnSwap = Contract.from_abi("BurnSwap", BURNSWAP_ADDRESS_TEST, burnSwapABI)

    tokenABI = MockToken.abi
    usdc = Contract.from_abi("MockToken", MOCK_USDC_ADDRESS_TEST, tokenABI)
    oburn = Contract.from_abi("MockToken", MOCK_OBURN_ADDRESS_TEST, tokenABI)

    quickswapRouter = interface.IUniswapV2Router02(ROUTER_ADDRESS_TEST)

    # Act
    amountUSDCIn = 1000
    slippage = 5
    initialUSDCBalance = usdc.balanceOf(account.address)
    initialBurnSwapUSDCBalance = usdc.balanceOf(burnSwap.address)
    initialOBURNBalance = oburn.balanceOf(account.address)
    buyFee = oburn.buyFee()

    amounts = quickswapRouter.getAmountsOut(amountUSDCIn, [usdc, oburn])
    amountOBURNOut = amounts[1]

    usdc.approve(BURNSWAP_ADDRESS_TEST, amountUSDCIn, {"from": account})
    burnSwap.purchaseOBURN(amountOBURNOut, amountUSDCIn, slippage, {"from": account})

    # Assert
    assert usdc.balanceOf(account.address) == initialUSDCBalance - amountUSDCIn

    newOBURNBalance = oburn.balanceOf(account.address)
    assert oburn.balanceOf(account.address) >= initialOBURNBalance + amountOBURNOut * ((100 - slippage - buyFee) / 100)
    assert oburn.balanceOf(account.address) <= initialOBURNBalance + amountOBURNOut * ((100 - buyFee) / 100) + 1

    initialUSDCBalance = usdc.balanceOf(account.address)
    burnSwapUSDCBalance = usdc.balanceOf(burnSwap.address)

    assert burnSwapUSDCBalance == initialBurnSwapUSDCBalance + (amountUSDCIn * buyFee / 100)

    burnSwap.withdrawUSDC({"from": account})

    assert usdc.balanceOf(account.address) == initialUSDCBalance + burnSwapUSDCBalance

# Tests to make sure users can buy OBURN with USDC with the Burn Swap contract when only specifying USDC amount
def test_user_can_buy_oburn_only_specify_usdc(interface):
    # Arrange
    account = get_account()
    
    burnSwapABI = BurnSwap.abi
    burnSwap = Contract.from_abi("BurnSwap", BURNSWAP_ADDRESS_TEST, burnSwapABI)

    tokenABI = MockToken.abi
    usdc = Contract.from_abi("MockToken", MOCK_USDC_ADDRESS_TEST, tokenABI)
    oburn = Contract.from_abi("MockToken", MOCK_OBURN_ADDRESS_TEST, tokenABI)

    quickswapRouter = interface.IUniswapV2Router02(ROUTER_ADDRESS_TEST)

    # Act
    amountUSDCIn = 1000
    slippage = 5
    initialUSDCBalance = usdc.balanceOf(account.address)
    initialOBURNBalance = oburn.balanceOf(account.address)
    buyFee = oburn.buyFee()

    amounts = quickswapRouter.getAmountsOut(amountUSDCIn, [usdc, oburn])
    amountOBURNOut = amounts[1]

    usdc.approve(BURNSWAP_ADDRESS_TEST, amountUSDCIn, {"from": account})
    burnSwap.purchaseOBURN(0, amountUSDCIn, slippage, {"from": account})

    # Assert
    assert usdc.balanceOf(account.address) == initialUSDCBalance - amountUSDCIn

    newOBURNBalance = oburn.balanceOf(account.address)
    assert oburn.balanceOf(account.address) >= initialOBURNBalance + amountOBURNOut * ((100 - slippage - buyFee) / 100)
    assert oburn.balanceOf(account.address) <= initialOBURNBalance + amountOBURNOut * ((100 - buyFee) / 100) + 1

# Tests to make sure users can buy OBURN with USDC with the Burn Swap contract when only specifying OBURN output amount
def test_user_can_buy_oburn_only_specify_oburn(interface):
    # Arrange
    account = get_account()
    
    burnSwapABI = BurnSwap.abi
    burnSwap = Contract.from_abi("BurnSwap", BURNSWAP_ADDRESS_TEST, burnSwapABI)

    tokenABI = MockToken.abi
    usdc = Contract.from_abi("MockToken", MOCK_USDC_ADDRESS_TEST, tokenABI)
    oburn = Contract.from_abi("MockToken", MOCK_OBURN_ADDRESS_TEST, tokenABI)

    quickswapRouter = interface.IUniswapV2Router02(ROUTER_ADDRESS_TEST)

    # Act
    amountUSDCIn = 1000
    slippage = 5
    initialUSDCBalance = usdc.balanceOf(account.address)
    initialOBURNBalance = oburn.balanceOf(account.address)
    buyFee = oburn.buyFee()

    amounts = quickswapRouter.getAmountsOut(amountUSDCIn, [usdc, oburn])
    amountOBURNOut = amounts[1]

    usdc.approve(BURNSWAP_ADDRESS_TEST, amountUSDCIn * ((100 + slippage) / 100), {"from": account})
    burnSwap.purchaseOBURN(amountOBURNOut, 0, slippage, {"from": account})

    # Assert
    assert oburn.balanceOf(account.address) == initialOBURNBalance + amountOBURNOut * ((100 - buyFee) / 100)

    assert usdc.balanceOf(account.address) >= initialUSDCBalance - amountUSDCIn * ((100 + slippage) / 100)
    assert usdc.balanceOf(account.address) <= initialUSDCBalance - (amountUSDCIn * 0.99)

# Tests to make sure users can buy OBURN with USDC with the Burn Swap contract and they aren't taxed when excluded from fees.
def test_user_can_buy_oburn_no_fee(interface):
    # Arrange
    account = get_account()
    
    burnSwapABI = BurnSwap.abi
    burnSwap = Contract.from_abi("BurnSwap", BURNSWAP_ADDRESS_TEST, burnSwapABI)

    tokenABI = MockToken.abi
    usdc = Contract.from_abi("MockToken", MOCK_USDC_ADDRESS_TEST, tokenABI)
    oburn = Contract.from_abi("MockToken", MOCK_OBURN_ADDRESS_TEST, tokenABI)

    quickswapRouter = interface.IUniswapV2Router02(ROUTER_ADDRESS_TEST)

    # Act
    amountUSDCIn = 1000
    slippage = 5
    initialUSDCBalance = usdc.balanceOf(account.address)
    initialOBURNBalance = oburn.balanceOf(account.address)
    buyFee = oburn.buyFee()

    amounts = quickswapRouter.getAmountsOut(amountUSDCIn, [usdc, oburn])
    amountOBURNOut = amounts[1]

    usdc.approve(BURNSWAP_ADDRESS_TEST, amountUSDCIn, {"from": account})
    burnSwap.exemptAddressFromFees(account.address, True, {"from": account})
    burnSwap.purchaseOBURN(amountOBURNOut, amountUSDCIn, slippage, {"from": account})
    burnSwap.exemptAddressFromFees(account.address, False, {"from": account})

    # Assert
    assert usdc.balanceOf(account.address) == initialUSDCBalance - amountUSDCIn

    newOBURNBalance = oburn.balanceOf(account.address)
    assert oburn.balanceOf(account.address) >= initialOBURNBalance + amountOBURNOut * ((100 - slippage) / 100)
    assert oburn.balanceOf(account.address) <= initialOBURNBalance + amountOBURNOut + 1 

# Tests to make sure users can NOT buy OBURN with USDC with the Burn Swap contract under certain scenarios such as a blacklist or trading paused.
def test_user_can_not_buy_oburn_certain_scenarios(interface):
    # Arrange
    account = get_account()
    
    burnSwapABI = BurnSwap.abi
    burnSwap = Contract.from_abi("BurnSwap", BURNSWAP_ADDRESS_TEST, burnSwapABI)

    tokenABI = MockToken.abi
    usdc = Contract.from_abi("MockToken", MOCK_USDC_ADDRESS_TEST, tokenABI)
    oburn = Contract.from_abi("MockToken", MOCK_OBURN_ADDRESS_TEST, tokenABI)

    quickswapRouter = interface.IUniswapV2Router02(ROUTER_ADDRESS_TEST)

    # Act / Assert
    amountUSDCIn = 1000
    slippage = 5
    initialUSDCBalance = usdc.balanceOf(account.address)
    initialBurnSwapUSDCBalance = usdc.balanceOf(burnSwap.address)
    initialOBURNBalance = oburn.balanceOf(account.address)
    buyFee = oburn.buyFee()

    amounts = quickswapRouter.getAmountsOut(amountUSDCIn, [usdc, oburn])
    amountOBURNOut = amounts[1]

    usdc.approve(BURNSWAP_ADDRESS_TEST, amountUSDCIn, {"from": account})

    burnSwap.pauseExchange({"from": account})

    with pytest.raises(ValueError) as ex:
        burnSwap.purchaseOBURN(amountOBURNOut, amountUSDCIn, slippage, {"from": account})
    assert "Pausable: paused" in str(ex.value)  

    burnSwap.unpauseExchange({"from": account})

    burnSwap.blacklistOrUnblacklistUser(account.address, True, {"from": account})   

    with pytest.raises(ValueError) as ex:
        burnSwap.purchaseOBURN(amountOBURNOut, amountUSDCIn, slippage, {"from": account})
    assert "You have been blacklisted from trading OBURN through this contract." in str(ex.value)  

    burnSwap.blacklistOrUnblacklistUser(account.address, False, {"from": account})  

    usdc.approve(BURNSWAP_ADDRESS_TEST, 0, {"from": account}) 

    with pytest.raises(ValueError) as ex:
        burnSwap.purchaseOBURN(amountOBURNOut, amountUSDCIn, slippage, {"from": account})
    assert "ERC20: insufficient allowance" in str(ex.value)      











# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ Sell Tests ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ 

# Tests to make sure users can sell OBURN for USDC with the Burn Swap contract.
def test_user_can_sell_oburn(interface):
    # Arrange
    account = get_account()
    
    burnSwapABI = BurnSwap.abi
    burnSwap = Contract.from_abi("BurnSwap", BURNSWAP_ADDRESS_TEST, burnSwapABI)

    tokenABI = MockToken.abi
    usdc = Contract.from_abi("MockToken", MOCK_USDC_ADDRESS_TEST, tokenABI)
    oburn = Contract.from_abi("MockToken", MOCK_OBURN_ADDRESS_TEST, tokenABI)

    quickswapRouter = interface.IUniswapV2Router02(ROUTER_ADDRESS_TEST)

    # Act
    amountOBURNIn = 1000
    slippage = 5
    initialUSDCBalance = usdc.balanceOf(account.address)
    initialOBURNBalance = oburn.balanceOf(account.address)
    sellFee = oburn.sellFee()

    amounts = quickswapRouter.getAmountsOut(amountOBURNIn, [oburn, usdc])
    amountUSDCOut = amounts[1]

    initialOBURNBurnt = burnSwap.OBURNBurnt()
    initialDeadWalletOBURNBalance = oburn.balanceOf(DEAD_WALLET)
    oburn.approve(BURNSWAP_ADDRESS_TEST, amountOBURNIn, {"from": account})
    burnSwap.sellOBURN(amountOBURNIn, amountUSDCOut, slippage, {"from": account})

    # Assert
    assert oburn.balanceOf(account.address) == initialOBURNBalance - amountOBURNIn
    assert burnSwap.OBURNBurnt() == initialOBURNBurnt + (amountOBURNIn * sellFee / 100)
    assert oburn.balanceOf(DEAD_WALLET) == initialDeadWalletOBURNBalance + amountOBURNIn * (sellFee / 100)

    assert usdc.balanceOf(account.address) >= initialUSDCBalance + amountUSDCOut * ((100 - slippage - sellFee) / 100)
    assert usdc.balanceOf(account.address) <= initialUSDCBalance + amountUSDCOut * ((100 - sellFee) / 100) + 1

# Tests to make sure users can sell OBURN for USDC with the Burn Swap contract.
def test_user_can_sell_oburn_only_specify_oburn(interface):
    # Arrange
    account = get_account()
    
    burnSwapABI = BurnSwap.abi
    burnSwap = Contract.from_abi("BurnSwap", BURNSWAP_ADDRESS_TEST, burnSwapABI)

    tokenABI = MockToken.abi
    usdc = Contract.from_abi("MockToken", MOCK_USDC_ADDRESS_TEST, tokenABI)
    oburn = Contract.from_abi("MockToken", MOCK_OBURN_ADDRESS_TEST, tokenABI)

    quickswapRouter = interface.IUniswapV2Router02(ROUTER_ADDRESS_TEST)

    # Act
    amountOBURNIn = 1000
    slippage = 5
    initialUSDCBalance = usdc.balanceOf(account.address)
    initialOBURNBalance = oburn.balanceOf(account.address)
    sellFee = oburn.sellFee()

    amounts = quickswapRouter.getAmountsOut(amountOBURNIn, [oburn, usdc])
    amountUSDCOut = amounts[1]

    initialOBURNBurnt = burnSwap.OBURNBurnt()
    initialDeadWalletOBURNBalance = oburn.balanceOf(DEAD_WALLET)
    oburn.approve(BURNSWAP_ADDRESS_TEST, amountOBURNIn, {"from": account})
    burnSwap.sellOBURN(amountOBURNIn, 0, slippage, {"from": account})

    # Assert
    assert oburn.balanceOf(account.address) == initialOBURNBalance - amountOBURNIn
    assert burnSwap.OBURNBurnt() == initialOBURNBurnt + (amountOBURNIn * sellFee / 100)
    assert oburn.balanceOf(DEAD_WALLET) == initialDeadWalletOBURNBalance + amountOBURNIn * (sellFee / 100)

    assert usdc.balanceOf(account.address) >= initialUSDCBalance + amountUSDCOut * ((100 - slippage - sellFee) / 100)
    assert usdc.balanceOf(account.address) <= initialUSDCBalance + amountUSDCOut * ((100 - sellFee) / 100) + 1

# Tests to make sure users can sell OBURN for USDC with the Burn Swap contract and only specifying USDC.
def test_user_can_sell_oburn_only_specify_usdc(interface):
    # Arrange
    account = get_account()
    
    burnSwapABI = BurnSwap.abi
    burnSwap = Contract.from_abi("BurnSwap", BURNSWAP_ADDRESS_TEST, burnSwapABI)

    tokenABI = MockToken.abi
    usdc = Contract.from_abi("MockToken", MOCK_USDC_ADDRESS_TEST, tokenABI)
    oburn = Contract.from_abi("MockToken", MOCK_OBURN_ADDRESS_TEST, tokenABI)

    quickswapRouter = interface.IUniswapV2Router02(ROUTER_ADDRESS_TEST)

    # Act
    amountOBURNIn = 1000
    slippage = 5
    initialUSDCBalance = usdc.balanceOf(account.address)
    initialOBURNBalance = oburn.balanceOf(account.address)
    sellFee = oburn.sellFee()

    amounts = quickswapRouter.getAmountsOut(amountOBURNIn, [oburn, usdc])
    amountUSDCOut = amounts[1]

    initialOBURNBurnt = burnSwap.OBURNBurnt()
    initialDeadWalletOBURNBalance = oburn.balanceOf(DEAD_WALLET)
    oburn.approve(BURNSWAP_ADDRESS_TEST, amountOBURNIn * ((100 + slippage) / 100), {"from": account})
    burnSwap.sellOBURN(0, amountUSDCOut, slippage, {"from": account})

    # Assert
    assert usdc.balanceOf(account.address) == initialUSDCBalance + amountUSDCOut * ((100 - sellFee) / 100)
    assert burnSwap.OBURNBurnt() == initialOBURNBurnt + (amountOBURNIn * sellFee / 100)
    assert oburn.balanceOf(DEAD_WALLET) == initialDeadWalletOBURNBalance + amountOBURNIn * (sellFee / 100)

    assert oburn.balanceOf(account.address) >= initialOBURNBalance - amountOBURNIn * ((100 + slippage) / 100)
    assert oburn.balanceOf(account.address) <= initialOBURNBalance - (amountOBURNIn * 0.99)

# Tests to make sure users can sell OBURN for USDC with the Burn Swap contract and have no fee taken when excluded from fees.
def test_user_can_sell_oburn_no_fee(interface):
    # Arrange
    account = get_account()
    
    burnSwapABI = BurnSwap.abi
    burnSwap = Contract.from_abi("BurnSwap", BURNSWAP_ADDRESS_TEST, burnSwapABI)

    tokenABI = MockToken.abi
    usdc = Contract.from_abi("MockToken", MOCK_USDC_ADDRESS_TEST, tokenABI)
    oburn = Contract.from_abi("MockToken", MOCK_OBURN_ADDRESS_TEST, tokenABI)

    quickswapRouter = interface.IUniswapV2Router02(ROUTER_ADDRESS_TEST)

    # Act
    amountOBURNIn = 1000
    slippage = 5
    initialUSDCBalance = usdc.balanceOf(account.address)
    initialOBURNBalance = oburn.balanceOf(account.address)
    sellFee = oburn.sellFee()

    amounts = quickswapRouter.getAmountsOut(amountOBURNIn, [oburn, usdc])
    amountUSDCOut = amounts[1]

    initialOBURNBurnt = burnSwap.OBURNBurnt()
    initialDeadWalletOBURNBalance = oburn.balanceOf(DEAD_WALLET)
    oburn.approve(BURNSWAP_ADDRESS_TEST, amountOBURNIn, {"from": account})
    burnSwap.exemptAddressFromFees(account.address, True, {"from": account})
    burnSwap.sellOBURN(amountOBURNIn, amountUSDCOut, slippage, {"from": account})
    burnSwap.exemptAddressFromFees(account.address, False, {"from": account})

    # Assert
    assert oburn.balanceOf(account.address) == initialOBURNBalance - amountOBURNIn
    assert burnSwap.OBURNBurnt() == initialOBURNBurnt
    assert oburn.balanceOf(DEAD_WALLET) == initialDeadWalletOBURNBalance

    assert usdc.balanceOf(account.address) >= initialUSDCBalance + amountUSDCOut * ((100 - slippage) / 100)
    assert usdc.balanceOf(account.address) <= initialUSDCBalance + amountUSDCOut + 1    

# Tests to make sure users can not sell OBURN for USDC with the Burn Swap contract under certain scenarios such as a blacklist or paused exchange.
def test_user_can_not_sell_oburn_certain_scenarios(interface):
    # Arrange
    account = get_account()
    
    burnSwapABI = BurnSwap.abi
    burnSwap = Contract.from_abi("BurnSwap", BURNSWAP_ADDRESS_TEST, burnSwapABI)

    tokenABI = MockToken.abi
    usdc = Contract.from_abi("MockToken", MOCK_USDC_ADDRESS_TEST, tokenABI)
    oburn = Contract.from_abi("MockToken", MOCK_OBURN_ADDRESS_TEST, tokenABI)

    quickswapRouter = interface.IUniswapV2Router02(ROUTER_ADDRESS_TEST)

    # Act / Assert
    amountOBURNIn = 1000
    slippage = 5
    initialUSDCBalance = usdc.balanceOf(account.address)
    initialOBURNBalance = oburn.balanceOf(account.address)
    sellFee = oburn.sellFee()

    amounts = quickswapRouter.getAmountsOut(amountOBURNIn, [oburn, usdc])
    amountUSDCOut = amounts[1]

    initialOBURNBurnt = burnSwap.OBURNBurnt()
    initialDeadWalletOBURNBalance = oburn.balanceOf(DEAD_WALLET)
    oburn.approve(BURNSWAP_ADDRESS_TEST, amountOBURNIn, {"from": account})

    burnSwap.pauseExchange({"from": account})

    with pytest.raises(ValueError) as ex:
        burnSwap.sellOBURN(amountOBURNIn, amountUSDCOut, slippage, {"from": account})
    assert "Pausable: paused" in str(ex.value)  

    burnSwap.unpauseExchange({"from": account})

    burnSwap.blacklistOrUnblacklistUser(account.address, True, {"from": account})   

    with pytest.raises(ValueError) as ex:
        burnSwap.sellOBURN(amountOBURNIn, amountUSDCOut, slippage, {"from": account})
    assert "You have been blacklisted from trading OBURN through this contract." in str(ex.value)  

    burnSwap.blacklistOrUnblacklistUser(account.address, False, {"from": account})  

    oburn.approve(BURNSWAP_ADDRESS_TEST, 0, {"from": account}) 

    with pytest.raises(ValueError) as ex:
        burnSwap.sellOBURN(amountOBURNIn, amountUSDCOut, slippage, {"from": account})
    assert "ERC20: insufficient allowance" in str(ex.value)          
    