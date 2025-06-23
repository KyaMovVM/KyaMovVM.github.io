"""Simple backend interface for SSH commands and HTTP requests."""
import paramiko
import requests


def run_ssh_command(
    host: str,
    username: str,
    password: str,
    command: str,
) -> str:
    """Execute a command on a remote host via SSH and return its output."""
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(hostname=host, username=username, password=password)
    stdin, stdout, stderr = ssh.exec_command(command)
    output = stdout.read().decode()
    ssh.close()
    return output


def fetch_url(url: str) -> str:
    """Perform a GET request and return the response text."""
    response = requests.get(url)
    response.raise_for_status()
    return response.text


if __name__ == "__main__":
    # Example usage placeholders
    HOST = "example.com"
    USER = "user"
    PASSWORD = "password"
    print(run_ssh_command(HOST, USER, PASSWORD, "echo hello"))
    print(fetch_url("https://example.com"))
