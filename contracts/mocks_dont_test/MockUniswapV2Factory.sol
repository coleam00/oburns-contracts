// SPDX-License-Identifier: MIT
pragma solidity >=0.8.0 <0.9.0;

import "../../interfaces/Uniswap.sol";

contract MockUniswapV2Factory is IUniswapV2Factory {
    address public _tokenA;
    address public _tokenB;

    function createPair(address tokenA, address tokenB) external returns (address pair) {
        _tokenA = tokenA;
        _tokenB = tokenB;

        return address(this);
    }
}