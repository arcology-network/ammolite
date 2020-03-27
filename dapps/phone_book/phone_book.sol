pragma solidity ^0.5.0;

import "./ConcurrentLibInterface.sol";

contract PhoneBook {
    address apiAddr = address(0x81);

    event PhoneNoUpdated(address addr, uint256 no);
    event PhoneNoQuery(address addr, uint256 no);
    
    constructor() public {
        ConcurrentHashMap chm = ConcurrentHashMap(apiAddr);
        chm.create("addr2phoneNo", int32(ConcurrentLib.DataType.ADDRESS), int32(ConcurrentLib.DataType.UINT256));
    }
    
    function set(uint256 phoneNo) public {
        ConcurrentHashMap chm = ConcurrentHashMap(apiAddr);
        chm.set("addr2phoneNo", msg.sender, phoneNo);
        emit PhoneNoUpdated(msg.sender, phoneNo);
    }
    
    function get(address addr) public {
        ConcurrentHashMap chm = ConcurrentHashMap(apiAddr);
        uint256 phoneNo = chm.getUint256("addr2phoneNo", addr);
        emit PhoneNoQuery(addr, phoneNo);
    }
}