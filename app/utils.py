import secrets
import string


def generate_api_key(length: int = 64) -> str:
    """Generate a secure random API key"""
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))


def format_command_result(command: str, status: str) -> str:
    """Format a mock command execution result"""
    return f"[MOCK] Command '{command}' would be executed with status: {status}"
