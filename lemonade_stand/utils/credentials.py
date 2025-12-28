""" """

from dataclasses import dataclass
from dataclasses import field


@dataclass
class ValidateCredentials:
    """ """

    username: bool
    password: bool
    invalid_credentials: list = field(default_factory=lambda: [], init=False)

    def __post_init__(self):
        """
        Post initialization variables set up
        """

        self.valid_credentials = [
            x
            for x in [
                None if self.username else "username",
                None if self.password else "password",
            ]
            if x is not None
        ]


def validate_user_credentials(username: str, userpassword: str):
    """ """

    return ValidateCredentials(
        username=(username in ["", "test"]),
        password=(userpassword in ["", "test"]),
    )
