"""
Compatibility patch for instagrapi with Python 3.14+
"""
import sys

# Patch pydantic for Python 3.14 compatibility
if sys.version_info >= (3, 14):
    import pydantic
    from pydantic import class_validators
    
    # Monkey patch to ignore the validator field check
    original_check = class_validators.ValidatorGroup.check_for_unused
    
    def patched_check(self):
        try:
            original_check(self)
        except pydantic.errors.ConfigError as e:
            # Ignore validator field errors in Python 3.14
            if "Validators defined with incorrect fields" in str(e):
                pass
            else:
                raise
    
    class_validators.ValidatorGroup.check_for_unused = patched_check
