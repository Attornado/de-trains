var TicketStore = artifacts.require("TicketStore");


module.exports = function(deployer) {
   deployer.deploy(TicketStore);
}
