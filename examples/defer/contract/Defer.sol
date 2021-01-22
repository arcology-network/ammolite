pragma solidity ^0.5.0;

import "./ConcurrentLibInterface.sol";

contract Defer {
    ConcurrentQueue constant queue = ConcurrentQueue(0x82);
    System constant system = System(0xa1);

    uint256 counter = 0;
    event CounterQuery(uint256 value);

    constructor() public {
        queue.create("counterUpdates", uint256(ConcurrentLib.DataType.UINT256));
        system.createDefer("updateCounter", "updateCounter(string)");
    }

    function increase(uint256 value) public {
        queue.pushUint256("counterUpdates", value);
        system.callDefer("updateCounter");
    }

    function getCounter() public {
        emit CounterQuery(counter);
    }

    function updateCounter(string memory) public {
        uint256 len = queue.size("counterUpdates");
        for (uint256 i = 0; i < len; i++) {
            uint256 changes = queue.popUint256("counterUpdates");
            counter += changes;
        }
    }
}