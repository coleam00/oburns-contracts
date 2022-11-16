// SPDX-License-Identifier: MIT

pragma solidity 0.8.13;

import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/security/Pausable.sol";

/**
 * @title TBURN to OBURN token exchange contract.
 */
contract OburnExchange is Pausable, Ownable {
    // TBURN token reference - this is the token users will be sending in to exchange 1:1 for OBURN.
    IERC20 public _tburn;

    // OBURN token reference - this is the token users will get 1:1 for the TBURN they send in.
    IERC20 public _oburn;

    // Event to emit whenever someone exchanges TBURN for OBURN.
    event TBURNExchanged(address indexed user, uint256 exchangeAmount);

    // Event to emit whenever tokens are withdraw from the contract.
    event tokensWithdraw(address indexed tokenAddress, uint256 tokenAmount);

    constructor(IERC20 tburn, IERC20 oburn) {
        _tburn = tburn;
        _oburn = oburn;
    }

    /**
    @dev Function for exchanging TBURN for OBURN 1:1. This functionality can be paused.
    @param tburnAmount the amount of TBURN to exchange for OBURN.
    */
    function OBURNExchange(uint256 tburnAmount) external whenNotPaused {
        require(_tburn.balanceOf(msg.sender) >= tburnAmount, "You don't have enough TBURN to perform this exchange.");
        require(_tburn.allowance(msg.sender, address(this)) >= tburnAmount, "You must first approve this contract to spend your TBURN to exchange it for OBURN.");
        require(_oburn.balanceOf(address(this)) >= tburnAmount, "This contract doesn't have enough OBURN to perform this exchange.");

        _tburn.transferFrom(msg.sender, address(this), tburnAmount);
        _oburn.transfer(msg.sender, tburnAmount);

        emit TBURNExchanged(msg.sender, tburnAmount);
    }

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
    @dev Private function for withdrawing tokens.
    @param token the token being withdrawn to the owner
    @param amount the amount of the token to withdraw to the owner
    */
    function withdrawTokens(IERC20 token, uint256 amount) private {
        token.transfer(owner(), amount);
        emit tokensWithdraw(address(token), amount);
    }

    /**
    @dev Only owner function to withdraw all tburn from the contract.
    */
    function withdrawAllTBURN() external onlyOwner {
        withdrawTokens(_tburn, _tburn.balanceOf(address(this)));
    }

    /**
    @dev Only owner function to withdraw all oburn from the contract.
    */
    function withdrawAllOBURN() external onlyOwner {
        withdrawTokens(_oburn, _oburn.balanceOf(address(this)));
    }

    /**
    @dev Only owner function to withdraw a specific amount of TBURN from the contract (in wei).
    @param tburnAmount the amount of TBURN to withdraw from the contract.
    */
    function withdrawSpecifiedTBURN(uint256 tburnAmount) external onlyOwner {
        withdrawTokens(_tburn, tburnAmount);
    }

    /**
    @dev Only owner function to withdraw a specific amount of OBURN from the contract (in wei).
    @param oburnAmount the amount of OBURN to withdraw from the contract.
    */
    function withdrawSpecifiedOBURN(uint256 oburnAmount) external onlyOwner {
        withdrawTokens(_oburn, oburnAmount);
    }

    /**
    @dev Only ower function to rescue any funds in the contract that someone might have sent on accident - accepts an amount to withdraw.
    @param tokenAddress the address of the token being rescued
    @param rescueAmount the amount of tokens to withdraw for the rescue
    */
    function rescueFundsWithAmount(address tokenAddress, uint256 rescueAmount) external onlyOwner {
        require(tokenAddress != address(0), "Token address cannot be the 0 address.");
        withdrawTokens(IERC20(tokenAddress), rescueAmount);
    }

    /**
    @dev Only ower function to rescue any funds in the contract that someone might have sent on accident.
    * Rescues the entire contract balance of the token specified.
    @param tokenAddress the address of the token being rescued
    */
    function rescueFunds(address tokenAddress) external onlyOwner {
        require(tokenAddress != address(0), "Token address cannot be the 0 address.");
        withdrawTokens(IERC20(tokenAddress), IERC20(tokenAddress).balanceOf(address(this)));
    }

    /**
    @dev Only owner function to change the reference to the TBURN token.
    @param newTBURN reference to the new TBURN token
    */
    function updateTBURNTokenReference(IERC20 newTBURN) external onlyOwner {
        _tburn = newTBURN;
    }

    /**
    @dev Only owner function to change the reference to the OBURN token.
    @param newOBURN reference to the new OBURN token
    */
    function updateOBURNTokenReference(IERC20 newOBURN) external onlyOwner {
        _oburn = newOBURN;
    }
}