from ..client.evm_client import EvmClient
from ..models.networks import Networks
from ..utils.decorator.decorators import retry_execution
from loguru import logger
from web3 import Web3
import pyuseragents


class Transfer(EvmClient):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(
        self,
        account_name=None,
        private_key=None,
        network=Networks.Monad,
        user_agent=None,
        proxy=None,
    ):
        # Only initialize if not already initialized
        if not hasattr(self, "_initialized"):
            super().__init__(account_name, private_key, network, user_agent, proxy)
            self._initialized = True

    def update_wallet(self, account_name, private_key, proxy=None):
        self.account_name = account_name
        self.private_key = private_key
        self.proxy = proxy

        if self.proxy:
            self.user_agent = pyuseragents.random()
            self.request_kwargs = {
                "headers": {
                    "User-Agent": self.user_agent,
                    "Content-Type": "application/json",
                },
                "proxies": {
                    "http": self.proxy,
                    "https": self.proxy,
                },
                "timeout": 60,
            }

        self.w3 = Web3(
            Web3.HTTPProvider(
                endpoint_uri=self.rpc,
                request_kwargs=(
                    self.request_kwargs if self.proxy and self.user_agent else None
                ),
            )
        )
        if self.private_key:
            self.account = self.w3.eth.account.from_key(self.private_key)
            self.address = self.account.address

    @retry_execution
    def perform(self, recipient_address: str, amount: float | None = None) -> str:
        is_checksum = self.w3.is_checksum_address(recipient_address)

        if not is_checksum:
            recipient_address = self.w3.to_checksum_address(recipient_address)
        if amount and not isinstance(amount, float):
            amount = float(amount)

        logger.info(
            f"{self.account_name} | {self.address} | Sending {round(amount, 4) if amount is not None else 'full balance'} {self.network.token} to {recipient_address}"
        )

        if not amount:
            tx_data = self.get_tx_params(
                to_address=recipient_address,
                data="0x",
                value=0,
                default_gas=25000,
                eip_1559=False,
                estimate_gas=True,
                is_for_contract_tx=False,
                full_balance=True,
            )
        else:
            tx_data = self.get_tx_params(
                to_address=recipient_address,
                data="0x",
                value=int(amount * 10**18),
                default_gas=25000,
                eip_1559=False,
                estimate_gas=False,
                is_for_contract_tx=False,
                full_balance=True,
            )
            tx_data["gas"] = 25000

        if not tx_data:
            logger.warning(
                f"{self.account_name} | {self.address}: Does not have enough {self.network.token} to cover the network fee"
            )
            return

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
