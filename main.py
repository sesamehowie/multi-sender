import os
from src.utils.helpers.helpers import sleeping
from src.actions.transfer import Transfer
from dotenv import load_dotenv
from loguru import logger
from src.models.networks import Networks

load_dotenv()

PRIVATE_KEY = os.environ.get("ADMIN_PKEY")
TARGET_ADDRESS = os.environ.get("TARGET_ADDRESS")
ACCOUNT_NAME = "admin wallet"


def choose_mode():
    try:
        val = int(
            input(
                "Choose your option:\n1. One wallet to many\n2. Many wallets to one\n"
            )
        )
        if val not in range(1, 3):
            raise Exception("Invalid input")

        return val
    except Exception:
        logger.warning("Invalid input. Try again")
        return choose_mode()


def many_to_one():
    from itertools import cycle

    results = []

    with open("data/private_keys.txt", "r") as f:
        private_keys = f.read().splitlines()

    with open("data/proxies.txt", "r") as f:
        proxies = f.read().splitlines()

    proxy_cycle = cycle(proxies)

    transfer = Transfer(network=Networks.Binance)

    for account_name, private_key in enumerate(private_keys, start=1):
        transfer.update_wallet(account_name, private_key, next(proxy_cycle))
        result = transfer.perform(TARGET_ADDRESS, None)

        if result:
            results.append(f"{transfer.address} - Success - {result}")
        else:
            results.append(f"{transfer.address} - Failed - none")
        sleeping(1)

    if results:
        with open("results/manyToOneResults.txt", "a") as f:
            for line in results:
                f.write(line + "\n")


def one_to_many():
    results = []

    with open("data/data.txt", "r") as f:
        transfer_data = f.read().splitlines()

    transfer = Transfer(account_name=ACCOUNT_NAME, private_key=PRIVATE_KEY)

    for item in transfer_data:
        items = item.split(",")
        recipient_address = items[0].strip()
        amount = float(items[1].strip())

        result = transfer.perform(recipient_address, amount)

        if result:
            results.append(f"{recipient_address} - Success - {result}")
        else:
            results.append(f"{recipient_address} - Failed - none")

        sleeping(1)

    if results:
        with open("results/oneToManyResults.txt", "a") as f:
            for line in results:
                f.write(line + "\n")


def main():
    choice = choose_mode()

    match choice:
        case 1:
            one_to_many()
        case 2:
            many_to_one()


if __name__ == "__main__":
    main()
