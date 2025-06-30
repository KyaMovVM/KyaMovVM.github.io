"""Скрипт для создания и проверки учетных записей."""

import argparse
import pyotp
import auth_manager


def main() -> None:
    parser = argparse.ArgumentParser(description="Управление учётными записями")
    sub = parser.add_subparsers(dest="cmd")

    create_p = sub.add_parser("create", help="Создать учётную запись")
    create_p.add_argument("username")
    create_p.add_argument("--password")
    create_p.add_argument("--ssh-key")
    create_p.add_argument("--mfa", action="store_true")

    test_p = sub.add_parser("test", help="Проверить вход")
    test_p.add_argument("username")
    test_p.add_argument("--password")
    test_p.add_argument("--ssh-key")
    test_p.add_argument("--mfa-code")

    args = parser.parse_args()

    if args.cmd == "create":
        acc = auth_manager.create_account(
            args.username,
            password=args.password or "",
            ssh_key=args.ssh_key or "",
            enable_mfa=args.mfa,
        )
        print("Учётка создана")
        if acc.mfa_secret:
            totp = pyotp.TOTP(acc.mfa_secret)
            print("MFA secret:", acc.mfa_secret)
            print("Текущий код:", totp.now())
    elif args.cmd == "test":
        ok = auth_manager.authenticate(
            args.username,
            password=args.password or "",
            ssh_key=args.ssh_key or "",
            mfa_code=args.mfa_code or "",
        )
        print("Успех" if ok else "Не удалось войти")
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
