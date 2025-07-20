import os

from email_validator import EmailNotValidError, validate_email


class EmailConfig:
    """
    email config data
    # https://support.google.com/a/answer/176600?hl=en
    """

    ENABLE_KEY = "enable"
    HOST_KEY = "smtp_host"
    PORT_KEY = "smtp_port"
    USERNAME_KEY = "username"
    PASSWORD_KEY = "password"
    FROM_EMAIL_KEY = "from_email"
    TO_EMAIL_KEY = "to_email"

    # envars placed in /etc/environment and not in user space
    USERNAME_ENVAR = "WW_EMAIL_USERNAME"
    PASSWORD_ENVAR = "WW_EMAIL_PASSWORD"

    def __init__(self, config: dict):
        """
        ctor
        :param self: this
        """
        for key in config:
            self.__dict__[key] = config[key]

        if self.enable:

            if EmailConfig.USERNAME_ENVAR not in os.environ or EmailConfig.PASSWORD_ENVAR not in os.environ:
                raise Exception("missing env var " + EmailConfig.USERNAME_ENVAR + "," + EmailConfig.PASSWORD_ENVAR)

            toEmail = self.__dict__[EmailConfig.TO_EMAIL_KEY]
            try:
                emailinfo = validate_email(toEmail, check_deliverability=False)
                self.__dict__[EmailConfig.TO_EMAIL_KEY] = emailinfo.normalized
            except EmailNotValidError as e:
                raise Exception(f"Invalid to email address {toEmail}") from e

            fromEmail = self.__dict__[EmailConfig.FROM_EMAIL_KEY]
            try:
                emailinfo = validate_email(fromEmail, check_deliverability=False)
                self.__dict__[EmailConfig.FROM_EMAIL_KEY] = emailinfo.normalized
            except EmailNotValidError as e:
                raise Exception(f"Invalid from email address {fromEmail}") from e

    @property
    def enable(self) -> bool:
        """
        enable property getter
        :param self: this
        :return: the enable
        """
        return self.__dict__[EmailConfig.ENABLE_KEY]

    @property
    def host(self) -> str:
        """
        host property getter
        :param self: this
        :return: the host
        """
        return self.__dict__[EmailConfig.HOST_KEY]

    @property
    def port(self) -> int:
        """
        port property getter
        :param self: this
        :return: the port
        """
        return self.__dict__[EmailConfig.PORT_KEY]

    @property
    def username(self) -> str:
        """
        username property getter
        :param self: this
        :return: the username
        """
        return self.__dict__[EmailConfig.USERNAME_KEY]

    @property
    def password(self) -> str:
        """
        password property getter
        :param self: this
        :return: the password
        """
        return self.__dict__[EmailConfig.PASSWORD_KEY]

    @property
    def from_email(self) -> str:
        """
        from_email property getter
        :param self: this
        :return: the from email address
        """
        return self.__dict__[EmailConfig.FROM_EMAIL_KEY]

    @property
    def to_email(self) -> str:
        """
        to_email property getter
        :param self: this
        :return: the to email address
        """
        return self.__dict__[EmailConfig.TO_EMAIL_KEY]
