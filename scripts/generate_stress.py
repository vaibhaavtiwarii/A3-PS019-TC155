"""Generate two larger, seeded, SYNTHETIC stress sets with their answer keys.

    python scripts/generate_stress.py            # writes data/stress/tune and data/stress/sealed

  tune    used while developing the rules (regression check). Names the scanner knows.
  sealed  different seed, UNSEEN names and different column vocabulary. Evaluate it only after the
          rules are frozen. Whatever number it gives is the honest one.

Both sets contain the same kinds of difficulty: renamed or unnamed columns, mixed formats, PII hidden
in free text and JSON, columns that look personal but are not (order numbers, SKUs, hire dates),
sparse and empty columns, a semicolon CSV in Latin-1, SQLite tables with a view and INTEGER phones.

Everything is invented. The answer key comes from the generator, so these sets are labelled
automatically; the HAND-labelled sets (data/ and data/holdout/) remain the headline numbers.
Each set also gets metadata.csv (declared purpose / retention / owner with deliberate gaps) and
gaps.csv (the gap codes a correct linker must report)."""
import csv
import json
import random
import sqlite3
from datetime import date, timedelta
from pathlib import Path

from privexis.lexicon import FIRST_NAMES, LAST_NAMES
from privexis.validators import verhoeff_check_digit

OUT = Path("data/stress")
REF = date(2026, 10, 17)
DIGITS, LETTERS = "0123456789", "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

NAMES_KNOWN = ([n.capitalize() for n in sorted(FIRST_NAMES)[:60]],
               [n.capitalize() for n in sorted(LAST_NAMES)[:40]])
NAMES_UNSEEN = (
    ["Advait", "Bhavna", "Chirag", "Dhruv", "Eshaan", "Falguni", "Gargi", "Harshita", "Indrani", "Jatin",
     "Lavanya", "Madhav", "Navya", "Omkar", "Parth", "Qasim", "Radhika", "Samar", "Ujjwal", "Vedant",
     "Wasim", "Yamini", "Zubin", "Brandon", "Dmitri", "Gustav", "Ibrahim", "Jovan", "Katarina", "Mateo",
     "Oskar", "Saanvi", "Tobias", "Viraj", "Xavier", "Yusuf", "Anvi", "Bodhi", "Charvi", "Devansh"],
    ["Bhattacharya", "Dasgupta", "Fernandes", "Gowda", "Hegde", "Lobo", "Mukherjee", "Nambiar", "Oberoi",
     "Parekh", "Raghavan", "Sethi", "Trivedi", "Upadhyay", "Venkatesh", "Zaveri", "Okafor", "Petrov",
     "Lindqvist", "Novak", "Haddad", "Tanaka", "Moreau", "Kowalski", "Rossi", "Silva", "Varma"])
assert not {n.lower() for n in NAMES_UNSEEN[0]} & FIRST_NAMES, "sealed first names must be unseen"
assert not {n.lower() for n in NAMES_UNSEEN[1]} & LAST_NAMES, "sealed surnames must be unseen"

CITIES = ["Pune", "Bareilly", "Jaipur", "Kochi", "Lucknow", "Nagpur", "Surat", "Indore", "Patna", "Mysuru"]
COMPANIES = ["Northwind Traders", "Acme Supplies", "Globex Industries", "Initech Systems", "Hooli Networks",
             "Stark Fabrication", "Wayne Distribution", "Tyrell Components", "Orbit Logistics Pvt Ltd"]
PRODUCTS = ["Blue Widget", "Red Gadget", "Steel Bracket", "Copper Wire", "Oak Panel", "Glass Jar", "Solar Lamp"]
PETS = ["Bruno", "Tommy", "Max", "Rocky", "Simba", "Luna", "Bella", "Coco"]
PURPOSES = ["Customer communication", "KYC identity verification", "Two-factor authentication",
            "Order fulfilment", "Payroll processing", "Fraud monitoring", "Support ticketing"]
RETENTIONS = ["Closure + 180 days", "Statutory (7 years)", "24 months", "Until consent withdrawn", "90 days"]
OWNERS = ["Compliance", "Support team", "Security team", "Platform team", "HR"]

# Column-name vocabularies. 'sealed' deliberately uses words that are NOT in config/rules.yaml.
VOCAB = {
    "tune": {
        "NAME": ["customer_name", "full_name", "first_name", "last_name", "applicant_name", "holder", "recipient_name"],
        "EMAIL": ["email", "contact_email", "work_email", "tmp_mail", "email_addr", "mail_id"],
        "PHONE": ["mobile", "phone", "contact_no", "cell_no", "tmp_ph", "usr_contact", "alt_phone"],
        "GOVT_ID": ["aadhaar_no", "pan_number", "national_id", "tax_id", "uid", "tmp_id"],
        "DOB": ["dob", "birth_date", "date_of_birth", "birth_dt", "born_on"],
    },
    "sealed": {
        "NAME": ["passenger_name", "student_name", "patient", "payee", "client", "guest", "tenant",
                 "first_name", "surname", "insured_name", "borrower"],
        "EMAIL": ["email_primary", "mail_address", "notify_to", "login", "e-mail", "correspondence", "emailid"],
        "PHONE": ["mobile_primary", "tel_no", "whatsapp_number", "emergency_contact", "cellphone",
                  "phone_number", "reach_me", "col_phone"],
        "GOVT_ID": ["aadhaar_uid", "pancard", "identity_proof", "id_number", "kyc_document_no", "uidai_no", "taxpayer_ref"],
        "DOB": ["birthdate", "dt_of_birth", "bday", "date_born", "birthday", "dob_text"],
    },
}
NEGATIVES = [
    ("order_number", lambda r, c: str(r.randint(6, 9)) + "".join(r.choices(DIGITS, k=9))),
    ("tracking_id", lambda r, c: str(r.randint(6, 9)) + "".join(r.choices(DIGITS, k=9))),
    ("account_no", lambda r, c: str(r.randint(1, 9)) + "".join(r.choices(DIGITS, k=11))),
    ("invoice_no", lambda r, c: f"INV-2026-{r.randint(1, 99999):05d}"),
    ("company_name", lambda r, c: r.choice(COMPANIES)),
    ("product_title", lambda r, c: r.choice(PRODUCTS)),
    ("pet_name", lambda r, c: r.choice(PETS)),
    ("city", lambda r, c: r.choice(CITIES)),
    ("hire_date", lambda r, c: (REF - timedelta(days=r.randint(300, 365 * 20))).isoformat()),
    ("created_on", lambda r, c: (REF - timedelta(days=r.randint(1, 700))).isoformat()),
    ("last_login", lambda r, c: (REF - timedelta(days=r.randint(1, 90))).isoformat()),
    ("serial_number", lambda r, c: "".join(r.choices(LETTERS, k=3)) + r.choice("DEGKMNQRSUVWXYZ") + "".join(r.choices(LETTERS, k=1)) + "".join(r.choices(DIGITS, k=4)) + r.choice(LETTERS)),
    ("pincode", lambda r, c: str(r.randint(1, 9)) + "".join(r.choices(DIGITS, k=5))),
    ("amount", lambda r, c: f"{r.uniform(5, 9999):.2f}"),
    ("status", lambda r, c: r.choice(["active", "dormant", "closed"])),
    ("department", lambda r, c: r.choice(["Ops", "HR", "IT", "Finance"])),
    ("gst_no", lambda r, c: f"{r.randint(10, 37)}" + "".join(r.choices(LETTERS, k=5)) + "".join(r.choices(DIGITS, k=4)) + r.choice(LETTERS) + "1Z" + r.choice(LETTERS)),
    ("notes", lambda r, c: r.choice(["Delivery on time.", "Asked for a callback.", "Item restocked.", "Refund processed."])),
]
# Hard negatives that CAN fool a value-only rule. Reported honestly, not hidden.
TRICKY = [
    ("item_code", lambda r, c: "".join(r.choices(LETTERS, k=3)) + r.choice("DEGKMNQRSUVWXYZ") + r.choice(LETTERS) + "".join(r.choices(DIGITS, k=4)) + r.choice(LETTERS)),
    ("legacy_ref", lambda r, c: str(r.randint(6, 9)) + "".join(r.choices(DIGITS, k=9))),
]


# ------------------------------------------------------------------ value generators
def person(r, pool):
    return r.choice(pool[0]), r.choice(pool[1])


def gen_for(cls, r, pool, varied=True):
    """Return a function that makes one value of class `cls`."""
    def name(style="full"):
        f, l = person(r, pool)
        return {"full": f"{f} {l}", "first": f, "last": l,
                "mixed": r.choice([f"{f} {l}", f"{f} {l}".upper(), f"{f} {r.choice('ABKMRS')}. {l}"])}[style]

    def email():
        f, l = person(r, pool)
        local = r.choice([f"{f}.{l}", f"{f}{l}", f"{f[0]}{l}", f"{f}_{l}"]).lower()
        if varied and r.random() < 0.25:
            local += r.choice(["+promo", str(r.randint(1, 99)), "+bank"])
        return f"{local}@{r.choice(['example.com', 'mail.example.org', 'corp.example.in', 'demo-mail.net'])}"

    def phone():
        m = r.choice("6789") + "".join(r.choices(DIGITS, k=9))
        if not varied:
            return m
        return r.choice([m, m, f"+91 {m[:5]} {m[5:]}", f"{m[:5]}-{m[5:]}", f"+91{m}", f"0{m}", f"(+91){m}"])

    def aadhaar():
        body = r.choice("23456789") + "".join(r.choices(DIGITS, k=10))
        n = body + verhoeff_check_digit(body)
        return r.choice([n, f"{n[:4]} {n[4:8]} {n[8:]}", f"{n[:4]}-{n[4:8]}-{n[8:]}"]) if varied else n

    def pan():  # real PANs: the 4th letter is a holder type
        return ("".join(r.choices(LETTERS, k=3)) + r.choice("PPPPCHFATBLJG") + r.choice(LETTERS)
                + "".join(r.choices(DIGITS, k=4)) + r.choice(LETTERS))

    def dob():
        d = REF - timedelta(days=r.randint(19 * 365, 78 * 365))
        if not varied:
            return d.isoformat()
        return r.choice([d.isoformat(), d.strftime("%d/%m/%Y"), d.strftime("%d-%m-%Y"), d.strftime("%-d %b %Y")])

    return {"NAME": name, "EMAIL": email, "PHONE": phone, "DOB": dob,
            "GOVT_ID": lambda: aadhaar() if r.random() < 0.6 else pan(), "_pan": pan,
            "_first": lambda: name("first"), "_last": lambda: name("last"), "_mixed_name": lambda: name("mixed")}[cls]


class Col:
    def __init__(self, name, fn, truth="NONE", null=0.0, as_int=False):
        self.name, self.fn, self.truth, self.null, self.as_int = name, fn, truth, null, as_int


def build(profile: str, seed: int, pool):
    r = random.Random(seed)
    vocab = VOCAB[profile]
    gens = {c: gen_for(c, r, pool) for c in vocab}
    tables = []

    # ---- randomised general tables: a random subset of classes + decoys per table
    for k in range(14):
        cols, used = [], set()
        for cls in vocab:
            if r.random() < 0.85:
                nm = r.choice(vocab[cls])
                while nm in used:
                    nm = r.choice(vocab[cls]) + str(r.randint(2, 9))
                used.add(nm)
                fn = gens[cls]
                if cls == "NAME" and nm in ("first_name",):
                    fn = gen_for("_first", r, pool)
                if cls == "NAME" and nm in ("surname",):
                    fn = gen_for("_last", r, pool)
                cols.append(Col(nm, fn, cls, null=0.1 if r.random() < 0.25 else 0.0))
        for nm, fn in r.sample(NEGATIVES, 5):
            cols.append(Col(nm, lambda f=fn: f(r, None)))
        if r.random() < 0.6:
            nm, fn = r.choice(TRICKY)
            cols.append(Col(nm, lambda f=fn: f(r, None)))
        r.shuffle(cols)
        kind = "sqlite" if k % 5 == 4 else ("semi" if k % 7 == 6 else "csv")
        tables.append((f"{profile}_{k + 1:02d}", cols, 260, kind))

    # ---- fixed hard tables
    em, ph, aad = gens["EMAIL"], gens["PHONE"], gens["GOVT_ID"]
    clean = lambda: r.choice(["Delivery was on time.", "Please update the shipping window.", "Warranty extension asked.",
                              "Refund processed to the original mode.", "Follow-up after the weekend."])
    tables.append((f"{profile}_text", [
        Col("id", lambda: f"C{r.randint(0, 99999):05d}"),
        Col("feedback", lambda: clean() + (f" Reach me at {em()} for details." if r.random() < 0.45 else ""), "EMAIL"),
        Col("call_log", lambda: clean() + (f" Call {ph()} after 5pm." if r.random() < 0.45 else ""), "PHONE"),
        Col("comments", clean)], 200, "csv"))
    tables.append((f"{profile}_json", [
        Col("id", lambda: f"C{r.randint(0, 99999):05d}"),
        Col("profile", lambda: json.dumps({"email": em(), "phone": gens["PHONE"](), "tier": r.choice(["gold", "silver"]),
                                           "address": {"city": r.choice(CITIES), "pin": str(r.randint(100000, 999999))}}))],
                  200, "csv"))
    tables.append((f"{profile}_mixed", [
        Col("contact", lambda: em() if r.random() < 0.5 else gens["PHONE"](), "EMAIL|PHONE"),
        Col("remark", clean)], 200, "csv"))
    tables.append((f"{profile}_sparse", [
        Col("alt_email", em, "EMAIL", null=0.92), Col("fax_no", gens["PHONE"], "PHONE", null=1.0),
        Col("old_mobile", gens["PHONE"], "PHONE", null=0.85), Col("remark", clean, null=0.5)], 200, "csv"))
    tables.append((f"{profile}_unnamed", [
        Col("col_1", gen_for("_mixed_name", r, pool), "NAME"), Col("col_2", em, "EMAIL"),
        Col("col_3", gens["DOB"], "DOB"), Col("col_4", lambda: aad(), "GOVT_ID"),
        Col("col_5", lambda: f"{r.uniform(5, 9999):.2f}")], 200, "csv"))
    return tables


# --------------------------------------------------------------------------- writers
def _write_table(root: Path, name, cols, n, kind, r):
    rows = [[("" if (c.null and r.random() < c.null) else str(c.fn())) for c in cols] for _ in range(n)]
    header = [c.name for c in cols]
    if kind in ("csv", "semi"):
        f = root / f"{name}.csv"
        enc, delim = ("latin-1", ";") if kind == "semi" else ("utf-8", ",")
        if kind == "semi":                               # make the Latin-1 file really contain accents
            for row in rows[::9]:
                row[0] = row[0].replace("a", "á", 1)
        with open(f, "w", newline="", encoding=enc) as fh:
            w = csv.writer(fh, delimiter=delim)
            w.writerow(header)
            w.writerows(rows)
        return f.name, "-"
    db = root / f"{name}.sqlite"
    con = sqlite3.connect(db)
    con.execute(f'CREATE TABLE records ({", ".join(chr(34) + h + chr(34) for h in header)})')
    typed = [[(int(v) if c.as_int and v.isdigit() else (v or None)) for c, v in zip(cols, row)] for row in rows]
    con.executemany(f"INSERT INTO records VALUES ({','.join('?' * len(cols))})", typed)
    con.execute("CREATE VIEW records_view AS SELECT * FROM records")
    con.commit()
    con.close()
    return db.name, "records"


def generate(profile: str, seed: int, pool, out: Path):
    r = random.Random(seed + 1)
    root = out / profile
    root.mkdir(parents=True, exist_ok=True)
    for old in root.iterdir():
        old.unlink()
    labels, meta, gaps = [], [], []
    tables = build(profile, seed, pool)
    default_table = tables[2][0]                         # one table gets a table-level declared default
    for name, cols, n, kind in tables:
        src, tab = _write_table(root, name, cols, n, kind, r)
        views = [(src, "records_view")] if kind == "sqlite" else []
        for c in cols:
            if c.name == "profile":
                keys = [("profile.email", "EMAIL"), ("profile.phone", "PHONE"), ("profile.tier", "NONE"),
                        ("profile.address.city", "NONE"), ("profile.address.pin", "NONE")]
                labels += [(src, tab, k, t) for k, t in keys]
                continue
            for s, t in [(src, tab)] + views:
                labels.append((s, t, c.name, c.truth))
        # metadata for personal columns of the base table only (views are not documented)
        if (name == default_table) and kind != "sqlite":
            meta.append([src, "", "*", r.choice(PURPOSES), r.choice(RETENTIONS), r.choice(OWNERS)])
        for c in cols:
            if c.truth == "NONE" or c.name == "profile":
                continue
            if name == default_table:
                gaps.append((src, tab, c.name, set()))      # covered by the table default
                continue
            roll = r.random()
            vals = {"purpose": r.choice(PURPOSES), "retention": r.choice(RETENTIONS), "owner": r.choice(OWNERS)}
            if roll < 0.55:
                missing = set()
            elif roll < 0.70:
                missing = {"purpose"}
            elif roll < 0.82:
                missing = {"retention"}
            elif roll < 0.90:
                missing = {"owner"}
            elif roll < 0.95:
                missing = {"purpose", "retention"}
            else:
                missing = None                               # no entry at all
            if missing is None:
                gaps.append((src, tab, c.name, {"NO_METADATA_ENTRY", "MISSING_PURPOSE", "MISSING_RETENTION", "MISSING_OWNER"}))
                continue
            for m in missing:
                vals[m] = r.choice(["", "TBD"]) if m != "owner" else ""
            meta.append([src, tab if tab != "-" else "", c.name.upper() if r.random() < 0.05 else c.name,
                         vals["purpose"], vals["retention"], vals["owner"]])
            gaps.append((src, tab, c.name, {f"MISSING_{m.upper()}" for m in missing}))
    first = tables[0]
    meta += [[f"{first[0]}.csv", "", f"legacy_field_{i}", "Historic campaign", "12 months", "Marketing"] for i in (1, 2)]

    def w(path, header, rows):
        with open(path, "w", newline="", encoding="utf-8") as fh:
            cw = csv.writer(fh)
            cw.writerow(header)
            cw.writerows(rows)
    w(root / "labels.csv", ["source", "table", "column", "true_class"], labels)
    w(root / "metadata.csv", ["source", "table", "column", "purpose", "retention", "owner"], meta)
    w(root / "gaps.csv", ["source", "table", "column", "expected_gaps"],
      [(s, t, c, "|".join(sorted(g))) for s, t, c, g in gaps])
    personal = sum(1 for l in labels if l[3] != "NONE")
    print(f"{profile:7s} files={len(list(root.glob('*.csv'))) + len(list(root.glob('*.sqlite'))) - 3:3d} "
          f"columns={len(labels):3d} personal={personal:3d}")


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    generate("tune", 101, NAMES_KNOWN, OUT)
    generate("sealed", 909, NAMES_UNSEEN, OUT)
    print(f"Written to {OUT}/  (labels.csv, metadata.csv, gaps.csv in each set)")


if __name__ == "__main__":
    main()
