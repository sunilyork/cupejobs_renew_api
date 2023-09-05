import pytest

from apps.lib.helper import decrypt_message, encrypt_message, is_valid_password


def test_decrypt_message(mocker):
    encrypted_value1 = encrypt_message("test")
    encrypted_value2 = encrypt_message("test")
    assert encrypted_value1 is not None
    assert encrypted_value2 is not None
    decrypted_value1 = decrypt_message(encrypted_value1)
    decrypted_value2 = decrypt_message(encrypted_value2)
    assert decrypted_value1 == decrypted_value2


@pytest.mark.parametrize("password", ["Abcdefgh1*", "!CupeUser1"])
def test_is_valid_password_should_pass(password):
    assert is_valid_password(password) is True


@pytest.mark.parametrize(
    "password",
    [
        "",
        None,
        "Abcdefgh1",
        12312312312,
        "abcdefgh1*",
        "cupeuser1!",
        "CUPEUSER1!",
        "CupeUser11",
        "CupeUser!!",
        "1234567890Abcdefgh1*",
        "Abcdefgh1*Abcdefgh1*",
        "           ",
    ],
)
def test_is_valid_password_should_fail(password):
    assert is_valid_password(password) is False
