// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "@openzeppelin/contracts/token/ERC20/IERC20.sol";

contract PriorityQueue {
    IERC20 public immutable token;

    struct Txn {
        address sender;
        uint256 amount;
        uint256 priority;
        uint256 day;
        string  timeRaw;
        uint16  timeVal;
        uint256 idx;
    }

    uint256 private _counter;
    uint256[] private _queue;
    mapping(uint256 => Txn) private _txns;

    constructor(address tokenAddress) {
        token = IERC20(tokenAddress);
    }

    function enqueue(
        uint256 amount,
        uint256 priority,
        uint256 day,
        string calldata time
    ) external {
        require(token.balanceOf(msg.sender) >= amount, "Insufficient balance");
        _counter += 1;
        uint256 entryId = _counter;
        uint16 tVal = _parseTime(time);

        _txns[entryId] = Txn({
            sender: msg.sender,
            amount: amount,
            priority: priority,
            day: day,
            timeRaw: time,
            timeVal: tVal,
            idx: entryId
        });
        _queue.push(entryId);
    }

    function dequeue()
        external
        returns (
            address sender_,
            uint256 amount_,
            uint256 priority_,
            uint256 day_,
            string memory time_
        )
    {
        require(_queue.length > 0, "Queue is empty");

        uint256 bestIdxInArray = _queue.length; // sentinel
        uint256 bestId = 0;
        Txn memory bestTxn;

        for (uint256 i = 0; i < _queue.length; i++) {
            uint256 id = _queue[i];
            Txn memory t = _txns[id];

            if (token.balanceOf(t.sender) < t.amount) {
                continue;
            }
            if (bestId == 0) {
                bestId = id;
                bestTxn = t;
                bestIdxInArray = i;
                continue;
            }
            bool isBetter =
                (t.priority < bestTxn.priority) ||
                (t.priority == bestTxn.priority && t.day < bestTxn.day) ||
                (t.priority == bestTxn.priority && t.day == bestTxn.day && t.timeVal < bestTxn.timeVal) ||
                (t.priority == bestTxn.priority && t.day == bestTxn.day && t.timeVal == bestTxn.timeVal && t.idx < bestTxn.idx);

            if (isBetter) {
                bestId = id;
                bestTxn = t;
                bestIdxInArray = i;
            }
        }

        require(bestId != 0, "No eligible transaction");

        // remove via swap-and-pop
        uint256 lastId = _queue[_queue.length - 1];
        _queue[bestIdxInArray] = lastId;
        _queue.pop();

        sender_   = bestTxn.sender;
        amount_   = bestTxn.amount;
        priority_ = bestTxn.priority;
        day_      = bestTxn.day;
        time_     = bestTxn.timeRaw;

        delete _txns[bestId];
    }

    function queueLength() external view returns (uint256) {
        return _queue.length;
    }

    function _parseTime(string calldata ts) private pure returns (uint16) {
        bytes memory b = bytes(ts);
        require(b.length == 5 && b[2] == ":", "Invalid time format");

        uint16 h = (uint16(uint8(b[0])) - 48) * 10 + (uint16(uint8(b[1])) - 48);
        uint16 m = (uint16(uint8(b[3])) - 48) * 10 + (uint16(uint8(b[4])) - 48);
        require(h < 24 && m < 60, "Time out of range");

        return h * 60 + m;
    }
}
