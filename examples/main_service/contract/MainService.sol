pragma solidity ^0.5.0;

import "./ConcurrentLibInterface.sol";

contract StorageService {
    ConcurrentHashMap constant hashmap = ConcurrentHashMap(0x81);
    
    event Checker(uint256, uint256, uint256, uint256, bytes);
    
    constructor() public {
        hashmap.create("map1", int32(ConcurrentLib.DataType.UINT256), int32(ConcurrentLib.DataType.UINT256));
        hashmap.create("map2", int32(ConcurrentLib.DataType.UINT256), int32(ConcurrentLib.DataType.UINT256));
        hashmap.create("map3", int32(ConcurrentLib.DataType.UINT256), int32(ConcurrentLib.DataType.UINT256));
        hashmap.create("map4", int32(ConcurrentLib.DataType.UINT256), int32(ConcurrentLib.DataType.BYTES));
    }
    
    //function func(uint256 key, uint256 args, bytes memory data) public {
    function func(uint256 key, uint256 args) public {
        uint256 arg1 = args & 0xff;
        if (arg1 != 0) {
            hashmap.set("map1", key, hashmap.getUint256("map1", key)+arg1);
        }
        
        uint256 arg2 = (args & 0xff00) >> 8;
        if (arg2 != 0) {
            hashmap.set("map2", key, arg2);
        }
        
        uint256 arg3 = (args & 0xff0000) >> 16;
        if (arg3 != 0) {
            hashmap.set("map3", key, arg3);
        }
        
        //if (data.length > 0) {
        //    hashmap.set("map4", key, data);
        //}
    }
    
    function check(uint256 key) public {
        emit Checker(
            key,
            hashmap.getUint256("map1", key),
            hashmap.getUint256("map2", key),
            hashmap.getUint256("map3", key),
            hashmap.getBytes("map4", key)
        );
    }
}

contract ComputingService {
    function func(uint256 n) public pure returns(uint256) {
        if (n == 0 || n == 1 || n == 2) {
            return 1;
        }
        
        uint256 n_1 = 1;
        uint256 n_2 = 1;
        for (uint256 i = 3; i < n; i++) {
            uint256 tmp = n_1;
            n_1 = n_1 + n_2;
            n_2 = tmp;
        }
        
        return n_1 + n_2;
    }
}

contract MainService {
    ConcurrentHashMap constant hashmap = ConcurrentHashMap(0x81);
    
    // event Checker(uint256, uint256, uint256, uint256, uint256, uint256, bytes);
    event Checker(uint256, uint256, uint256, uint256, uint256, uint256);
    
    constructor() public {
        hashmap.create("map1", int32(ConcurrentLib.DataType.UINT256), int32(ConcurrentLib.DataType.UINT256));
        hashmap.create("map2", int32(ConcurrentLib.DataType.UINT256), int32(ConcurrentLib.DataType.UINT256));
        hashmap.create("map3", int32(ConcurrentLib.DataType.UINT256), int32(ConcurrentLib.DataType.UINT256));
        hashmap.create("map4", int32(ConcurrentLib.DataType.UINT256), int32(ConcurrentLib.DataType.UINT256));
        hashmap.create("map5", int32(ConcurrentLib.DataType.UINT256), int32(ConcurrentLib.DataType.UINT256));
        hashmap.create("map6", int32(ConcurrentLib.DataType.UINT256), int32(ConcurrentLib.DataType.BYTES));
    }
    
    //function func(uint256 key, uint256 args, bytes memory data, address storageSvc, uint256 sargs, address computeSvc, uint256 cargs) payable public {
    function func(uint256 key, uint256 args, address storageSvc, uint256 sargs, address computeSvc, uint256 cargs) payable public {
        if (storageSvc != address(0)) {
            StorageService svc = StorageService(storageSvc);
            //svc.func(key, sargs, data);
            svc.func(key, sargs);
        }
        
        if (computeSvc != address(0)) {
            ComputingService svc = ComputingService(computeSvc);
            svc.func(cargs);
        }
        
        uint256 arg1 = args & 0xff;
        if (arg1 != 0) {
            hashmap.set("map1", key, hashmap.getUint256("map1", msg.sender)+arg1);
        }
        
        uint256 arg2 = (args & 0xff00) >> 8;
        if (arg2 != 0) {
            hashmap.set("map2", key, hashmap.getUint256("map2", msg.sender)+arg2);
        }
        
        uint256 arg3 = (args & 0xff0000) >> 16;
        if (arg3 != 0) {
            hashmap.set("map3", key, arg3);
        }
        
        uint256 arg4 = (args & 0xff000000) >> 24;
        if (arg4 != 0) {
            hashmap.set("map4", key, arg4);
        }
        
        uint256 arg5 = (args & 0xff00000000) >> 32;
        if (arg5 != 0) {
            hashmap.set("map5", key, arg5);
        }
        
        uint256 arg6 = (args & 0xff0000000000) >> 40;
        if (arg6 != 0) {
            msg.sender.transfer(arg6);
        }
        
        //if (data.length > 0) {
        //    hashmap.set("map6", key, data);
        //}
    }
    
    function check(uint256 key) public {
        emit Checker(
            key,
            hashmap.getUint256("map1", key),
            hashmap.getUint256("map2", key),
            hashmap.getUint256("map3", key),
            hashmap.getUint256("map4", key),
            hashmap.getUint256("map5", key)
            // hashmap.getBytes("map6", key)
        );
    }
}
