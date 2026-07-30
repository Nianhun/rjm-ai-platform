import os
import unittest
from unittest.mock import patch

from rjm_formula_ai.http_server import (
    _ai_http_client_from_environment,
    _load_local_env_file,
    runtime_config_diagnostics,
    server_config_from_environment,
)


class HttpServerConfigTest(unittest.TestCase):
    def test_reads_host_and_port_from_environment(self):
        with patch.dict(os.environ, {"RJM_HTTP_HOST": "0.0.0.0", "RJM_HTTP_PORT": "9001"}):
            host, port = server_config_from_environment()

        self.assertEqual("0.0.0.0", host)
        self.assertEqual(9001, port)

    def test_defaults_to_java_configured_python_port(self):
        with patch.dict(os.environ, {}, clear=True):
            host, port = server_config_from_environment()

        self.assertEqual("127.0.0.1", host)
        self.assertEqual(8000, port)

    def test_loads_local_env_and_overrides_yuxi_runtime_keys(self):
        from tempfile import TemporaryDirectory
        from pathlib import Path

        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / ".env.local").write_text(
                "RJM_YUXI_GRAPH_ENABLED=true\nRJM_YUXI_API_TOKEN=file-token\nRJM_HTTP_PORT=8010\n",
                encoding="utf-8",
            )
            with patch.dict(
                os.environ,
                {
                    "RJM_HTTP_PORT": "9002",
                    "RJM_YUXI_GRAPH_ENABLED": "false",
                    "RJM_YUXI_API_TOKEN": "",
                },
                clear=True,
            ):
                _load_local_env_file(root)

                self.assertEqual("true", os.environ["RJM_YUXI_GRAPH_ENABLED"])
                self.assertEqual("file-token", os.environ["RJM_YUXI_API_TOKEN"])
                self.assertEqual("9002", os.environ["RJM_HTTP_PORT"])

    def test_runtime_config_diagnostics_masks_secret_values(self):
        from tempfile import TemporaryDirectory
        from pathlib import Path

        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / ".env.local").write_text(
                "RJM_YUXI_GRAPH_ENABLED=true\nRJM_YUXI_API_TOKEN=secret-token\nRJM_AI_API_KEY=secret-key\nRJM_AI_BASE_URL=http://ai.example\nRJM_AI_MODEL=deepseek\n",
                encoding="utf-8",
            )
            with patch.dict(os.environ, {}, clear=True):
                payload = runtime_config_diagnostics(root)

        self.assertTrue(payload["env_file_exists"])
        self.assertTrue(payload["yuxi_graph_enabled"])
        self.assertTrue(payload["yuxi_api_token_configured"])
        self.assertTrue(payload["ai_provider_configured"])
        self.assertNotIn("secret-token", str(payload))
        self.assertNotIn("secret-key", str(payload))

    def test_loads_local_env_with_utf8_bom(self):
        from tempfile import TemporaryDirectory
        from pathlib import Path

        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / ".env.local").write_text("\ufeffRJM_YUXI_GRAPH_ENABLED=true\n", encoding="utf-8")
            with patch.dict(os.environ, {"RJM_YUXI_GRAPH_ENABLED": "false"}, clear=True):
                _load_local_env_file(root)

                self.assertEqual("true", os.environ["RJM_YUXI_GRAPH_ENABLED"])

    def test_ai_http_client_defaults_to_curl_on_windows(self):
        with patch.dict(os.environ, {}, clear=True), patch("rjm_formula_ai.http_server.os.name", "nt"):
            self.assertEqual("curl", _ai_http_client_from_environment())

    def test_ai_http_client_uses_explicit_override(self):
        with patch.dict(os.environ, {"RJM_AI_HTTP_CLIENT": "python"}, clear=True), patch("rjm_formula_ai.http_server.os.name", "nt"):
            self.assertEqual("python", _ai_http_client_from_environment())


if __name__ == "__main__":
    unittest.main()
