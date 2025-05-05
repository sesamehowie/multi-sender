from ..client.evm_client import EvmClient
from ..models.networks import Networks
from ..utils.decorator.decorators import retry_execution
from loguru import logger


class Transfer(EvmClient):
    def __init__(
        self,
        account_name=None,
        private_key=None,
        network=Networks.Monad,
        user_agent=None,
        proxy=None,
    ):
        super().__init__(account_name, private_key, network, user_agent, proxy)

    @retry_execution
    def perform(self, recipient_address: str, amount: float) -> str:
        is_checksum = self.w3.is_checksum_address(recipient_address)

        if not is_checksum:
            recipient_address = self.w3.to_checksum_address(recipient_address)
        if not isinstance(amount, float):
            amount = float(amount)

        logger.info(
            f"{self.account_name} | Sending {amount:.4f} {self.network.token} to {recipient_address}"
        )

        tx_data = self.get_tx_params(
            to_address=recipient_address,
            data="0x",
            value=int(amount * 10**18),
            default_gas=25000,
            eip_1559=False,
            estimate_gas=False,
            is_for_contract_tx=False,
        )

        tx_data["gas"] = 25000

        signed = self.sign_transaction(tx_dict=tx_data)

        if signed:
            tx_hash = self.send_tx(signed_tx=signed)
            if tx_hash is not None:
                return tx_hash
            else:
                raise Exception(
                    "Failed to get transaction hash, transaction most likely didnt get to the mempool"
                )
        raise Exception(
            "Failed to sign transaction, most likely transaction parameters are invalid"
        )
