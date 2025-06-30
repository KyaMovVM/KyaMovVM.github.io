import json
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Optional, Dict
import pyotp

ACCOUNT_FILE = Path(__file__).with_name("accounts.json")


@dataclass
class Account:
    username: str
    password: str = ""
    ssh_key: str = ""
    mfa_secret: str = ""


def load_accounts() -> Dict[str, Account]:
    if ACCOUNT_FILE.exists():
        data = json.loads(ACCOUNT_FILE.read_text(encoding="utf-8"))
        return {u: Account(**v) for u, v in data.items()}
    return {}


def save_accounts(accounts: Dict[str, Account]) -> None:
    data = {u: asdict(a) for u, a in accounts.items()}
    ACCOUNT_FILE.write_text(
        json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8"
    )


def create_account(
    username: str, password: str = "", ssh_key: str = "", enable_mfa: bool = False
) -> Account:
    accounts = load_accounts()
    secret = pyotp.random_base32() if enable_mfa else ""
    acc = Account(
        username=username, password=password, ssh_key=ssh_key, mfa_secret=secret
    )
    accounts[username] = acc
    save_accounts(accounts)
    return acc


def get_account(username: str) -> Optional[Account]:
    return load_accounts().get(username)


def verify_mfa(acc: Account, code: str) -> bool:
    if not acc.mfa_secret:
        return True
    totp = pyotp.TOTP(acc.mfa_secret)
    return totp.verify(code)


def authenticate(
    username: str, password: str = "", ssh_key: str = "", mfa_code: str = ""
) -> bool:
    acc = get_account(username)
    if not acc:
        return False
    if password:
        if password != acc.password:
            return False
    elif ssh_key:
        if ssh_key.strip() != acc.ssh_key.strip():
            return False
    else:
        return False
    return verify_mfa(acc, mfa_code)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Account management")
    sub = parser.add_subparsers(dest="cmd")

    c = sub.add_parser("create")
    c.add_argument("username")
    c.add_argument("--password")
    c.add_argument("--ssh-key")
    c.add_argument("--mfa", action="store_true")

    a = sub.add_parser("auth")
    a.add_argument("username")
    a.add_argument("--password")
    a.add_argument("--ssh-key")
    a.add_argument("--mfa-code", default="")

    args = parser.parse_args()

    if args.cmd == "create":
        acc = create_account(
            args.username, args.password or "", args.ssh_key or "", args.mfa
        )
        print("Аккаунт создан")
        if acc.mfa_secret:
            print("MFA secret:", acc.mfa_secret)
            print("Текущий код:", pyotp.TOTP(acc.mfa_secret).now())
    elif args.cmd == "auth":
        ok = authenticate(
            args.username, args.password or "", args.ssh_key or "", args.mfa_code
        )
        print("Успешно" if ok else "Ошибка аутентификации")
    else:
        parser.print_help()
