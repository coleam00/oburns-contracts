/**
 *  SPDX-License-Identifier: MIT
 *
 *
 *  OnlyBurns (Oburn) Token Presale
 *
 *  Website -------- https://onlyburns.com
 *  Twitter -------- https://twitter.com/onlyburnsdefi
 **/

pragma solidity 0.8.13;

import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/utils/Context.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";


/**
 * @title Token presale contract for $Oburn
 * @author Parrotly Finance, Inc.
 */
contract OburnTokenPresale is ReentrancyGuard, Context, Ownable {
    // The token being sold
    IERC20 private _token;

    // USDC reference since the presale is in USDC
    IERC20 private _usdc;

    // Address where funds are collected
    address payable private _wallet;

    // Amount of USDC raised
    uint256 private _usdcRaised;

    mapping(address => bool) private _whitelistedAddresses;
    mapping(address => uint256) private _whitelistAddressSpend;
    mapping(address => uint256) private _OburnPurchased;
    bool private _saleParametersLocked = false;
    bool private _whitelistSaleActive = false;
    bool private _publicSaleActive = false;
    bool private _whitelistSaleStarted = false;
    bool private _whitelistSaleEnded = false;
    uint256 private _whitelistSaleOburnSold;
    uint256 private _publicSaleOburnSold;
    uint256 private _whitelistSaleOburnCap = 25000000000 ether; // max Oburn available (WL)
    uint256 private _whitelistSaleRate = 500000 * (10 ** 12); // Oburn per the smallest amount of USDC ($0.000001) (WL)
    uint256 private _publicSaleOburnCap = 130000000000 ether; // max Oburn available (public)
    uint256 private _publicSaleRate = 250000 * (10 ** 12); // Oburn per the smallest amount of USDC ($0.000001) (public)
    uint256 private _maxOburnPerAddress = 1250000000 ether; // max Oburn spend per adddress

    /**
     * Event for token purchase logging
     * @param purchaser who paid for the tokens
     * @param beneficiary who got the tokens
     * @param value usdc paid for purchase
     * @param amount amount of tokens purchased
     */
    event TokensPurchased(address indexed purchaser, address indexed beneficiary, uint256 value, uint256 amount);

    /**
     * @param preSaleWallet Address where collected funds will be forwarded to
     * @param preSaleToken Address of the token being sold
     * @param usdc Address of the USDC token which will be used to purchase OBurn in the presale
     */
    constructor(
        address payable preSaleWallet,
        IERC20 preSaleToken,
        IERC20 usdc
    ) {
        require(preSaleWallet != address(0), "Wallet is the zero address");
        require(address(preSaleToken) != address(0), "Token is the zero address");
        _wallet = preSaleWallet;
        _token = preSaleToken;
        _usdc = usdc;
    }

    /**
     * @dev Throws if sale parameters are locked
     */
    modifier onlyWhenUnlocked() {
        require(_saleParametersLocked == false, "Sale parameters are locked");
        _;
    }

    /**
     @dev Internal function to validate the presale purchase.
     @param beneficiary the address of the user receiving tokens from the presale purchase
     @param usdcAmount the amount of USDC sent in for the presale purchase
     */
    function _preValidatePurchase(address beneficiary, uint256 usdcAmount) internal view {
        require(beneficiary != address(0), "Beneficiary is the zero address");
        require(usdcAmount != 0, "usdcAmount is 0");
        require(_usdc.allowance(_msgSender(), address(this)) >= usdcAmount, "Sender hasn't allowed this contract to spend enough USDC for this presale purchase.");
        require(_saleParametersLocked, "Sale parameters are not locked");
        require(_whitelistSaleActive || _publicSaleActive, "Whitelist sale and public sale are both not active");
        require(_msgSender() == beneficiary, "Sender address must also be the beneficiary address");

        if (_whitelistSaleActive) {
            _validateWhitelistSale(beneficiary, usdcAmount);
        } else {
            _validatePublicSale(beneficiary, usdcAmount);
        }
    }

    /**
     * @dev Validation specific to the whitelist portion of the sale
     * @param beneficiary address receiving the OBURN
     * @param usdcAmount Value in USDC involved in the purchase
     */
    function _validateWhitelistSale(address beneficiary, uint256 usdcAmount) internal view {
        require(checkAddressWhitelisted(beneficiary), "Beneficiary address is not whitelisted");

        uint256 tokens = _getTokenAmount(usdcAmount);

        require(_whitelistSaleOburnSold + tokens <= _whitelistSaleOburnCap, "Exceeds whitelist sale cap");
        require(_OburnPurchased[beneficiary] + tokens <= _maxOburnPerAddress, "Exceeds maximum tokens per address");
    }

    /**
     * @dev Validation specific to the public portion of the sale
     * @param beneficiary address receiving the OBURN
     * @param usdcAmount Value in USDC involved in the purchase
     */
    function _validatePublicSale(address beneficiary, uint256 usdcAmount) internal view {
        uint256 tokens = _getTokenAmount(usdcAmount);

        require(_publicSaleOburnSold + tokens <= _publicSaleOburnCap, "Exceeds public sale cap");
        require(_OburnPurchased[beneficiary] + tokens <= _maxOburnPerAddress, "Exceeds maximum tokens per address");
    }

    /**
    @dev Internal function to compute the amount of OBURN the beneficiary will receive based on the amount of USDC sent in.
    @param usdcAmount the amount of USDC sent in for the presale purchase.
     */
    function _getTokenAmount(uint256 usdcAmount) internal view returns (uint256) {
        if (_whitelistSaleActive) {
            return usdcAmount * _whitelistSaleRate;
        }

        return usdcAmount * _publicSaleRate;
    }

    /**
    @dev External function to compute how many tokens someone would get if they sent in usdcAmount USDC.
    @param usdcAmount the amount of USDC to use when computing the OBURN amount
     */
    function getTokenAmount(uint256 usdcAmount) external view returns (uint256) {
        return _getTokenAmount(usdcAmount);
    }

    /**
    @dev Internal function to update the presale state (OBURN purchased, public ORBURN sold, whitelist OBURN sold, etc.)
    @param beneficiary the address of the user receiving OBURN for the presale purchase
    @param usdcAmount the amount of USDC sent in for the presale purchase
     */
    function _updatePurchasingState(address beneficiary, uint256 usdcAmount) internal {
        uint256 tokens = _getTokenAmount(usdcAmount);
        if (_whitelistSaleActive) {
            _OburnPurchased[beneficiary] += tokens;
            _whitelistSaleOburnSold += tokens;
        } else {
            _OburnPurchased[beneficiary] += tokens;
            _publicSaleOburnSold += tokens;
        }
    }

    /**
     * @dev Function for purchasing tokens in the presale.
     * This function has a non-reentrancy guard, so it shouldn't be called by
     * another `nonReentrant` function.
     * @param beneficiary Recipient of the token purchase
     */
    function buyTokens(address beneficiary, uint256 usdcAmount) external nonReentrant {
        _preValidatePurchase(beneficiary, usdcAmount);

        // calculate token amount to be sent
        uint256 tokens = _getTokenAmount(usdcAmount);

        // update state
        _usdcRaised = _usdcRaised + usdcAmount;

        _processPurchase(beneficiary, tokens, usdcAmount);

        emit TokensPurchased(_msgSender(), beneficiary, usdcAmount, tokens);

        _updatePurchasingState(beneficiary, usdcAmount);
    }

    /**
     * @dev Executed when a purchase has been validated and is ready to be executed. Doesn't necessarily emit/send
     * tokens.
     * @param beneficiary Address receiving the tokens
     * @param tokenAmount Number of tokens to be purchased
     * @param usdcAmount the amount of USDC spent on the presale purchase
     */
    function _processPurchase(address beneficiary, uint256 tokenAmount, uint256 usdcAmount) internal {
        _usdc.transferFrom(_msgSender(), _wallet, usdcAmount);
        _token.transfer(beneficiary, tokenAmount);
    }     

    /**
     * @dev onlyOwner
     * Send remaining Oburn back to the owner
     */
    function endSale() external onlyOwner {
        require(_publicSaleActive, "Public sale has not started");
        _publicSaleActive = false;
        uint256 balance = _token.balanceOf(address(this));
        _token.transfer(owner(), balance);
    }

    /**
     * Getters & Setters
     */
    function getWhitelistSaleOburnSold() external view returns (uint256) {
        return _whitelistSaleOburnSold;
    }

    function getPublicSaleOburnSold() external view returns (uint256) {
        return _publicSaleOburnSold;
    }

    function getWhitelistSaleOburnCap() external view returns (uint256) {
        return _whitelistSaleOburnCap;
    }

    /**
     * @return the token being sold.
     */
    function token() external view returns (IERC20) {
        return _token;
    }

    /**
     * @return the address where funds are collected.
     */
    function wallet() external view returns (address payable) {
        return _wallet;
    }

    /**
     * @return the amount of USDC raised.
     */
    function usdcRaised() external view returns (uint256) {
        return _usdcRaised;
    }

    /**
     * @dev onlyOwner and onlyWhenUnlocked
     */
    function setWhitelistSaleOburnCap(uint256 cap) external onlyOwner onlyWhenUnlocked {
        _whitelistSaleOburnCap = cap;
    }

    function getPublicSaleOburnCap() external view returns (uint256) {
        return _publicSaleOburnCap;
    }

    /**
     * @dev onlyOwner and onlyWhenUnlocked
     */
    function setPublicSaleOburnCap(uint256 cap) external onlyOwner onlyWhenUnlocked {
        _publicSaleOburnCap = cap;
    }

    function getWhitelistSaleRate() external view returns (uint256) {
        return _whitelistSaleRate;
    }

    /**
     * @dev onlyOwner and onlyWhenUnlocked
     */
    function setWhitelistSaleRate(uint256 rate) external onlyOwner onlyWhenUnlocked {
        _whitelistSaleRate = rate;
    }

    function getPublicSaleRate() external view returns (uint256) {
        return _publicSaleRate;
    }

    /**
     * @dev onlyOwner and onlyWhenUnlocked
     */
    function setPublicSaleRate(uint256 rate) external onlyOwner onlyWhenUnlocked {
        _publicSaleRate = rate;
    }

    function getMaxOburnPerAddress() external view returns (uint256) {
        return _maxOburnPerAddress;
    }

    /**
     * @dev onlyOwner and onlyWhenUnlocked
     */
    function setMaxOburnPerAddress(uint256 amount) external onlyOwner onlyWhenUnlocked {
        _maxOburnPerAddress = amount;
    }

    function getSaleParametersLocked() external view returns (bool) {
        return _saleParametersLocked;
    }

    /**
     * @dev onlyOwner
     * Parameters cannot be unlocked
     */
    function lockSaleParameters() external onlyOwner {
        _saleParametersLocked = true;
    }

    function getWhitelistSaleActive() external view returns (bool) {
        return _whitelistSaleActive;
    }

    /**
     * @dev onlyOwner
     */
    function setWhitelistSaleActive(bool active) external onlyOwner {
        require(_saleParametersLocked, "Sale parameters are not locked");
        require(!_whitelistSaleEnded, "Whitelist sale has ended");

        _whitelistSaleActive = active;
        if (_whitelistSaleActive && !_whitelistSaleStarted) {
            _whitelistSaleStarted = true;
        }
    }

    function getPublicSaleActive() external view returns (bool) {
        return _publicSaleActive;
    }

    /**
     * @dev onlyOwner
     */
    function setPublicSaleActive(bool active) external onlyOwner {
        require(_saleParametersLocked, "Sale parameters are not locked");
        require(_whitelistSaleStarted, "Whitelist sale has not started");

        _publicSaleActive = active;
        if (_publicSaleActive && !_whitelistSaleEnded) {
            endWhitelistSale();
            transferWhitelistSaleTokensToPublicSaleCap();
            adjustMaxOburnPerAddress();
        }
    }

    /**
     * @dev Set whitelist sale state according to the end of the whitelist sale
     */
    function endWhitelistSale() private {
        _whitelistSaleActive = false;
        _whitelistSaleEnded = true;
    }

    /**
     * @dev Any unsold whitelist sale tokens will be made available in the public sale
     */
    function transferWhitelistSaleTokensToPublicSaleCap() private {
        _publicSaleOburnCap += (_whitelistSaleOburnCap - _whitelistSaleOburnSold);
    }

    /**
     * @dev Adjust the max Oburn per address to play nice with the rounded rate
     */
    function adjustMaxOburnPerAddress() private {
        _maxOburnPerAddress = 1250000125 ether;
    }

    /**
     * @dev onlyOwner
     */
    function addAddressToWhitelist(address user) external onlyOwner {
        _whitelistedAddresses[user] = true;
    }

    /**
     * @dev onlyOwner
     */
    function addAddressesToWhitelist(address[] calldata users) external onlyOwner {
        for (uint256 i; i < users.length; i++) {
            _whitelistedAddresses[users[i]] = true;
        }
    }

    /**
     * @dev onlyOwner
     */
    function removeAddressFromWhitelist(address user) external onlyOwner {
        _whitelistedAddresses[user] = false;
    }

    /**
     * @dev onlyOwner
     */
    function isAddressWhitelisted(address user) external view onlyOwner returns (bool) {
        return checkAddressWhitelisted(user);
    }

    function singleAddressCheckWhitelist() external view returns (bool) {
        return _whitelistedAddresses[_msgSender()];
    }

    function singleAddressCheckOburnAmountPurchased() external view returns (uint256) {
        return _OburnPurchased[_msgSender()];
    }

    function singleAddressCheckOburnAmountAvailable() external view returns (uint256) {
        return _maxOburnPerAddress - _OburnPurchased[_msgSender()];
    }

    function checkAddressWhitelisted(address user) private view returns (bool) {
        return _whitelistedAddresses[user];
    }
}