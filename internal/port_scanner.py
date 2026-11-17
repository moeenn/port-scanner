import asyncio
import functools
import logging
from dataclasses import dataclass

logger = logging.getLogger("port-scanner")


@dataclass
class PortGroup:
    name: str
    ports: list[int]


@dataclass
class PortWithName:
    name: str
    port: int


def safe(func):
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except Exception as ex:
            logger.error(f"function {func.__name__} failed: {ex!r}")

    return wrapper


class PortScanner:
    __host: str
    __sem: asyncio.Semaphore

    def __init__(self, host: str, max_parallel=4) -> None:
        self.__host = host
        self.__sem = asyncio.Semaphore(max_parallel)

    @safe
    async def check_port_open(
        self, host: str, port: int, name: str, timeout_sec=2.0
    ) -> PortWithName | None:
        async with self.__sem:
            logger.info(f"scanning {host}:{port}")
            try:
                _, writer = await asyncio.wait_for(
                    asyncio.open_connection(host, port), timeout_sec
                )
                writer.close()
                await writer.wait_closed()
                return PortWithName(name, port)
            except (TimeoutError, OSError):
                return None

    async def scan(
        self, target_ports: list[PortGroup]
    ) -> list[asyncio.Task[PortWithName | None]]:
        results: list[asyncio.Task[PortWithName | None]] = []
        async with asyncio.TaskGroup() as tg:
            for group in target_ports:
                for port in group.ports:
                    result = tg.create_task(
                        self.check_port_open(
                            host=self.__host, port=port, name=group.name
                        )
                    )
                    results.append(result)

        return results

    @staticmethod
    def common_ports() -> list[PortGroup]:
        return [
            PortGroup("http/s", [80, 443]),
            PortGroup("ssh", [22, 2222, 22222]),
            PortGroup("postgresql", [5432]),
            PortGroup("mysql", [3306, 33060, 33062]),
            PortGroup("mongodb", [27017, 27018, 27019, 27020]),
            PortGroup("redis", [6379]),
            PortGroup("influx-db", [8086]),
            PortGroup("elastic-search", [9200]),
            PortGroup("rabbit-mq", [5672, 15672]),
            PortGroup("web-app", [3000, 5000, 8000, 8080, 9000]),
            PortGroup("prometheus", [9090]),
            PortGroup("loki", [3100, 9095]),
            PortGroup("tempo", [3200, 9096]),
            PortGroup("mimir", [9009, 9095]),
            PortGroup("grpc", [50051]),
            PortGroup("jupyter", [8888]),
        ]
