import os
import unittest
from unittest.mock import patch

from rjm_formula_ai.http_server import server_config_from_environment


class HttpServerConfigTest(unittest.TestCase):
    def test_reads_host_and_port_from_environment(self):
        with patch.dict(os.environ, {"RJM_HTTP_HOST": "0.0.0.0", "RJM_HTTP_PORT": "9001"}):
            host, port = server_config_from_environment()

        self.assertEqual("0.0.0.0", host)
        self.assertEqual(9001, port)

    def test_defaults_to_existing_local_smoke_port(self):
        with patch.dict(os.environ, {}, clear=True):
            host, port = server_config_from_environment()

        self.assertEqual("127.0.0.1", host)
        self.assertEqual(8787, port)


if __name__ == "__main__":
    unittest.main()
