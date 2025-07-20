import os
import smtplib
import tempfile
import time
import traceback
from datetime import datetime
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from conf.AppConfig import AppConfig
from conf.EmailConfig import EmailConfig
from py_singleton import singleton
from util.Logger import logger

__all__ = ["Emailer"]


@logger
@singleton
class Emailer:
    """
    A class to send error notifications via Gmail with stack traces as attachments.
    """

    def __init__(self):
        """
        ctor
        :param self: this
        """
        self._config: EmailConfig = AppConfig().email

    def send_error_notification(self, exception: Exception, subject_prefix: str = "Application Error"):
        """
        Send an email notification with error details and stack trace attachment.

        Args:
            exception (Exception): The exception that occurred
            subject_prefix (str): Prefix for the email subject
            additional_context (str): Additional context information to include
        """
        self.logger.exception(subject_prefix)

        try:

            msg: MIMEMultipart = self.build_message(f"{subject_prefix}: {type(exception).__name__}", exception)

            # Create stack trace attachment
            stack_trace = traceback.format_exc()

            msg.attach(self.build_attachement(stack_trace))

            self.send_message(msg)

        except Exception:
            self.logger.exception("Failed to send error notification")

    def build_attachement(self, stack: str) -> MIMEBase:
        """
        build stack trace attachment

        Args:
            stack (str): the stack trace in string
            
            returns:
            MIMEBase: the mime base part with the stack trace as attachment
        """
        part = MIMEBase("application", "octet-stream")

        # Create a temporary file for the stack trace
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", prefix="stack_trace_", delete=False) as temp_file:
            temp_file.write("Stack Trace\n")
            temp_file.write("=" * 50 + "\n\n")
            temp_file.write("".join(stack))
            temp_filename = temp_file.name

        try:
            # Attach the stack trace file
            with open(temp_filename, "rb") as attachment:
                part.set_payload(attachment.read())

            encoders.encode_base64(part)
            part.add_header(
                "Content-Disposition", f"attachment; filename= stack_trace_{int(round(time.time() * 1000))}.txt"
            )

        finally:
            # Clean up temporary file
            try:
                os.unlink(temp_filename)
            except OSError:
                pass
        
        return part
        
    def build_message(self, subject: str, exception: Exception) -> MIMEMultipart:
        """
        build email mime message with exception stack as attachement

        Args:
            subject (str): message subject
            exception (Exception): the exception to include in the message
        """
        # Get current timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Create email message
        msg = MIMEMultipart()
        msg["From"] = self._config.from_email
        msg["To"] = self._config.to_email
        msg["Subject"] = f"{subject} at {timestamp}"

        # Create email body
        error_message = str(exception)
        body = f"""
An error occurred in your application:

Error Type: {type(exception).__name__}
Error Message: {error_message}
Timestamp: {timestamp}

Please see the attached file for the complete stack trace.

---
This is an automated error notification.
"""

        # Attach the body to the email
        msg.attach(MIMEText(body, "plain"))

        return msg

    def send_message(self, msg: MIMEMultipart):
        """
        Send email message to smtp.

        Args:
            msg (MIMEMultipart): the mime message payload
        """
        # Send the email
        server = smtplib.SMTP_SSL(self._config.smtp_host, self._config.smtp_port)
        server.ehlo()
        server.login(self._config.username, self._config.password)

        text = msg.as_string()
        server.sendmail(self._config.from_email, self._config.to_email, text)
        server.quit()

        self.logger.debug(f"Error notification sent successfully to {self._config.to_email}")
