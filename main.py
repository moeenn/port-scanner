#! /bin/env python3

import argparse
import asyncio
import functools
import logging

logger = logging.getLogger("main")


def safe(func):
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except Exception as ex:
            logger.error(f"function {func.__name__} failed: {str(ex)}")

    return wrapper


@safe
async def check_port_open(
    sem: asyncio.Semaphore, host: str, port: int, timeout_sec=2.0
) -> int | None:
    async with sem:
        logger.info(f"scanning {host}:{port}")
        try:
            _, writer = await asyncio.wait_for(
                asyncio.open_connection(host, port), timeout_sec
            )
            writer.close()
            await writer.wait_closed()
            return port
        except (TimeoutError, OSError):
            return None


async def main(host: str) -> None:
    sem = asyncio.Semaphore(4)
    target_ports = [
        80,
        443,  # http/s
        22,  # ssh
        5432,  # postgresql
        3306,  # mysql
        33060,
        33062,
        27017,  # mongodb
        27018,
        27019,
        27020,
    ]

    results: list[asyncio.Task[int | None]] = []
    async with asyncio.TaskGroup() as tg:
        for port in target_ports:
            result = tg.create_task(check_port_open(sem, host=host, port=port))
            results.append(result)

    logger.info("scan complete")
    print("\n- Open Ports " + ("-" * 60))
    for result in results:
        if port := result.result():
            print(port)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    parser = argparse.ArgumentParser(
        prog="port-scanner", description="Simple port scanner"
    )
    parser.add_argument("-host", help="Host to target")
    args = parser.parse_args()

    asyncio.run(main(args.host))
