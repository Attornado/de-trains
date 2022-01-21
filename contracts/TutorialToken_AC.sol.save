pragma solidity ^0.8.0;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/access/AccessControl.sol";

contract TutorialToken_AC is ERC20, AccessControl {
   bytes32 public constant MINTER_ROLE = keccak256("MINTER_ROLE");

   constructor(
        string memory name,
        string memory symbol,
        uint256 initialSupply) ERC20(name, symbol) {
      _mint(msg.sender, initialSupply);
      _setupRole(DEFAULT_ADMIN_ROLE, msg.sender);
   }

   modifier onlyAdmin() {
      require(isAdmin(msg.sender), "Restricted to admins");
      _;
   }

   modifier onlyMinters() {
      require(hasRole(MINTER_ROLE, msg.sender), "Caller is not a minter");
      _;
   }

   function isAdmin(address account) public virtual view returns (bool) {
      return hasRole(DEFAULT_ADMIN_ROLE, account);
   }

   function mint(address to, uint256 amount) public onlyMinters {
      _mint(to, amount);
    }

    function addMinterRole(address to) public onlyAdmin {
      _grantRole(MINTER_ROLE, to);
    }

    function removeMinterRole (address to) public onlyAdmin {
      revokeRole(MINTER_ROLE, to);
    }
}
