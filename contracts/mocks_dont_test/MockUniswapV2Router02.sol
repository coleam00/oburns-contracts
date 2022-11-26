// SPDX-License-Identifier: MIT
pragma solidity >=0.8.0 <0.9.0;

import "../../interfaces/Uniswap.sol";

contract MockUniswapV2Router02 {
    address public _factory;

    constructor(address initFactory) {
        _factory = initFactory;
    }

    function factory() external view returns (address) {
        return _factory;
    }
}