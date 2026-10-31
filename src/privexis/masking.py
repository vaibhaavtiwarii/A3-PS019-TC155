"""Mask sample values before they are shown anywhere. Raw personal values never leave the scanner."""
import re


def _stars(n: int) -> str:
    return "*" * max(n, 1)


def mask_value(value: str, cls: str = "") -> str:
    """Class-aware masking that keeps just enough shape for a reviewer to recognise the format."""
    v = str(value).strip()
    if not v:
        return ""
    cls = (cls or "").upper()
    if cls == "EMAIL" or (not cls and "@" in v):
        local, _, domain = v.partition("@")
        return f"{local[:1]}{_stars(len(local) - 1)}@{domain}" if domain else v[:1] + _stars(len(v) - 1)
    if cls == "PHONE":
        digits = re.sub(r"\D", "", v)
        return _stars(len(digits) - 3) + digits[-3:]
    if cls == "GOVT_ID":
        compact = re.sub(r"[ -]", "", v)
        if compact.isdigit():
            return "XXXX XXXX " + compact[-4:]
        return compact[:2].upper() + _stars(len(compact) - 3) + compact[-1:].upper()
    if cls == "DOB":
        m = re.search(r"(?:19|20)\d{2}", v)
        return f"{m.group(0)}-**-**" if m else "****-**-**"
    if cls == "NAME":
        return " ".join(t[:1] + _stars(len(t) - 1) for t in v.split())
    return v[:1] + _stars(len(v) - 2) + v[-1:] if len(v) > 2 else _stars(len(v))
