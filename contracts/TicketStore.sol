// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;
import "@openzeppelin/contracts/token/ERC721/ERC721.sol";
import "@openzeppelin/contracts/token/ERC721/extensions/ERC721URIStorage.sol";
import "@openzeppelin/contracts/access/AccessControl.sol";
import "@openzeppelin/contracts/utils/Counters.sol";
import "@openzeppelin/contracts/utils/Address.sol";

struct Ticket {
    string startStation;
    string endStation;
    int stationNum;
    uint256 date;
    bool used;
    bool refunded;
}

contract TicketStore is ERC721URIStorage, AccessControl {

    // Library declarations
    using Counters for Counters.Counter;
    using Address for address payable;

    // Constants definition
    bytes32 public constant USAGE_SETTER_ROLE = keccak256("USAGE_SETTER");
    uint256 public constant EURO_WEI = 370816960785710;
    uint256 public constant TICKET_PRICE_SHORT = EURO_WEI;
    uint256 public constant TICKET_PRICE_MEDIUM = 2*EURO_WEI;
    uint256 public constant TICKET_PRICE_LONG = 3*EURO_WEI;
    int public constant MIN_STATION_MEDIUM = 5;
    int public constant MIN_STATION_LONG = 13;

    // State variables
    Counters.Counter private _ticketIds;
    mapping (uint256 => Ticket) tickets;

    // Constructor
    constructor() ERC721("TicketStore", "TKS") {
        _ticketIds.increment(); // because we want to start from 1
        _setupRole(DEFAULT_ADMIN_ROLE, msg.sender);
        _setRoleAdmin(USAGE_SETTER_ROLE, DEFAULT_ADMIN_ROLE);
    }

    // Event definition
    event Debug(address user, address sender, bytes32 role, bytes32 adminRole, bytes32 senderRole);
    event DebugBuy(address buyer, uint256 amount, int stationNum, uint256 date, uint256 blocktimestamp);
    event ChecksoloAdmins(address user);
    event ChecksoloUsageSetters(address user);
    event RefundTicket(uint256 ticketId, address user, uint256 refundedAmount);
    event UseTicket(uint256 ticketId, address ownerAccount, address usageSetter);
    event Transfer(address toTransfer);

    // AccessControl modifier and permission-checking function definition
    modifier soloAdmins() {
        emit ChecksoloAdmins(msg.sender);
        require(isAdmin(msg.sender), "Caller is not an admin account!");
        _;
    }

    modifier soloUsageSetters() {
        emit ChecksoloUsageSetters(msg.sender);
        require(isUsageSetter(msg.sender) || isAdmin(msg.sender), "Caller is not a usage setter account!");
        _;
    }

    function isAdmin(address account) public virtual view returns (bool) {
        return hasRole(DEFAULT_ADMIN_ROLE, account);
    }

    function isUsageSetter(address account) public virtual view returns (bool) {
        return hasRole(USAGE_SETTER_ROLE, account);
    }

    function addAdminRole(address to) public soloAdmins {
        emit Debug(to, msg.sender, DEFAULT_ADMIN_ROLE, getRoleAdmin(DEFAULT_ADMIN_ROLE), DEFAULT_ADMIN_ROLE);
        grantRole(DEFAULT_ADMIN_ROLE, to);
    }

    function addUsageSetterRole(address to) public soloAdmins {
        emit Debug(to, msg.sender, USAGE_SETTER_ROLE, getRoleAdmin(USAGE_SETTER_ROLE), DEFAULT_ADMIN_ROLE);
        grantRole(USAGE_SETTER_ROLE, to);
    }

    function removeUsageSetterRole(address to) public soloUsageSetters {
        require(isAdmin(msg.sender) || msg.sender == to); // sender must be an admin or the usage setter himself
        renounceRole(USAGE_SETTER_ROLE, to);
    }

    function removeAdminRole(address to) public soloAdmins {
        renounceRole(DEFAULT_ADMIN_ROLE, to);
    }

    // Other misc functions 
    function buyTicket(address buyer, string memory ticketURI, int stationNum, string memory startStation,
     string memory endStation, uint256 date) public payable returns (uint256) {
        uint256 paidAmount = msg.value;
        // subtract 1 day to allow same-day ticket purchase
        emit DebugBuy(buyer, msg.value, stationNum, date, block.timestamp - 24*3600);
        if (checkPaidAmount(paidAmount, stationNum) && date > block.timestamp - 24*3600){
            _ticketIds.increment();
            uint256 newTicketId = _ticketIds.current();
            _mint(buyer, newTicketId);
            _setTokenURI(newTicketId, ticketURI);
            tickets[newTicketId] = Ticket(startStation, endStation, stationNum, date, false, false);
            return newTicketId;
        }
        else {
            return 0;
        }
    }

    function nextId() public view returns (uint256){
        return _ticketIds.current() + 1;
    }

    function checkPaidAmount(uint256 paidAmount, int stationNum) private pure returns (bool){
        if(stationNum < MIN_STATION_MEDIUM && paidAmount == TICKET_PRICE_SHORT){
            return true;
        }
        else if(stationNum >= MIN_STATION_MEDIUM && stationNum < MIN_STATION_LONG && paidAmount == TICKET_PRICE_MEDIUM){
            return true;
        }
        else if(stationNum >= MIN_STATION_LONG && paidAmount == TICKET_PRICE_LONG){
            return true;
        }
        return false;
    }

    function refund(uint256 ticketId) public {
        // caller must be the owner
        address payable owner = payable(ownerOf(ticketId));
        require(msg.sender == owner);

        // ticket has not to be already used
        require(!tickets[ticketId].used);

        // ticket has to be not expired, and we don't care if the miner can modify this by 900s
        require(tickets[ticketId].date > block.timestamp - 3600*24);

        // ticked has to be not refunded
        require(!tickets[ticketId].refunded);
        tickets[ticketId].refunded = true;

        // calculate ticket price
        uint256 ticketPrice = TICKET_PRICE_SHORT;
        if(tickets[ticketId].stationNum >= MIN_STATION_MEDIUM && tickets[ticketId].stationNum < MIN_STATION_LONG){
            ticketPrice = TICKET_PRICE_MEDIUM;
        }
        else if(tickets[ticketId].stationNum >= MIN_STATION_LONG){
            ticketPrice = TICKET_PRICE_LONG;
        }
        
        // library function to send amounts to specified address, after which we emit a refund event
        owner.sendValue(ticketPrice);
        emit RefundTicket(ticketId, owner, ticketPrice);
    }

    function transfer(address payable addressToTransfer) public soloAdmins{

        // library function to send amounts to specified address, after which we emit a transfer event
        addressToTransfer.sendValue(address(this).balance);
        emit Transfer(addressToTransfer);

    }

    function useTicket(uint256 ticketId) public soloUsageSetters{
        // ticket has not to be already used
        require(!tickets[ticketId].used);

        // ticket has to be not expired, subtract 1 day to allow same-day ticket refunds, also we don't care if the
        // miner can modify this by 900s
        require(tickets[ticketId].date > block.timestamp - 3600*24);

        // ticked has to be not refunded
        require(!tickets[ticketId].refunded);

        tickets[ticketId].used = true;
        emit UseTicket(ticketId, ownerOf(ticketId), msg.sender);
    }

    // override to prevent errors with the multiple inheritage
    function supportsInterface(bytes4 interfaceId) public view virtual override(ERC721, AccessControl) returns (bool) {
        return super.supportsInterface(interfaceId);
    }
}

