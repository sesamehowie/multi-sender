from dataclasses import dataclass


class Network:

    def __init__(
        self,
        name,
        chain_id,
        rpc_list,
        scanner,
        eip1559_support: bool = False,
        token: str = "ETH",
    ):
        self.name = name
        self.chain_id = chain_id
        self.rpc_list = rpc_list
        self.scanner = scanner
        self.token = token


@dataclass
class Networks:
    Ethereum = Network(
        name="Ethereum",
        chain_id=1,
        rpc_list=[
            "https://eth.meowrpc.com",
            "https://eth.drpc.org",
        ],
        scanner="https://etherscan.io",
        eip1559_support=True,
    )
    Base = Network(
        name="Base",
        chain_id=8453,
        rpc_list=[
            "https://base.drpc.org",
            "https://1rpc.io/base",
        ],
        scanner="https://basescan.org",
        eip1559_support=True,
    )
    Optimism = Network(
        name="Optimism",
        rpc_list=[
            "https://rpc.ankr.com/optimism/",
            "https://optimism.drpc.org",
            "https://1rpc.io/op",
        ],
        chain_id=10,
        eip1559_support=True,
        token="ETH",
        scanner="https://optimistic.etherscan.io",
    )
    Linea = Network(
        name="Linea",
        rpc_list=[
            "https://rpc.linea.build",
            "https://1rpc.io/linea",
            "https://linea.blockpi.network/v1/rpc/public",
        ],
        chain_id=59144,
        eip1559_support=False,
        token="ETH",
        scanner="https://lineascan.build",
    )
    Arbitrum = Network(
        name="Arbitrum",
        rpc_list=[
            "https://arbitrum-one.publicnode.com",
            "https://arbitrum-one.publicnode.com",
        ],
        chain_id=42161,
        eip1559_support=True,
        token="ETH",
        scanner="https://arbiscan.io/",
    )
    Zora = Network(
        name="Zora",
        chain_id=7777777,
        rpc_list=["https://rpc.zora.energy"],
        scanner="https://explorer.zora.energy",
        eip1559_support=True,
        token="ETH",
    )
    Scroll = Network(
        name="Scroll",
        chain_id=534352,
        rpc_list=[
            "https://empty-newest-mountain.scroll-mainnet.quiknode.pro/fb052bf49fc42586377a0376dde4c80109e9facf",
            "https://empty-newest-mountain.scroll-mainnet.quiknode.pro/fb052bf49fc42586377a0376dde4c80109e9facf",
        ],
        scanner="https://scrollscan.com/",
        eip1559_support=True,
        token="ETH",
    )
    Bitlayer = Network(
        name="Bitlayer",
        chain_id=200901,
        rpc_list=[
            "https://rpc.bitlayer-rpc.com",
            "https://rpc.ankr.com/bitlayer",
            "https://rpc.bitlayer.org",
        ],
        scanner="https://www.btrscan.com",
        eip1559_support=True,
        token="BTC",
    )
    Monad = Network(
        name="Monad Testnet",
        chain_id=10143,
        rpc_list=["https://testnet-rpc.monad.xyz", "https://testnet-rpc.monad.xyz"],
        eip1559_support=False,
        scanner="https://testnet.monadexplorer.com",
        token="MON",
    )
    Binance = Network(
        name="Binance Smart Chain",
        chain_id=56,
        rpc_list=[
            "https://muddy-nameless-knowledge.bsc.quiknode.pro/1349fe899f6e712099bfc7c57b0cbfb743701895/",
            "https://muddy-nameless-knowledge.bsc.quiknode.pro/1349fe899f6e712099bfc7c57b0cbfb743701895/",
            "https://muddy-nameless-knowledge.bsc.quiknode.pro/1349fe899f6e712099bfc7c57b0cbfb743701895/",
        ],
        scanner="https://bscscan.com",
        eip1559_support=True,
        token="BNB",
    )

    NetworkList = [
        Ethereum,
        Base,
        Optimism,
        Linea,
        Arbitrum,
        Zora,
        Scroll,
        Bitlayer,
        Monad,
        Binance,
    ]

    @staticmethod
    def get_network_by_name(name: str) -> Network | None:
        return {
            "Arbitrum": Networks.Arbitrum,
            "Ethereum": Networks.Ethereum,
            "Optimism": Networks.Optimism,
            "Base": Networks.Base,
            "Linea": Networks.Linea,
            "Zora": Networks.Zora,
            "Scroll": Networks.Scroll,
            "Bitlayer": Networks.Bitlayer,
            "Binance Smart Chain": Networks.Binance,
        }.get(name, None)

    @staticmethod
    def get_network_by_orbiter_id(orbiter_id: int) -> Network | None:
        return Networks.get_network_by_name(
            {
                1: "Ethereum",
                2: "Arbitrum",
                6: "Polygon",
                7: "Optimism",
                19: "Scroll",
                21: "Base",
                23: "Linea",
                30: "Zora",
                59: "Bitlayer",
            }.get(orbiter_id, None)
        )

    @staticmethod
    def get_network_by_chain_id(chain_id: int) -> Network | None:
        return {
            1: Networks.Ethereum,
            56: Networks.Binance,
            42161: Networks.Arbitrum,
            8453: Networks.Base,
            10: Networks.Optimism,
            59144: Networks.Linea,
            7777777: Networks.Zora,
            534352: Networks.Scroll,
            200901: Networks.Bitlayer,
        }.get(chain_id, None)
