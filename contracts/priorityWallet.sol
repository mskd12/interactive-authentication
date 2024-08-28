// SPDX-License-Identifier: GPL-3.0

pragma solidity >=0.7.0 <0.9.0;

import "hardhat/console.sol";

contract PriorityWallet {

    uint public numCredentials;
    mapping(address => uint) public priority;

    bool public withdrawalInProgress = false;
    uint public maxClaimID = 0;

    struct Details {
        bool[] supporters;
        uint amount;
        address addr;
    }
    Details[] public claimDetails;

    uint64 constant public delay = 100;
    uint64 public expiryTime;

    // Set the guardians and the priority vector. Ideally, you'd also want to deposit some money.
    constructor(address[] memory credentialList_) {
        numCredentials = credentialList_.length;
        for (uint i = 0; i < credentialList_.length; i++) {
            priority[credentialList_[i]] = i + 1;
        }
    }

    // Start a new withdrawal
    function initiateWithdrawal() public {
        assert (priority[msg.sender] > 0);
        assert (!withdrawalInProgress);

        withdrawalInProgress = true;
        expiryTime = uint64(block.timestamp + delay);
        // purge previous claim data (if any)
        delete claimDetails;
        maxClaimID = 0;
    }

    function createNewClaim(uint amount, address ToAddress) public returns (uint claimID) {
        assert (priority[msg.sender] > 0);
        assert (withdrawalInProgress); // otherwise call initiateWithdrawal
        console.log("Time: ", uint64(block.timestamp));
        assert (uint64(block.timestamp) <= expiryTime); 

        bool[] memory supporters = new bool[](numCredentials + 1);
        supporters[priority[msg.sender]] = true;
        claimDetails.push(Details(supporters, amount, ToAddress));
        console.log("Details: ", claimDetails[claimID].supporters[priority[msg.sender]]);

        claimID = maxClaimID; // create new claimID
        maxClaimID = maxClaimID + 1;
    }

    // adds approval to an existing claim
    function addApproval(uint claimID) public {
        assert (withdrawalInProgress);
        assert (claimID < maxClaimID);
        console.log("Time: ", uint64(block.timestamp));
        assert (uint64(block.timestamp) <= expiryTime); 
        assert (priority[msg.sender] > 0);

        claimDetails[claimID].supporters[priority[msg.sender]] = true;
    }

    function getClaimSupporters(uint claimID) public view returns (bool[] memory) {
        return claimDetails[claimID].supporters;
    }

    function withdraw() public {
        console.log("Time: ", uint64(block.timestamp));
        assert(uint64(block.timestamp) > expiryTime);
        assert(withdrawalInProgress);

        bool[] memory potentialWinners = new bool[](maxClaimID);
        for (uint c = 0; c < maxClaimID; c++) {
            potentialWinners[c] = true;
        }

        for (uint p = 1; p <= numCredentials; p++) {
            bool foundAny = false;
            for (uint c = 0; c < maxClaimID; c++) {
                if (potentialWinners[c] && claimDetails[c].supporters[p]) {
                    foundAny = true;
                }
            }

            if (foundAny) {
                for (uint c = 0; c < maxClaimID; c++) {
                    if (potentialWinners[c] && !claimDetails[c].supporters[p]) {
                        potentialWinners[c] = false;
                    }
                }
            }
        }

        for (uint c = 0; c < maxClaimID; c++) {
            if (potentialWinners[c]) {
                uint winningClaimID = c;
                console.log("Winning claim is", winningClaimID);
                console.log("Sending", claimDetails[winningClaimID].amount);
                console.log("To", claimDetails[winningClaimID].addr);
                // TODO: Send amount
                withdrawalInProgress = false;
                break;
            }
        }
    }
}

// 0x5B38Da6a701c568545dCfcB03FcB875f56beddC4
// 0xAb8483F64d9C6d1EcF9b849Ae677dD3315835cb2
// 0x4B20993Bc481177ec7E8f571ceCaE8A9e22C02db
// 0x78731D3Ca6b7E34aC0F824c42a7cC18A495cabaB
// ["0x5B38Da6a701c568545dCfcB03FcB875f56beddC4", "0xAb8483F64d9C6d1EcF9b849Ae677dD3315835cb2", "0x4B20993Bc481177ec7E8f571ceCaE8A9e22C02db", "0x78731D3Ca6b7E34aC0F824c42a7cC18A495cabaB"]