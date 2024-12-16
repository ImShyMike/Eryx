"""Module for error classes."""

from typing import Any, Dict


class ValidationError(RuntimeError):
    def __init__(self, message, errors):
        super().__init__(message)
            
        # Now for your custom code...
        self.errors = errors