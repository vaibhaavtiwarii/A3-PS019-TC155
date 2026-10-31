"""Strict validators: the 'is this really an X?' layer of the detection pipeline.

Every function takes one string and returns True/False (or a subtype string).
They are pure: no file access, no global state, so they are easy to test.
"""
import re
import unicodedata
from datetime import date, datetime

from privexis.lexicon import FIRST_NAMES, LAST_NAMES, ORG_WORDS

# --- Verhoeff checksum (used by Aadhaar) -----------------------------------
# D = multiplication table of the dihedral group D5, P = position permutation,
# INV = inverse of each element of D.
_D = [
    [0,1,2,3,4,5,6,7,8,9], [1,2,3,4,0,6,7,8,9,5], [2,3,4,0,1,7,8,9,5,6],
    [3,4,0,1,2,8,9,5,6,7], [4,0,1,2,3,9,5,6,7,8], [5,9,8,7,6,0,4,3,2,1],
    [6,5,9,8,7,1,0,4,3,2], [7,6,5,9,8,2,1,0,4,3], [8,7,6,5,9,3,2,1,0,4],
    [9,8,7,6,5,4,3,2,1,0],
]
_P = [
    [0,1,2,3,4,5,6,7,8,9], [1,5,7,6,2,8,3,0,9,4], [5,8,0,3,7,9,6,1,4,2],
    [8,9,1,6,0,4,3,5,2,7], [9,4,5,3,1,2,6,8,7,0], [4,2,8,6,5,7,3,9,0,1],
    [2,7,9,3,8,0,6,4,1,5], [7,0,4,6,9,1,3,2,5,8],
]
_INV = [0, 4, 3, 2, 1, 5, 6, 7, 8, 9]


def verhoeff_validate(number: str) -> bool:
    """True if the full number (including its check digit) is valid."""
    if not number or not number.isascii() or not number.isdigit():
        return False
    c = 0
    for i, ch in enumerate(reversed(number)):
        c = _D[c][_P[i % 8][int(ch)]]
    return c == 0


def verhoeff_check_digit(body: str) -> str:
    """Compute the check digit to append to `body`."""
    c = 0
    for i, ch in enumerate(reversed(body)):
        c = _D[c][_P[(i + 1) % 8][int(ch)]]
    return str(_INV[c])


# --- Aadhaar-style number ---------------------------------------------------
_AADHAAR_SHAPE = re.compile(r"^\d{4}([ -]?)\d{4}\1\d{4}$")


def is_aadhaar_like(value: str) -> bool:
    v = value.strip()
    if not _AADHAAR_SHAPE.match(v):
        return False
    digits = re.sub(r"[ -]", "", v)
    return digits[0] in "23456789" and verhoeff_validate(digits)


# --- PAN ---------------------------------------------------------------------
_PAN_RE = re.compile(r"^[A-Z]{5}[0-9]{4}[A-Z]$")
PAN_HOLDER_TYPES = frozenset("PCHFATBLJG")    # 4th letter = type of holder


def is_pan(value: str, strict: bool = False) -> bool:
    """AAAAA9999A. With strict=True the 4th letter must be a real holder type."""
    v = value.strip().upper()
    return bool(_PAN_RE.match(v)) and (not strict or v[3] in PAN_HOLDER_TYPES)


def is_govt_id(value: str, strict_pan: bool = False) -> bool:
    return is_aadhaar_like(value) or is_pan(value, strict_pan)


def govt_id_kind(value: str, strict_pan: bool = False):
    """'aadhaar', 'pan' or None: which kind of ID the value is."""
    if is_aadhaar_like(value):
        return "aadhaar"
    return "pan" if is_pan(value, strict_pan) else None


# --- Email (practical subset of RFC 5322 addr-spec) --------------------------
_LOCAL_ATOM = re.compile(r"^[A-Za-z0-9!#$%&'*+/=?^_`{|}~-]+$")
_DOMAIN_LABEL = re.compile(r"^[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?$")


def is_email(value: str) -> bool:
    v = value.strip()
    if v.count("@") != 1 or len(v) > 254:
        return False
    local, domain = v.split("@")
    if not local or len(local) > 64:
        return False
    if any(not a or not _LOCAL_ATOM.match(a) for a in local.split(".")):
        return False                 # empty atom = leading/trailing/double dot
    labels = domain.split(".")
    if len(labels) < 2 or any(not _DOMAIN_LABEL.match(x) for x in labels):
        return False
    return labels[-1].isalpha() and len(labels[-1]) >= 2


# --- Phone numbers ------------------------------------------------------------
_PHONE_CHARS = re.compile(r"^[\d\s().+-]+$")


def is_phone(value: str) -> bool:
    """Indian mobile (10 digits starting 6-9, optional +91 / 91 / 0) or international E.164."""
    v = value.strip()
    if not _PHONE_CHARS.match(v) or v.count("+") > 1:
        return False
    plus = v.count("+") == 1
    if plus and not re.match(r"^\(?\s*\+", v):
        return False                       # '+' only allowed at the very start
    d = re.sub(r"\D", "", v)
    if len(set(d)) < 3:                    # 0000000000, 9999999999, 9898989898 ...
        return False
    if plus:
        if not 8 <= len(d) <= 15 or d[0] == "0":
            return False
        return len(d) == 12 and d[2] in "6789" if d.startswith("91") else True
    if len(d) == 10:
        return d[0] in "6789"
    if len(d) == 11 and d[0] == "0":
        return d[1] in "6789"
    return len(d) == 12 and d.startswith("91") and d[2] in "6789"


# --- Dates of birth -------------------------------------------------------------
_DATE_FORMATS = ("%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y", "%d.%m.%Y", "%Y/%m/%d",
                 "%d %b %Y", "%d %B %Y", "%b %d, %Y", "%B %d, %Y", "%d-%b-%Y")


def parse_date(value: str):
    v = value.strip()
    if not v or len(v) > 30:
        return None
    for fmt in _DATE_FORMATS:
        try:
            return datetime.strptime(v, fmt).date()
        except ValueError:
            continue
    return None


def is_plausible_dob(value: str, today: date = None) -> bool:
    """A real calendar date between 1900-01-01 and today."""
    d = parse_date(value)
    return d is not None and date(1900, 1, 1) <= d <= (today or date.today())


def birth_like_spread(values, today: date = None) -> bool:
    """Do these dates look like BIRTH dates rather than record dates (created, joined ...)?

    Birth dates of a population span decades and mostly fall at adult ages. Record dates
    cluster in the last few years. True when at least 90% of the values are dates, at least
    90% imply an age of 16-100, and the dates cover a span of 10 years or more."""
    today = today or date.today()
    values = list(values)
    dates = [d for d in (parse_date(v) for v in values) if d is not None]
    if not values or len(dates) / len(values) < 0.9:
        return False
    ages = [(today - d).days / 365.25 for d in dates]
    adult = sum(16 <= a <= 100 for a in ages)
    return adult / len(values) >= 0.9 and (max(d.year for d in dates) - min(d.year for d in dates)) >= 10


# --- Person names ------------------------------------------------------------------
_PARTICLES = {"de", "da", "van", "von", "bin", "al", "el", "la", "le", "di", "du", "bint", "ben", "mc"}


def _fold(s: str) -> str:
    """Lower-case and strip accents: 'José' -> 'jose'."""
    s = unicodedata.normalize("NFKD", s)
    return "".join(c for c in s if not unicodedata.combining(c)).lower()


def is_person_name(value: str, strong: bool = False) -> bool:
    """Shape of a personal name: 1-4 alphabetic words, each capitalised.

    A single word is also a name only if the column name is a strong hint (first_name,
    surname ...) or the word is a known given/family name. Words typical of organisations
    ('Pvt', 'Ltd', 'Logistics') rule the value out."""
    toks = value.strip().split()
    if not 1 <= len(toks) <= 4 or len(value) > 60:
        return False
    for t in toks:
        core = t.strip(".")
        if not core or not all(c.isalpha() or c in "'-." for c in core) or not core[0].isalpha():
            return False
        if not (core[0].isupper() or _fold(core) in _PARTICLES):
            return False
        if _fold(core.strip(".'-")) in ORG_WORDS:
            return False
    if len(toks) == 1:
        word = _fold(toks[0].strip(".'-"))
        return strong or word in FIRST_NAMES or word in LAST_NAMES
    return True


def known_name_ratio(values) -> float:
    """Share of values containing at least one well-known given/family name (supporting evidence)."""
    values = list(values)
    if not values:
        return 0.0
    hits = sum(any(_fold(t.strip(".'-")) in FIRST_NAMES | LAST_NAMES for t in v.split()) for v in values)
    return hits / len(values)
