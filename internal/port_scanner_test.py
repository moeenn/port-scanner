from unittest import TestCase

from internal.port_scanner import PortScanner


class TestPortScanner(TestCase):
    def test_common_ports_unique(self) -> None:
        ports = PortScanner.common_ports()
        already_seen = set[int]()
        for group in ports:
            for port in group.ports:
                self.assertFalse(port in already_seen, f"port {port} already exists")
                already_seen.add(port)
