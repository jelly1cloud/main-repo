#!/usr/bin/env python3
"""
AtlasCryptoKit.py
CLI-інструмент для локальної роботи з Ethereum-сумісними гаманцями та транзакціями.

Функції:
- Генерація BIP-39 мнемонік і HD-адрес (m/44'/60'/0'/0/i)
- Імпорт приватного ключа
- Показ балансу ETH і ERC-20 токенів (через RPC)
- Створення, підпис та опціональне надсилання транзакцій
- Підпис повідомлення
- Локальна валідація хешів і підписів

Безпека: приватні ключі/мнемоніки ніколи не надсилаються в мережу автоматично.
"""

import os
import json
import argparse
import getpass
import secrets
from decimal import Decimal
from typing import Tuple

from mnemonic import Mnemonic
from eth_account import Account
from eth_account.messages import encode_defunct
from web3 import Web3
from web3.middleware import geth_poa_middleware

# Налаштування: змінюй на свій RPC лише коли впевнений
DEFAULT_RPC = "https://mainnet.infura.io/v3/YOUR_INFURA_KEY"  # замінити або передати через --rpc

# --- УТИЛІТИ ---


def safe_print(msg: str):
    print(msg)


def wei_to_eth(wei: int) -> Decimal:
    return Decimal(wei) / Decimal(10**18)


def eth_to_wei(amount_eth: Decimal) -> int:
    return int(amount_eth * Decimal(10**18'))


# --- ГАМАНЕЦЬ / HD ---


def generate_mnemonic(strength: int = 128) -> str:
    """Генерує BIP-39 мнемоніку (12/24 слів залежно від strength)."""
    mnemo = Mnemonic("english")
    return mnemo.generate(strength=strength)


def mnemonic_to_seed(mnemonic: str, passphrase: str = "") -> bytes:
    mnemo = Mnemonic("english")
    return mnemo.to_seed(mnemonic, passphrase=passphrase)


def derive_account_from_mnemonic(mnemonic: str, index: int = 0, passphrase: str = "") -> Tuple[str, str]:
    """
    Повертає (address, private_key_hex) -> HD derivation m/44'/60'/0'/0/index
    Ми використовуємо eth-account's Account.from_mnemonic якщо доступно,
    інакше робимо через встроєні засоби.
    """
    # eth-account recent versions підтримують from_mnemonic
    try:
        acct = Account.from_mnemonic(mnemonic, account_path=f"m/44'/60'/0'/0/{index}", passphrase=passphrase)
        return acct.address, acct.key.hex()
    except Exception:
        # fallback (рекомендуємо оновити eth-account)
        raise RuntimeError("Ваша версія eth-account не підтримує from_mnemonic. Оновіть пакет.")


# --- WEB3 ---


def make_web3(rpc_url: str, use_poa: bool = False) -> Web3:
    w3 = Web3(Web3.HTTPProvider(rpc_url))
    if use_poa:
        # для мереж типу BSC, Polygon (локальні PoA)
        w3.middleware_onion.inject(geth_poa_middleware, layer=0)
    if not w3.isConnected():
        raise ConnectionError(f"Не вдалось підключитись до RPC: {rpc_url}")
    return w3


def get_eth_balance(w3: Web3, address: str) -> Decimal:
    wei = w3.eth.get_balance(address)
    return wei_to_eth(wei)


# ERC-20 баланс через standard ABI (balanceOf)
ERC20_ABI_FRAGMENT = [
    {
        "constant": True,
        "inputs": [{"name": "_owner", "type": "address"}],
        "name": "balanceOf",
        "outputs": [{"name": "balance", "type": "uint256"}],
        "type": "function",
    },
    {
        "constant": True,
        "inputs": [],
        "name": "decimals",
        "outputs": [{"name": "", "type": "uint8"}],
        "type": "function",
    },
    {
        "constant": True,
        "inputs": [],
        "name": "symbol",
        "outputs": [{"name": "", "type": "string"}],
        "type": "function",
    },
]


def get_erc20_balance(w3: Web3, token_address: str, user_address: str) -> Tuple[Decimal, int, str]:
    contract = w3.eth.contract(address=w3.toChecksumAddress(token_address), abi=ERC20_ABI_FRAGMENT)
    raw = contract.functions.balanceOf(w3.toChecksumAddress(user_address)).call()
    try:
        decimals = contract.functions.decimals().call()
    except Exception:
        decimals = 18
    try:
        symbol = contract.functions.symbol().call()
    except Exception:
        symbol = ""
    scaled = Decimal(raw) / Decimal(10**decimals)
    return scaled, decimals, symbol


# --- ТРАНЗАКЦІЇ ---


def build_eth_transaction(w3: Web3, from_address: str, to_address: str, value_eth: Decimal, gas: int = None,
                          gas_price_gwei: Decimal = None, max_priority_fee_gwei: Decimal = None, max_fee_gwei: Decimal = None,
                          nonce: int = None, chain_id: int = None) -> dict:
    """
    Створює словник транзакції (EIP-1559 якщо задано max_fee/max_priority).
    Параметри gas/gas_price можуть бути None (буде використано estimate / suggest).
    """
    from_checksum = w3.toChecksumAddress(from_address)
    to_checksum = w3.toChecksumAddress(to_address)

    if nonce is None:
        nonce = w3.eth.get_transaction_count(from_checksum)

    tx = {
        "from": from_checksum,
        "to": to_checksum,
        "value": int(value_eth * Decimal(10**18)),
        "nonce": nonce,
        "chainId": chain_id or w3.eth.chain_id,
    }

    # EIP-1559
    if max_fee_gwei is not None and max_priority_fee_gwei is not None:
        tx["type"] = "0x2"
        tx["maxFeePerGas"] = int(max_fee_gwei * Decimal(10**9))
        tx["maxPriorityFeePerGas"] = int(max_priority_fee_gwei * Decimal(10**9))
        if gas is None:
            tx["gas"] = w3.eth.estimate_gas({k: v for k, v in tx.items() if k in ("to", "value", "from")})
        else:
            tx["gas"] = gas
    else:
        # legacy
        if gas_price_gwei is None:
            gas_price = w3.eth.gas_price
        else:
            gas_price = int(gas_price_gwei * Decimal(10**9))
        tx["gasPrice"] = gas_price
        if gas is None:
            tx["gas"] = w3.eth.estimate_gas({"to": to_checksum, "from": from_checksum, "value": tx["value"]})
        else:
            tx["gas"] = gas

    return tx


def sign_transaction(account_private_key_hex: str, tx: dict, w3: Web3) -> dict:
    acct = Account.from_key(account_private_key_hex)
    signed = acct.sign_transaction(tx)
    return signed


def send_signed_transaction(w3: Web3, signed_txn) -> str:
    tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
    return tx_hash.hex()


# --- ПІДПИС ПОВІДОМЛЕННЯ ---


def sign_message(private_key_hex: str, message: str) -> dict:
    acct = Account.from_key(private_key_hex)
    msg = encode_defunct(text=message)
    signed = acct.sign_message(msg)
    return {"message": message, "signature": signed.signature.hex(), "address": signed.address}


def verify_message(signature_hex: str, message: str, w3: Web3) -> str:
    msg = encode_defunct(text=message)
    signer = w3.eth.account.recover_message(msg, signature=signature_hex)
    return signer


# --- CLI / RUN ---


def cmd_generate(args):
    strength = 128 if not args.long else 256
    mnemonic = generate_mnemonic(strength=strength)
    safe_print("=== MNEMONIC (KEEP IT SECRET!) ===")
    safe_print(mnemonic)
    safe_print("")
    safe_print("Deriving first 3 addresses:")
    for i in range(3):
        addr, pk = derive_account_from_mnemonic(mnemonic, index=i, passphrase=args.passphrase or "")
        safe_print(f"[{i}] {addr}  (private key HIDDEN)")
    safe_print("\nЗбережіть мнемоніку у безпечному місці.")


def cmd_derive(args):
    mnemonic = args.mnemonic
    if not mnemonic:
        mnemonic = getpass.getpass("Введіть мнемоніку: ")
    for i in range(args.count):
        addr, pk = derive_account_from_mnemonic(mnemonic, index=i, passphrase=args.passphrase or "")
        safe_print(f"{i}: {addr}  (privkey: {pk})")


def cmd_balance(args):
    w3 = make_web3(args.rpc, use_poa=args.poa)
    addr = w3.toChecksumAddress(args.address)
    eth_bal = get_eth_balance(w3, addr)
    safe_print(f"ETH balance of {addr}: {eth_bal} ETH")
    if args.erc20:
        for t in args.erc20:
            bal, decs, sym = get_erc20_balance(w3, t, addr)
            safe_print(f"Token {sym or t} balance: {bal} (decimals: {decs})")


def cmd_send(args):
    w3 = make_web3(args.rpc, use_poa=args.poa)
    # приватний ключ з environment або введи вручну
    if args.privkey:
        priv = args.privkey
    else:
        priv = getpass.getpass("Введіть приватний ключ (0x...): ").strip()
    acct = Account.from_key(priv)
    from_addr = acct.address
    to = args.to
    value = Decimal(args.value)
    chain_id = args.chain_id or w3.eth.chain_id

    # Параметри газу
    tx = build_eth_transaction(
        w3,
        from_addr,
        to,
        value_eth=value,
        gas=args.gas,
        gas_price_gwei=Decimal(args.gas_price) if args.gas_price else None,
        max_priority_fee_gwei=Decimal(args.max_priority_fee) if args.max_priority_fee else None,
        max_fee_gwei=Decimal(args.max_fee) if args.max_fee else None,
        nonce=args.nonce,
        chain_id=chain_id
    )

    safe_print("Transaction preview:")
    safe_print(json.dumps(tx, indent=2))
    confirm = input("Підписати і відправити? (yes/no): ").strip().lower()
    if confirm not in ("yes", "y"):
        safe_print("Скасовано.")
        return

    signed = sign_transaction(priv, tx, w3)
    tx_hash = send_signed_transaction(w3, signed)
    safe_print(f"Sent. tx hash: {tx_hash}")


def cmd_sign_msg(args):
    if args.privkey:
        priv = args.privkey
    else:
        priv = getpass.getpass("Введіть приватний ключ (0x...): ").strip()
    res = sign_message(priv, args.message)
    safe_print("Signed message:")
    safe_print(json.dumps(res, indent=2))


def cmd_verify_msg(args):
    w3 = make_web3(args.rpc, use_poa=args.poa)
    signer = verify_message(args.signature, args.message, w3)
    safe_print(f"Recovered signer: {signer}")


def build_parser():
    p = argparse.ArgumentParser(description="AtlasCryptoKit — локальний крипто-тул для Ethereum-сумісних мереж")
    p.add_argument("--rpc", type=str, default=os.environ.get("ATLAS_RPC", DEFAULT_RPC), help="RPC URL")
    p.add_argument("--poa", action="store_true", help="Enable POA middleware (BSC/Polygon)")
    sub = p.add_subparsers(dest="cmd")

    g = sub.add_parser("generate", help="Генерувати BIP39 мнемоніку")
    g.add_argument("--long", action="store_true", help="24 слова (256 біт)")
    g.add_argument("--passphrase", type=str, help="BIP39 passphrase (optional)")
    g.set_defaults(func=cmd_generate)

    d = sub.add_parser("derive", help="Деривувати адреси з мнемоніки")
    d.add_argument("--mnemonic", type=str, help="Передати мнемоніку як аргумент (небезпечно)")
    d.add_argument("--count", type=int, default=5, help="Кількість адрес для деривації")
    d.add_argument("--passphrase", type=str, help="passphrase якщо потрібна")
    d.set_defaults(func=cmd_derive)

    b = sub.add_parser("balance", help="Перевірити баланс ETH та ERC-20")
    b.add_argument("address", type=str, help="Адреса для перевірки")
    b.add_argument("--erc20", nargs="*", help="Списком адреси контрактів ERC20")
    b.set_defaults(func=cmd_balance)

    s = sub.add_parser("send", help="Створити, підписати і (опційно) відправити транзакцію")
    s.add_argument("--to", required=True, help="Куди відправляти")
    s.add_argument("--value", required=True, help="Сума у ETH (наприклад 0.01)")
    s.add_argument("--privkey", help="Приватний ключ (0x...) (НЕ РЕКОМЕНДУЄТЬСЯ в аргументах)")
    s.add_argument("--gas", type=int, help="Gas limit")
    s.add_argument("--gas_price", help="legacy gas price у Gwei")
    s.add_argument("--max_fee", help="EIP-1559 maxFeePerGas у Gwei")
    s.add_argument("--max_priority_fee", help="EIP-1559 maxPriorityFeePerGas у Gwei")
    s.add_argument("--nonce", type=int, help="Nonce (опціонально)")
    s.add_argument("--chain-id", type=int, dest="chain_id", help="chainId (опціонально)")
    s.set_defaults(func=cmd_send)

    sm = sub.add_parser("signmsg", help="Підписати текстове повідомлення (eth_sign)")
    sm.add_argument("--message", required=True, help="Текст повідомлення")
    sm.add_argument("--privkey", help="Приватний ключ (0x...)")
    sm.set_defaults(func=cmd_sign_msg)

    vm = sub.add_parser("verifymsg", help="Відновити підписанта по повідомленню і підпису")
    vm.add_argument("--message", required=True)
    vm.add_argument("--signature", required=True, help="Hex підпис")
    vm.set_defaults(func=cmd_verify_msg)

    return p


def main():
    parser = build_parser()
    args = parser.parse_args()
    if not hasattr(args, "func"):
        parser.print_help()
        return
    try:
        args.func(args)
    except Exception as e:
        safe_print(f"Помилка: {e}")


if __name__ == "__main__":
    main()
