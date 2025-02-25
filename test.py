from ecdsa import SigningKey, VerifyingKey, NIST256p, BadSignatureError
import hashlib

# Generate a new ECDSA key pair
def generate_keys():
    private_key = SigningKey.generate(curve=NIST256p)
    public_key = private_key.get_verifying_key()
    return private_key, public_key

# Sign a message using the private key
def sign_message(message, private_key):
    message_hash = hashlib.sha256(message.encode()).digest()
    signature = private_key.sign(message_hash)
    signature_hex = signature.hex()
    return signature_hex

# Verify a signature using the public key
def verify_signature(message, signature_hex, public_key):
    message_hash = hashlib.sha256(message.encode()).digest()
    signature = bytes.fromhex(signature_hex)
    try:
        return public_key.verify(signature, message_hash)
    except BadSignatureError:
        return False
    except Exception as e:
        print(f"Verification error: {e}")
        return False

# Encode the public key to a hex string
def encode_public_key(public_key):
    public_key_bytes = public_key.to_string()
    public_key_hex = public_key_bytes.hex()
    return public_key_hex

# Decode the public key from a hex string
def decode_public_key(public_key_hex):
    public_key_bytes = bytes.fromhex(public_key_hex)
    public_key = VerifyingKey.from_string(public_key_bytes, curve=NIST256p)
    return public_key

# Main test function
def test_signing_verification():
    # Step 1: Generate keys
    private_key, public_key = generate_keys()
    print("Private key generated.")
    print("Public key generated.")

    # Step 2: Encode the public key to hex (simulate storage/transmission)
    public_key_hex = encode_public_key(public_key)
    print(f"Public key (hex): {public_key_hex}")

    # Step 3: Sign a message
    message = "This is a test message."
    signature_hex = sign_message(message, private_key)
    print(f"Message: {message}")
    print(f"Signature (hex): {signature_hex}")

    # Step 4: Decode the public key from hex (simulate retrieval)
    public_key_decoded = decode_public_key(public_key_hex)
    print("Public key decoded from hex.")

    # Step 5: Verify the signature
    is_valid = verify_signature(message, signature_hex, public_key_decoded)
    print(f"Signature valid: {is_valid}")

    # Step 6: Attempt verification with a wrong message
    wrong_message = "This is a tampered message."
    is_valid_wrong = verify_signature(wrong_message, signature_hex, public_key_decoded)
    print(f"Signature valid with wrong message: {is_valid_wrong}")

    # Step 7: Attempt verification with a wrong signature
    wrong_signature_hex = "00" * len(signature_hex)
    is_valid_wrong_sig = verify_signature(message, wrong_signature_hex, public_key_decoded)
    print(f"Signature valid with wrong signature: {is_valid_wrong_sig}")

if __name__ == "__main__":
    test_signing_verification()
