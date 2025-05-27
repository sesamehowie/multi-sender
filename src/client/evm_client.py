from web3 import Web3
import random
import time
from web3.middleware.geth_poa import geth_poa_middleware
from typing import Self
from loguru import logger
from web3.types import SignedTx
from eth_typing import HexStr, ChecksumAddress
from eth_account import Account
from ..models.networks import Network, Networks
from ..config.constants import (
    GAS_AMT_MULTIPLIER,
    GAS_LIMIT_MULTIPLIER,
    GAS_PRICE_MULTIPLIER,
)
from ..config.transaction_config import MINIMUM_TRANSFER_REQUIREMENTS

import pyuseragents


class EvmClient:

    def __init__(
        self: Self,
        account_name: str | int = None,
        private_key: HexStr | str = None,
        network: Network = Networks.Ethereum,
        user_agent: str = None,
        proxy: str = None,
    ) -> Self:
        self.account_name = account_name if account_name else "unnamed account"
        self.private_key = private_key
        self.account = Account.from_key(self.private_key) if private_key else None
        self.address = (
            Web3.to_checksum_address(self.account.address) if private_key else None
        )
        self.network = network
        self.rpc = self.network.rpc_list[0]
        self.user_agent = user_agent if user_agent else pyuseragents.random()
        self.chain_id = self.network.chain_id
        self.proxy = proxy if proxy else None

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
                request_kwargs=self.request_kwargs if proxy and user_agent else None,
            )
        )

        self.logger = logger
        self.module_name = "EvmClient"

        if network.chain_id in (Networks.Linea.chain_id, Networks.Scroll.chain_id):
            self.w3.middleware_onion.inject(geth_poa_middleware, layer=0)

    def get_nonce(self, address: str | ChecksumAddress) -> int:
        return self.w3.eth.get_transaction_count(address)

    def get_new_provider(self):
        unused_rpcs = []
        for rpc in self.network.rpc_list:
            if rpc != self.rpc:
                unused_rpcs.append(rpc)

        if len(unused_rpcs) > 0:
            self.rpc = random.choice(unused_rpcs)
            self.w3 = self.w3 = Web3(
                Web3.HTTPProvider(
                    endpoint_uri=self.rpc,
                    request_kwargs=(
                        self.request_kwargs if self.proxy and self.user_agent else None
                    ),
                )
            )
        else:
            logger.warning(f"RPC error on {self.rpc} and no replacement rpc")
            time.sleep(60)

    def get_tx_params(
        self,
        to_address: str | ChecksumAddress = None,
        value: int = 0,
        data: bytes = None,
        default_gas: int = 200000,
        eip_1559: bool = True,
        estimate_gas: bool = True,
        is_for_contract_tx: bool = False,
        full_balance: bool = False,
    ) -> dict:
        balance = self.get_balance()

        if self.network.name in MINIMUM_TRANSFER_REQUIREMENTS.keys():
            minimum_requirements = MINIMUM_TRANSFER_REQUIREMENTS.get(self.network.name)
            min_gas, min_gas_price = minimum_requirements.get(
                "gas"
            ), minimum_requirements.get("gasPrice")
            min_network_fee = int(min_gas * min_gas_price)

            if all([item is not None for item in [min_gas, min_gas_price]]):
                if balance < min_network_fee:
                    logger.warning(
                        f"{self.account_name} | {self.address} - Does not meet the minimum balance requirements of {self.network.name}: {float(Web3.from_wei(min_network_fee, 'ether')):.8f} {self.network.token}"
                    )
                    return

        if is_for_contract_tx:
            return {
                "from": Web3.to_checksum_address(self.address),
                "nonce": self.get_nonce(self.address),
                "chainId": self.chain_id,
            }

        tx_params = {
            "from": Web3.to_checksum_address(self.address),
            "to": Web3.to_checksum_address(to_address),
            "chainId": self.chain_id,
            "nonce": self.get_nonce(self.address),
            "value": value,
        }

        time.sleep(4)

        if data is not None:
            tx_params["data"] = data

        if eip_1559:
            time.sleep(5)
            base_fee_per_gas = self.w3.eth.get_block("latest")["baseFeePerGas"]
            max_priority_fee_per_gas = self.w3.eth.max_priority_fee
            max_fee_per_gas = max_priority_fee_per_gas + int(
                base_fee_per_gas * GAS_LIMIT_MULTIPLIER
            )
            tx_params["maxPriorityFeePerGas"] = int(
                max_priority_fee_per_gas * GAS_PRICE_MULTIPLIER
            )
            tx_params["maxFeePerGas"] = int(max_fee_per_gas * GAS_PRICE_MULTIPLIER)
        else:
            tx_params["gasPrice"] = int(self.w3.eth.gas_price * GAS_PRICE_MULTIPLIER)
            time.sleep(4)

        if estimate_gas:
            try:
                tx_params["gas"] = int(
                    self.w3.eth.estimate_gas(transaction=tx_params) * GAS_AMT_MULTIPLIER
                )
                time.sleep(4)
            except Exception:
                tx_params["gas"] = default_gas

        if full_balance:
            if tx_params.get("gas", None) is not None:

                if eip_1559:
                    del tx_params["maxFeePerGas"]
                    del tx_params["maxPriorityFeePerGas"]
                    tx_params["gasPrice"] = int(
                        self.w3.eth.gas_price * GAS_PRICE_MULTIPLIER
                    )
                    tx_params["gas"] = int(
                        self.w3.eth.estimate_gas(transaction=tx_params)
                        * GAS_AMT_MULTIPLIER
                    )

                tx_params["value"] = int(
                    balance - (tx_params["gas"] * tx_params["gasPrice"])
                )

        return tx_params

    def get_balance(self):
        try:
            return int(self.w3.eth.get_balance(self.address))
        except Exception as e:
            logger.warning(f"{self.address} | Error getting balance: {str(e)}")
            self.get_new_provider()
            time.sleep(5)
            return self.get_balance()

    def send_tx(self, signed_tx: SignedTx) -> str | HexStr:
        timeout = 180
        try:
            tx_hash = self.w3.eth.send_raw_transaction(signed_tx.rawTransaction)
        except ValueError:
            return

        if tx_hash:

            res = self.w3.eth.wait_for_transaction_receipt(
                tx_hash.hex(), timeout=timeout
            )

            if res:
                if res["status"] == 1:
                    self.logger.success(
                        f"{self.account_name} | {self.address} | {self.module_name} | Transaction: {self.network.scanner}/tx/{tx_hash.hex()}"
                    )
                elif res["status"] == 0:
                    self.logger.warning(
                        f"{self.account_name} | {self.address} | {self.module_name} | Transaction failed: {self.network.scanner}/tx/{tx_hash.hex()}"
                    )

                return str(tx_hash.hex())

        self.logger.warning(
            f"{self.account_name} | {self.address} | {self.module_name} | Transaction didn't come through after {timeout} seconds."
        )

        return

    def sign_transaction(self, tx_dict: dict) -> SignedTx:

        return (
            self.w3.eth.account.sign_transaction(
                transaction_dict=tx_dict, private_key=self.private_key
            )
            if tx_dict
            else None
        )

    def get_gas_price(self):
        return self.w3.eth.gas_price

    def get_tx_receipt(self, tx_hash):
        return self.w3.eth.get_transaction_receipt(transaction_hash=tx_hash)
