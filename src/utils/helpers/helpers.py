import time
import random
from loguru import logger


def sleeping(mode: int) -> None:
    match mode:
        case 1:
            t = random.randint(2, 5)
        case 2:
            t = random.randint(5, 10)
        case 3:
            t = random.randint(10, 15)
        case _:
            t = 1

    logger.info(f'Sleeping for {t} {"second" if t == 1 else "seconds"}...')
    time.sleep(t)
    return
