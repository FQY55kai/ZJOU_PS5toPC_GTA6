# -*- coding: utf-8 -*-
"""AES-XTS via Git-for-Windows OpenSSL libcrypto-3-x64.dll (ctypes EVP).

Strict argtypes; verify with IEEE P1619 XTS-AES-128 vector 1, then use for PFS.
"""
import ctypes

DLL = r"C:\Program Files\Git\mingw64\bin\libcrypto-3-x64.dll"
lib = ctypes.CDLL(DLL)

V = ctypes.c_void_p
P = ctypes.POINTER

lib.EVP_CIPHER_CTX_new.restype = V
lib.EVP_CIPHER_CTX_free.argtypes = [V]
lib.EVP_CIPHER_CTX_set_padding.argtypes = [V, ctypes.c_int]
lib.EVP_aes_128_xts.restype = V
lib.EVP_aes_128_ecb.restype = V
for fn in ("EVP_EncryptInit_ex", "EVP_DecryptInit_ex"):
    getattr(lib, fn).argtypes = [V, V, V, ctypes.c_char_p, ctypes.c_char_p]
for fn in ("EVP_EncryptUpdate", "EVP_DecryptUpdate"):
    f = getattr(lib, fn)
    f.argtypes = [V, ctypes.c_char_p, P(ctypes.c_int), ctypes.c_char_p, ctypes.c_int]
    f.restype = ctypes.c_int

_ctx = lib.EVP_CIPHER_CTX_new()
lib.EVP_CIPHER_CTX_set_padding(_ctx, 0)


def _run(encrypt, key32, tweak16, data):
    cipher = lib.EVP_aes_128_xts()
    init = lib.EVP_EncryptInit_ex if encrypt else lib.EVP_DecryptInit_ex
    upd = lib.EVP_EncryptUpdate if encrypt else lib.EVP_DecryptUpdate
    # fresh ctx each call to avoid key/iv reuse quirks
    ctx = lib.EVP_CIPHER_CTX_new()
    lib.EVP_CIPHER_CTX_set_padding(ctx, 0)
    init(ctx, cipher, None, key32, tweak16)
    out = ctypes.create_string_buffer(len(data))
    n = ctypes.c_int(0)
    upd(ctx, out, ctypes.byref(n), bytes(data), len(data))
    lib.EVP_CIPHER_CTX_free(ctx)
    return out.raw[: n.value]


def xts_encrypt(key32, tweak16, data):
    """key32 = data_key(16) || tweak_key(16)  (OpenSSL EVP_aes_128_xts order)."""
    return _run(True, bytes(key32), bytes(tweak16), bytes(data))


def xts_decrypt(key32, tweak16, data):
    return _run(False, bytes(key32), bytes(tweak16), bytes(data))


def tweak_block(sector_num):
    return (sector_num & 0xFFFFFFFFFFFFFFFF).to_bytes(16, "little")


if __name__ == "__main__":
    k1 = bytes.fromhex("31415926535897932384626433832795")  # data key
    k2 = bytes.fromhex("27182818284590452353602874713526")  # tweak key
    expect = bytes.fromhex("d7b6dec55e1f1b1b10ee3c0d6ac92e57")
    got = xts_encrypt(k1 + k2, tweak_block(0), b"\x00" * 16)
    print("data||tweak:", got.hex(), "OK" if got == expect else "")
    got2 = xts_encrypt(k2 + k1, tweak_block(0), b"\x00" * 16)
    print("tweak||data:", got2.hex(), "OK" if got2 == expect else "")
