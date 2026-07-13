"""
side_a.py - Simula o "lado A" (quem envia) da troca PAKE.

O que este script faz:
1. Roda o protocolo SPAKE2 até chegar numa chave secreta compartilhada
   com o lado B -- sem nunca transmitir a senha nem a chave pela rede.
2. Usa essa chave pra criptografar um arquivo de teste.

Como rodar:
    Terminal 1: uv run side_a.py
    Terminal 2: uv run side_b.py   (na mesma pasta)

Os dois "conversam" através de arquivos temporários (msg_a_to_b.bin e
msg_b_to_a.bin), simulando a troca manual de mensagens que, no projeto
de verdade, vai passar pelo relay/rede.
"""

import os
import time
from pathlib import Path

from spake2 import SPAKE2_A
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

# A "senha" que os dois lados compartilham. No mundo real essa e a
# senha curta tipo "8338-galileo-collect-fidel" que o sender gera e
# fala pro receiver (por WhatsApp, viva-voz, etc). Aqui e fixa so
# para fins de teste. Os dois scripts precisam usar o MESMO valor.
PASSWORD = b"8338-galileo-collect-fidel"

MSG_A_TO_B = Path("msg_a_to_b.bin")
MSG_B_TO_A = Path("msg_b_to_a.bin")


def main():
    # limpa arquivos de uma rodada anterior, pra nao misturar sessoes
    MSG_A_TO_B.unlink(missing_ok=True)
    MSG_B_TO_A.unlink(missing_ok=True)
    Path("arquivo_criptografado.bin").unlink(missing_ok=True)

    print("[A] Iniciando protocolo SPAKE2 como lado A...")
    spake_a = SPAKE2_A(PASSWORD)

    # start() gera a mensagem que A vai "mandar" pra B. Essa mensagem,
    # sozinha, NAO revela a senha nem a chave final -- e por isso que
    # da pra deixar alguem espionar essa troca sem problema.
    outbound_msg = spake_a.start()
    MSG_A_TO_B.write_bytes(outbound_msg)
    print(f"[A] Mensagem enviada para B (salva em {MSG_A_TO_B})")

    print("[A] Aguardando mensagem de B... (rode side_b.py agora)")
    while not MSG_B_TO_A.exists():
        time.sleep(0.3)

    inbound_msg = MSG_B_TO_A.read_bytes()

    # finish() combina a mensagem recebida de B com o estado interno
    # de A (que depende da senha) e calcula a chave secreta final.
    # Se alguem tentasse fazer isso sem saber a senha certa, a conta
    # nao ia bater e a chave final seria diferente da de B.
    shared_key_raw = spake_a.finish(inbound_msg)
    print(f"[A] Chave bruta derivada do PAKE: {shared_key_raw.hex()}")

    # Boa pratica: passar a chave bruta por um KDF (HKDF) antes de
    # usar em criptografia simetrica, pra "padronizar" a chave num
    # formato ideal pro AES (32 bytes = AES-256).
    key = HKDF(
        algorithm=hashes.SHA256(),
        length=32,
        salt=None,
        info=b"send2peer-file-key",
    ).derive(shared_key_raw)
    print(f"[A] Chave final (AES-256): {key.hex()}")

    encrypt_test_file(key)


def encrypt_test_file(key: bytes):
    test_content = b"Ola, este eh um arquivo secreto enviado via send2peer!"
    Path("original.txt").write_bytes(test_content)

    aesgcm = AESGCM(key)
    nonce = os.urandom(12)  # nonce precisa ser unico a cada criptografia
    ciphertext = aesgcm.encrypt(nonce, test_content, None)

    # salva nonce + ciphertext juntos, o receptor precisa do nonce
    # pra conseguir decriptar
    Path("arquivo_criptografado.bin").write_bytes(nonce + ciphertext)
    print("[A] Arquivo de teste criptografado -> arquivo_criptografado.bin")
    print("[A] Concluido. Confira o resultado no terminal do lado B.")


if __name__ == "__main__":
    main()