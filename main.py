import os
from src.utils.helpers.helpers import sleeping
from src.actions.transfer import Transfer
from dotenv import load_dotenv

load_dotenv()

PRIVATE_KEY = os.environ.get("ADMIN_PKEY")
ACCOUNT_NAME = "admin wallet"


def main():
    results = []

    with open("data/airdropData.txt", "r") as f:
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
        with open("results/results.txt", "a") as f:
            for line in results:
                f.write(line + "\n")


if __name__ == "__main__":
    main()
