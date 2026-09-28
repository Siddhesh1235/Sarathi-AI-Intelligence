"""Custom exceptions for the Content Moderation pipeline."""


class ModerationException(Exception):
    """Base exception for all moderation errors."""
    def __init__(self, message: str, code: str = "MODERATION_ERROR"):
        super().__init__(message)
        self.message = message
        self.code = code


class PromptInjectionException(ModerationException):
    """Raised when malicious prompt injection or jailbreak attempt is detected."""
    def __init__(self, message: str = "Prompt injection attempt detected"):
        super().__init__(message, code="PROMPT_INJECTION")


class ProfanityDetectedException(ModerationException):
    """Raised when severe profanity or hate speech is detected."""
    def __init__(self, message: str = "Severe profanity detected"):
        super().__init__(message, code="PROFANITY_DETECTED")


class InvalidFileException(ModerationException):
    """Raised when uploaded file violates type, size, or safety constraints."""
    def __init__(self, message: str = "Invalid or unsafe file"):
        super().__init__(message, code="INVALID_FILE")
