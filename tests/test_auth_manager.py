import pyotp
import auth_manager
from pathlib import Path


def test_create_and_auth_password(tmp_path, monkeypatch):
    monkeypatch.setattr(auth_manager, 'ACCOUNT_FILE', tmp_path / 'acc.json')
    acc = auth_manager.create_account('user', password='pass', enable_mfa=True)
    code = pyotp.TOTP(acc.mfa_secret).now()
    assert auth_manager.authenticate('user', password='pass', mfa_code=code)
    assert not auth_manager.authenticate('user', password='wrong', mfa_code=code)
    assert not auth_manager.authenticate('user', password='pass', mfa_code='000000')


def test_create_and_auth_key(tmp_path, monkeypatch):
    monkeypatch.setattr(auth_manager, 'ACCOUNT_FILE', tmp_path / 'acc.json')
    auth_manager.create_account('user', ssh_key='KEY')
    assert auth_manager.authenticate('user', ssh_key='KEY')
    assert not auth_manager.authenticate('user', ssh_key='BAD')
