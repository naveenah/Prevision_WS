"""
Encryption utilities for securing OAuth tokens at rest.

Uses Fernet symmetric encryption from the cryptography library.
The encryption key is derived from Django's SECRET_KEY.
"""
import base64
import hashlib
import logging
from functools import lru_cache

from django.conf import settings

logger = logging.getLogger(__name__)

# Try to import cryptography, but provide fallback for dev environments
try:
    from cryptography.fernet import Fernet, InvalidToken
    ENCRYPTION_AVAILABLE = True
except ImportError:
    ENCRYPTION_AVAILABLE = False
    logger.warning("cryptography package not installed. Token encryption disabled.")


@lru_cache(maxsize=1)
def get_encryption_key() -> bytes:
    """
    Derive a Fernet-compatible encryption key from Django's SECRET_KEY.
    
    Fernet requires a 32-byte base64-encoded key. We derive this from
    the SECRET_KEY using SHA-256 and base64 encoding.
    """
    # Use SECRET_KEY as the basis for encryption
    secret = settings.SECRET_KEY.encode('utf-8')
    
    # Create a 32-byte key using SHA-256
    key_hash = hashlib.sha256(secret).digest()
    
    # Fernet requires a URL-safe base64-encoded 32-byte key
    return base64.urlsafe_b64encode(key_hash)


def get_fernet():
    """Get a Fernet instance for encryption/decryption."""
    if not ENCRYPTION_AVAILABLE:
        return None
    return Fernet(get_encryption_key())


def encrypt_token(plaintext: str) -> str:
    """
    Encrypt a token string for secure storage.
    
    Args:
        plaintext: The token to encrypt
        
    Returns:
        The encrypted token as a base64 string, or the original plaintext
        if encryption is not available.
    """
    if not plaintext:
        return plaintext
    
    if not ENCRYPTION_AVAILABLE:
        # In dev mode without cryptography, return as-is with marker
        logger.debug("Encryption not available, storing token in plaintext")
        return plaintext
    
    try:
        fernet = get_fernet()
        encrypted = fernet.encrypt(plaintext.encode('utf-8'))
        # Prefix with 'enc:' to identify encrypted values
        return f"enc:{encrypted.decode('utf-8')}"
    except Exception as e:
        logger.error(f"Failed to encrypt token: {e}")
        # Fall back to plaintext if encryption fails
        return plaintext


def decrypt_token(ciphertext: str) -> str:
    """
    Decrypt an encrypted token.
    
    Args:
        ciphertext: The encrypted token
        
    Returns:
        The decrypted plaintext token, or the original value if
        it's not encrypted or decryption fails.
    """
    if not ciphertext:
        return ciphertext
    
    # Check if this is an encrypted value
    if not ciphertext.startswith('enc:'):
        # Not encrypted, return as-is
        return ciphertext
    
    if not ENCRYPTION_AVAILABLE:
        logger.warning("Cannot decrypt token - cryptography package not installed")
        # Return without the prefix (will likely fail to use, but safe)
        return ciphertext[4:]
    
    try:
        fernet = get_fernet()
        encrypted_data = ciphertext[4:].encode('utf-8')  # Remove 'enc:' prefix
        decrypted = fernet.decrypt(encrypted_data)
        return decrypted.decode('utf-8')
    except InvalidToken:
        logger.error("Invalid token or wrong encryption key")
        return ""
    except Exception as e:
        logger.error(f"Failed to decrypt token: {e}")
        return ""


def is_encrypted(value: str) -> bool:
    """Check if a value is encrypted."""
    return value.startswith('enc:') if value else False
