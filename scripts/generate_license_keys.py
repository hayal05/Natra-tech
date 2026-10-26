"""One-time license signing keypair generator. Keep private seed secret."""
import base64
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

def b64(b):
    return base64.urlsafe_b64encode(b).rstrip(b"=").decode("ascii")

key = Ed25519PrivateKey.generate()
seed = key.private_bytes(serialization.Encoding.Raw, serialization.PrivateFormat.Raw,
                         serialization.NoEncryption())
pub = key.public_key().public_bytes(serialization.Encoding.Raw,
                                    serialization.PublicFormat.Raw)
print("NATRA_LICENSE_PRIVATE_KEY=" + b64(seed))
print("OFFLINE_APP_PUBLIC_KEY=" + b64(pub))
print("Store the private key ONLY in Render environment variables; embed ONLY the public key in the desktop app.")
