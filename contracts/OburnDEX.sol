// SPDX-License-Identifier: MIT

pragma solidity 0.8.13;


import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/security/Pausable.sol";
import "./oburn.sol";
import "@uniswap/v2-periphery/contracts/interfaces/IUniswapV2Router02.sol";
import "@uniswap/v2-core/contracts/interfaces/IUniswapV2Factory.sol";
// import "../interfaces/Uniswap.sol";

contract OburnDEX is Pausable, Ownable {
    // Mapping to determine which addresses are exempt from the USDC fee taken upon buys and sells in this contract.
    mapping (address => bool) private _addressesExemptFromFees;

    // Mapping to determine if an address is blacklisted from buying and selling OBURN with this contract.
    mapping (address => bool) private _blacklistedAddresses;

    // Mapping to determine the amount of USDC collected for each address.
    mapping (address => uint256) public addressToUSDCCollected;

    // Total USDC collected from all transaction fees.
    uint256 public USDCCollected = 0;

    // References the QuickSwap router for buying and selling OBURN.
    IUniswapV2Router02 public quickSwapRouter;

    // Address of the OBURN pair.
    address public quickSwapPair;

    // Token interface for OBURN.
    OnlyBurns private _oburn;

    // Token interface for USDC.
    IERC20 private _usdc;

    // Event to emit when a user is made exempt or included again in fees.
    event ExemptAddressFromFees(address indexed newAddress, bool indexed value);

    // Event to emit whenever someone is added or removed from the blacklist.
    event AddOrRemoveUserFromBlacklist(address indexed user, bool indexed blacklisted);

    // Event to emit whenever OBURN is bought with USDC.
    event oburnBuy(address indexed user, uint256 oburnAmount, uint256 usdcAmount);

    // Event to emit whenever OBURN is sold for USDC.
    event oburnSell(address indexed user, uint256 oburnAmount, uint256 usdcAmount);

    constructor(address initRouterAddress, address initOBURNPairAddress, address initOBURNAddress, address initUSDCAddress) {
        quickSwapRouter = IUniswapV2Router02(_routerAddress);
        quickSwapPair = initOBURNPairAddress;
        _oburn = OnlyBurns(initOBURNAddress);
        _usdc = IERC20(initUSDCAddress);

        _oburn.approve(initRouterAddress, type(uint256).max);
        _usdc.approve(initRouterAddress, type(uint256).max);
    }

    /**
    @dev Function to purchase OBURN with this contract - routes the transaction through QuickSwap and takes the fee out on the USDC side.
    @param amountOBURN the amount of OBURN to purchase (slippage factored in during buy) - if 0, just get as much OBURN as possible with the USDC amount supplied
    @param amountUSDC the amount of USDC to sell - if 0, sell the USDC required to get the OBURN amount specified
    @param slippage the slippage for the OBURN buy. 5% is 5, 10% is 10, etc
    */
    function purchaseOBURN(uint256 amountOBURN, uint256 amountUSDC, uint256 slippage) external {
        require(slippage < 100, "Slippage must be less than 100.");
        require(amountOBURN > 0 || amountUSDC > 0, "Either the amount of OBURN to buy or the amount of USDC to sell must be specified.");

        address[] memory path = new address[](2);
        path[0] = address(_oburn);
        path[1] = address(_usdc);

        uint256 amountUSDCNeeded = amountUSDC;
        uint256 oburnBuyFee = _oburn.buyFee();
        uint[] memory amounts = uniswapRouter.getAmountsIn(amountOBURN, path);

        if (amountUSDC == 0) {
            amountUSDCNeeded = amounts[0] * ((100 + slippage) / 100);
        }

        addressToUSDCCollected[msg.sender] == amountUSDCNeeded / oburnBuyFee;
        USDCCollected += amountUSDCNeeded / oburnBuyFee;

        _usdc.transferFrom(msg.sender, address(this), amountUSDCNeeded);

        uint256 amountUSDCAfterTax = amountUSDCNeeded * (100 - oburnBuyFee) / 100;

        if (amountUSDC > 0) {
            amounts = uniswapRouter.swapExactTokensForTokens(
                amountUSDCAfterTax,
                amountOBURN * (100 - slippage - oburnBuyFee) / 100,
                path,
                address(this),
                block.timestamp
            );
        }
        else {
            amounts = uniswapRouter.swapTokensForExactTokens(
                amountOBURN * (100 - oburnBuyFee) / 100,
                amountUSDCAfterTax,
                path,
                address(this),
                block.timestamp
            );            
        }

        _oburn.transfer(msg.sender, amounts[1]);

        if (amounts[0] < amountUSDCAfterTax) {
            _usdc.transfer(msg.sender, amountUSDCAfterTax - amounts[0]);
        }

        emit oburnBuy(msg.sender, amounts[0], amounts[1]);
    }

    /**
    @dev Function to sell OBURN with this contract - routes the transaction through QuickSwap and takes the fee out on the USDC side.
    @param amountOBURN the amount of OBURN to sell - if 0, just sell the amount of USDC supplied
    @param amountUSDC the amount of USDC to sell (slippage factored in during sell) - if 0, sell the USDC necessary to get the OBURN amount specified
    @param slippage the slippage for the OBURN sell. 5% is 5, 10% is 10, etc
    */
    function sellOBURN(uint256 amountOBURN, uint256 amountUSDC, uint256 slippage) external {
        require(slippage < 100, "Slippage must be less than 100.");
        require(amountOBURN > 0 || amountUSDC > 0, "Either the amount of OBURN to buy or the amount of USDC to sell must be specified.");

        address[] memory path = new address[](2);
        path[0] = address(_usdc);
        path[1] = address(_oburn);

        uint256 amountOBURNNeeded = amountOBURN;
        uint256 oburnSellFee = _oburn.sellFee();
        uint[] memory amounts = uniswapRouter.getAmountsIn(amountUSDC, path);

        if (amountOBURN == 0) {
            amountOBURNNeeded = amounts[0] * ((100 + slippage) / 100);
        }

        _oburn.transferFrom(msg.sender, address(this), amountOBURNNeeded);

        if (amountOBURN > 0) {
            amounts = uniswapRouter.swapExactTokensForTokens(
                amountOBURNNeeded,
                amountUSDC * (100 - slippage) / 100,
                path,
                address(this),
                block.timestamp
            );
        }
        else {
            amounts = uniswapRouter.swapTokensForExactTokens(
                amountUSDC,
                amountOBURNNeeded,
                path,
                address(this),
                block.timestamp
            );             
        }

        addressToUSDCCollected[msg.sender] == amounts[1] / oburnSellFee;
        USDCCollected += amounts[1] / oburnSellFee;    

        _usdc.transfer(msg.sender, amounts[1] * (100 - oburnSellFee) / 100);

        if (amounts[0] < amountOBURNNeeded) {
            _oburn.transfer(msg.sender, amountOBURNNeeded - amounts[0]);
        }        

        emit oburnSell(msg.sender, amounts[1], amounts[0]);
    }

    // TODO - add setter for the QuickSwap router

    /**
    @dev Only owner function to pause the exchange.
    */
    function pauseExchange() external onlyOwner {
        _pause();
    }

    /**
    @dev Only owner function to unpause the exchange.
    */
    function unpauseExchange() external onlyOwner {
        _unpause();
    }    

    /**
    @dev Only owner function to exempt or unexempt a user from trading fees.
    @param user the address that will be exempt or unexempt from fees
    @param exempt boolean to determine if the transaction is to remove or add a user to fees
    */
    function exemptAddressFromFees(address user, bool exempt) public onlyOwner {
        require(user != address(0), "Exempt user cannot be the zero address.");
        require(_addressesExemptFromFees[excludedAddress] != exempt, "Already set to this value.");

        _addressesExemptFromFees[excludedAddress] = exempt;

        emit ExemptAddressFromFees(excludedAddress, exempt);
    }

    /**
    @dev Only owner function to blacklist or unblacklist a user from trading OBURN with this contract.
    @param user the address of the user being blacklisted or unblacklisted
    @param blacklist boolean to determine if the user is going to be blacklisted or unblacklisted
    */
    function blacklistOrUnblacklistUser(address user, bool blacklist) public onlyOwner {
        require(user != address(0), "Blacklist user cannot be the zero address.");
        require(_blacklistedAddresses[user] != blacklist, "Already set to this value.");
        _blacklistedAddresses[user] = blacklist;
        emit AddOrRemoveUserFromBlacklist(user, blacklist);
    }

    /**
    @dev Getter function to return if a specified address is exempt from fees when trading OBURN with this contract.
    @param excludedAddress the address being looked up to determine if they are exempt from fees
    @return boolean which represents whether or not the specified address is exempt from fees
    */
    function getAddressExemptFromFees(address excludedAddress) public view returns (bool) {
        return _addressesExemptFromFees[excludedAddress];
    }

    /**
    @dev Getter function to return if a specified address is blacklisted from trading OBURN with this contract.
    @param blacklistedAddress the address being looked up to determine if they are blacklisted
    @return boolean which represents whether or not the specified address is blacklisted
    */
    function getAddressBlacklisted(address blacklistedAddress) public view returns (bool) {
        return _blacklistedAddresses[blacklistedAddress];
    }
}