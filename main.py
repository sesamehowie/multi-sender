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


def load_processed_addresses():
    return set()


def parse_transfer_data():
    transfer_data = []
    skipped_lines = []

    try:
        with open("data/data.txt", "r") as f:
            lines = f.read().splitlines()
    except FileNotFoundError:
        logger.error("data/data.txt not found!")
        return [], []

    for line_num, line in enumerate(lines, 1):
        line = line.strip()
        if not line:
            continue

        try:
            parts = line.split(",")
            if len(parts) != 2:
                raise ValueError(
                    f"Expected 2 parts separated by comma, got {len(parts)}"
                )

            address = parts[0].strip()
            amount = float(parts[1].strip())

            if not address.startswith("0x") or len(address) != 42:
                raise ValueError(f"Invalid address format: {address}")

            if amount <= 0:
                raise ValueError(f"Invalid amount: {amount}")

            transfer_data.append((address, amount))

        except Exception as e:
            error_msg = f"Line {line_num}: '{line}' - Error: {str(e)}"
            logger.error(error_msg)
            skipped_lines.append(error_msg)

    return transfer_data, skipped_lines


def one_to_many():
    logger.info("Starting one-to-many transfer process")

    transfer_data, skipped_lines = parse_transfer_data()
    processed_addresses = load_processed_addresses()

    if skipped_lines:
        logger.warning(f"Skipped {len(skipped_lines)} invalid lines:")
        for skip in skipped_lines:
            logger.warning(skip)

    if not transfer_data:
        logger.error("No valid transfer data found!")
        return

    logger.info(f"Loaded {len(transfer_data)} valid transfers")
    logger.info("Processing ALL wallets (no duplicate checking)")

    pending_transfers = transfer_data
    logger.info(f"Processing {len(pending_transfers)} pending transfers")
    transfer = Transfer(
        account_name=ACCOUNT_NAME, private_key=PRIVATE_KEY, network=Networks.Monad
    )

    results = []
    failed_transfers = []

    for i, (address, amount) in enumerate(pending_transfers, 1):
        logger.info(
            f"Processing {i}/{len(pending_transfers)}: {address} - {amount:.6f} {transfer.network.token}"
        )

        try:
            result = transfer.perform(address, amount)

            if result:
                success_msg = f"{address} - SUCCESS - {result}"
                results.append(success_msg)
            else:
                failed_msg = f"{address} - FAILED - None"
                results.append(failed_msg)
                failed_transfers.append((address, amount))

        except Exception as e:
            error_msg = f"{address} - ERROR - {str(e)}"
            results.append(error_msg)
            failed_transfers.append((address, amount))
            logger.error(
                f"{address} - {amount} {transfer.network.token} - Exception: {str(e)}"
            )

        if i < len(pending_transfers):
            sleeping(2)

    if results:
        with open("results/oneToManyResults.txt", "a") as f:
            for line in results:
                f.write(line + "\n")
        logger.info("Results saved to oneToManyResults.txt")

    if failed_transfers:
        with open("results/failedTransfers.txt", "w") as f:
            for address, amount in failed_transfers:
                f.write(f"{address}, {amount}\n")
        logger.warning(
            f"{len(failed_transfers)} transfers failed - saved to failedTransfers.txt"
        )

    successful = len(results) - len(failed_transfers)
    logger.info("Transfer Summary:")
    logger.info(f"Successful: {successful}")
    logger.info(f"Failed: {len(failed_transfers)}")
    logger.info(f"Total processed: {len(results)}")


def many_to_one():
    from itertools import cycle

    results = []

    try:
        with open("data/private_keys.txt", "r") as f:
            private_keys = f.read().splitlines()
    except FileNotFoundError:
        logger.error("private_keys.txt not found!")
        return

    try:
        with open("data/proxies.txt", "r") as f:
            proxies = f.read().splitlines()
    except FileNotFoundError:
        logger.error("proxies.txt not found!")
        return

    proxy_cycle = cycle(proxies)
    transfer = Transfer(network=Networks.Binance)

    for account_name, private_key in enumerate(private_keys, start=1):
        try:
            transfer.update_wallet(account_name, private_key, next(proxy_cycle))
            result = transfer.perform(TARGET_ADDRESS, None)

            if result:
                results.append(f"{transfer.address} - Success - {result}")
            else:
                results.append(f"{transfer.address} - Failed - none")

        except Exception as e:
            results.append(f"Account {account_name} - Error - {str(e)}")

        sleeping(1)

    if results:
        with open("results/manyToOneResults.txt", "a") as f:
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
