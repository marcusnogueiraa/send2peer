"""
side_b.py - Simula o "lado B" (quem recebe) da troca PAKE.

Rode side_a.py primeiro (outro terminal), depois este script,
na mesma pasta. Veja o comentario no topo de side_a.py para mais
contexto sobre o que esta acontecendo.
"""

import time
from pathlib import Path

from spake2 import SPAKE2_B
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

# Mesma senha do lado A -- em producao, essa e a senha curta que o
# usuario digita depois de receber o codigo do sender.
PASSWORD = b"8338-galileo-collect-fidel"

MSG_A_TO_B = Path("msg_a_to_b.bin")
MSG_B_TO_A = Path("msg_b_to_a.bin")


def main():
    print("[B] Iniciando protocolo SPAKE2 como lado B...")
    spake_b = SPAKE2_B(PASSWORD)

    # B tambem gera sua propria mensagem de saida, independente de
    # ja ter recebido algo de A (os dois lados comecam ao mesmo tempo)
    outbound_msg = spake_b.start()

    print("[B] Aguardando mensagem de A... (rode side_a.py primeiro)")
    while not MSG_A_TO_B.exists():
        time.sleep(0.3)
    inbound_msg = MSG_A_TO_B.read_bytes()

    MSG_B_TO_A.write_bytes(outbound_msg)
    print(f"[B] Mensagem enviada para A (salva em {MSG_B_TO_A})")

    # Assim como em A, finish() calcula a chave secreta final a partir
    # da mensagem recebida + do estado interno de B (que depende da
    # senha). Se as senhas dos dois lados baterem, as duas chaves
    # calculadas de forma independente vao ser IDENTICAS.
    shared_key_raw = spake_b.finish(inbound_msg)
    print(f"[B] Chave bruta derivada do PAKE: {shared_key_raw.hex()}")

    key = HKDF(
        algorithm=hashes.SHA256(),
        length=32,
        salt=None,
        info=b"send2peer-file-key",
    ).derive(shared_key_raw)
    print(f"[B] Chave final (AES-256): {key.hex()}")

    print("[B] Aguardando arquivo criptografado de A...")
    enc_file = Path("arquivo_criptografado.bin")
    while not enc_file.exists():
        time.sleep(0.3)

    decrypt_test_file(key, enc_file)


def decrypt_test_file(key: bytes, enc_file: Path):
    data = enc_file.read_bytes()
    nonce, ciphertext = data[:12], data[12:]

    aesgcm = AESGCM(key)
    plaintext = aesgcm.decrypt(nonce, ciphertext, None)

    print(f"[B] Arquivo decriptado com sucesso: {plaintext.decode()}")
    print("[B] Se voce ve a mensagem original acima, o PAKE funcionou!")


if __name__ == "__main__":
    main()