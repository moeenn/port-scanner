#! /bin/env python3

import argparse
import asyncio
import logging

from internal import PortScanner

logger = logging.getLogger("main")


async def main(host: str) -> None:
    scanner = PortScanner(host)
    target_ports = PortScanner.common_ports()
    results = await scanner.scan(target_ports)
    logger.info("scan complete")

    print("\n- Open Ports " + ("-" * 60))
    for result in results:
        if port := result.result():
            print(f"{port.name:20s}: {port.port}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    parser = argparse.ArgumentParser(
        prog="port-scanner", description="Simple port scanner"
    )
    parser.add_argument("-host", help="Host to target")
    args = parser.parse_args()

    asyncio.run(main(args.host))
