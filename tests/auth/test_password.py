"""Tests for password hashing and verification."""
from app.auth.password import hash_password, verify_password


def test_hash_password():
    """Test password hashing."""
    password = "testpassword123"
    hashed = hash_password(password)

    # Hash should be different from plain password
    assert hashed != password

    # Hash should be a string
    assert isinstance(hashed, str)

    # Hash should contain argon2 identifier
    assert hashed.startswith("$argon2")


def test_verify_password_success():
    """Test password verification with correct password."""
    password = "testpassword123"
    hashed = hash_password(password)

    # Verification should succeed
    assert verify_password(password, hashed) is True


def test_verify_password_failure():
    """Test password verification with incorrect password."""
    password = "testpassword123"
    wrong_password = "wrongpassword456"
    hashed = hash_password(password)

    # Verification should fail
    assert verify_password(wrong_password, hashed) is False


def test_hash_password_uniqueness():
    """Test that same password produces different hashes (salt)."""
    password = "testpassword123"
    hash1 = hash_password(password)
    hash2 = hash_password(password)

    # Hashes should be different due to salt
    assert hash1 != hash2

    # But both should verify correctly
    assert verify_password(password, hash1) is True
    assert verify_password(password, hash2) is True
