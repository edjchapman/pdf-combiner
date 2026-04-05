"""Custom exceptions for pdf-combiner."""


class PdfCombinerError(Exception):
    """Base exception for pdf-combiner."""


class EncryptedPdfError(PdfCombinerError):
    """Raised when a password-protected PDF is opened without the correct password."""


class InvalidPageRangeError(PdfCombinerError):
    """Raised for malformed or out-of-bounds page range specifications."""
