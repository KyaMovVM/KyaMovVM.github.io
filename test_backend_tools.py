import sys
import types
import unittest
from unittest.mock import MagicMock, patch

# Provide fake modules for paramiko and requests if they are missing
if 'paramiko' not in sys.modules:
    sys.modules['paramiko'] = types.ModuleType('paramiko')
    sys.modules['paramiko'].SSHClient = object
    sys.modules['paramiko'].AutoAddPolicy = object
if 'requests' not in sys.modules:
    sys.modules['requests'] = types.ModuleType('requests')
    sys.modules['requests'].get = lambda *args, **kwargs: None
if 'cuda' not in sys.modules:
    sys.modules['cuda'] = types.ModuleType('cuda')
    sys.modules['cuda'].cuInit = lambda x: None
    sys.modules['cuda'].cuDeviceGetCount = lambda: 0
    sys.modules['cuda'].cuDeviceGet = lambda i: None
    sys.modules['cuda'].cuDeviceGetName = lambda dev: 'mock'

import backend_tools

class TestBackendTools(unittest.TestCase):
    @patch('backend_tools.paramiko.SSHClient')
    def test_run_ssh_command(self, mock_sshclient):
        mock_client = MagicMock()
        mock_sshclient.return_value = mock_client
        mock_stdout = MagicMock()
        mock_stdout.read.return_value = b'hello\n'
        mock_client.exec_command.return_value = (None, mock_stdout, None)
        result = backend_tools.run_ssh_command('host', 'user', 'pass', 'echo hello')
        self.assertEqual(result, 'hello\n')
        mock_client.connect.assert_called_with(hostname='host', username='user', password='pass')
        mock_client.exec_command.assert_called_with('echo hello')
        mock_client.close.assert_called()

    @patch('backend_tools.requests.get')
    def test_fetch_url(self, mock_get):
        mock_response = MagicMock()
        mock_response.text = 'ok'
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response
        result = backend_tools.fetch_url('https://example.com')
        self.assertEqual(result, 'ok')
        mock_get.assert_called_with('https://example.com')
        mock_response.raise_for_status.assert_called()

    def test_list_cuda_devices(self):
        self.assertEqual(backend_tools.list_cuda_devices(), [])

if __name__ == '__main__':
    unittest.main()
