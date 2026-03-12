"""
wikidata_api.py
===============
Query Wikidata's free SPARQL endpoint to verify factual claims.
No API key required.

Provides:
  - verify_claim_wikidata(subject, relation, obj) → (bool, float, str)
  - search_entity(name) → QID or None
  - get_entity_facts(name) → list of (relation, object, confidence)
"""

import re
import json
import urllib.request
import urllib.parse
import urllib.error
from functools import lru_cache
from typing import Optional, Tuple, List


# ── Wikidata endpoints ────────────────────────────────────────────────────────

SPARQL_URL  = "https://query.wikidata.org/sparql"
SEARCH_URL  = "https://www.wikidata.org/w/api.php"
TIMEOUT     = 8  # seconds


# ── Relation → Wikidata property mapping ──────────────────────────────────────

RELATION_TO_PROPERTIES = {
    "capital_of":    ["P36"],                              # capital
    "founded_by":    ["P112", "P170", "P50"],               # founded by, creator, author
    "located_in":    ["P131", "P17", "P276", "P30", "P19"],  # admin territory, country, location, continent, birthplace
    "discovered":    ["P61"],                                # discoverer or inventor
    "is":            ["P31", "P279", "P361"],                # instance of, subclass of, part of
    "population_of": ["P1082"],                              # population
    "color":         ["P462"],                               # color
}

# Disambiguation suffixes to try when the first search result is wrong
_DISAMBIG_HINTS = {
    "founded_by": ["company", "organization", "brand"],
    "located_in": ["place", "landmark", "building", "city"],
    "discovered": ["scientist", "physicist", "chemist", "biologist"],
    "capital_of": ["city"],
    "is":         [],
}


# ── Low-level helpers ─────────────────────────────────────────────────────────

def _sparql_query(query: str) -> list:
    """Execute a SPARQL query against Wikidata and return the result bindings."""
    params = urllib.parse.urlencode({"query": query, "format": "json"})
    url = f"{SPARQL_URL}?{params}"
    req = urllib.request.Request(url, headers={
        "User-Agent": "VALKYRIE-Decoder/2.0 (fact-verification research project)",
        "Accept": "application/sparql-results+json",
    })
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return data.get("results", {}).get("bindings", [])
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, OSError):
        return []


def _search_api(params: dict) -> dict:
    """Call the MediaWiki API on Wikidata."""
    full_params = urllib.parse.urlencode(params)
    url = f"{SEARCH_URL}?{full_params}"
    req = urllib.request.Request(url, headers={
        "User-Agent": "VALKYRIE-Decoder/2.0",
    })
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, OSError):
        return {}


# ── Entity search ─────────────────────────────────────────────────────────────

@lru_cache(maxsize=1024)
def _raw_search(name: str, limit: int = 5) -> list:
    """Return raw search results from wbsearchentities."""
    data = _search_api({
        "action":   "wbsearchentities",
        "search":   name,
        "language": "en",
        "limit":    str(limit),
        "format":   "json",
    })
    return data.get("search", [])


def search_entity(name: str, hint: str = "") -> Optional[str]:
    """
    Search Wikidata for an entity by name.
    Returns the QID (e.g. 'Q90' for Paris) or None.

    If hint is provided (e.g. 'company'), tries to find the most
    contextually relevant result.
    """
    results = _raw_search(name)
    if not results:
        return None

    name_lower = name.lower().strip()
    hint_lower = hint.lower().strip()

    # If we have a hint, prefer results whose description contains the hint
    if hint_lower:
        for r in results:
            desc = r.get("description", "").lower()
            label = r.get("label", "").lower().strip()
            if label == name_lower and hint_lower in desc:
                return r["id"]
        for r in results:
            desc = r.get("description", "").lower()
            if hint_lower in desc:
                return r["id"]

    # Prefer exact label match
    for r in results:
        if r.get("label", "").lower().strip() == name_lower:
            return r["id"]

    return results[0]["id"]


def _search_entity_for_relation(name: str, relation: str) -> Optional[str]:
    """
    Smart entity search that uses the relation context to disambiguate.
    E.g. 'Apple' + 'founded_by' → tries 'Apple company' → Q312 (Apple Inc.)
    """
    # First try plain search
    qid = search_entity(name)

    # Try with disambiguation hints
    hints = _DISAMBIG_HINTS.get(relation, [])
    for hint in hints:
        hint_qid = search_entity(name, hint=hint)
        if hint_qid and hint_qid != qid:
            # Verify this QID actually has the relevant properties
            props = RELATION_TO_PROPERTIES.get(relation, [])
            for prop in props[:1]:  # Check just the primary property
                check = _sparql_query(f"""
                SELECT ?val WHERE {{
                  wd:{hint_qid} wdt:{prop} ?val .
                }} LIMIT 1
                """)
                if check:
                    return hint_qid

    # Check if the plain QID has the relevant properties
    if qid:
        props = RELATION_TO_PROPERTIES.get(relation, [])
        for prop in props[:1]:
            check = _sparql_query(f"""
            SELECT ?val WHERE {{
              wd:{qid} wdt:{prop} ?val .
            }} LIMIT 1
            """)
            if check:
                return qid

        # If plain QID doesn't have the property, try alternate search terms
        for hint in hints:
            alt_qid = search_entity(name, hint=hint)
            if alt_qid:
                return alt_qid

    return qid


# ── Core label-based verification ─────────────────────────────────────────────

def _verify_by_labels(qid: str, properties: list, target_obj: str) -> Tuple[bool, str]:
    """
    For a given entity QID, check if any of the given properties
    have a value whose label fuzzy-matches target_obj.
    """
    for prop in properties:
        query = f"""
        SELECT ?valLabel WHERE {{
          wd:{qid} wdt:{prop} ?val .
          SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en". }}
        }} LIMIT 10
        """
        results = _sparql_query(query)
        for r in results:
            val_label = r.get("valLabel", {}).get("value", "")
            if _fuzzy_match(val_label, target_obj):
                return True, f"Wikidata: {prop} → {val_label}"
    return False, ""


# ── Claim verification via SPARQL ─────────────────────────────────────────────

@lru_cache(maxsize=512)
def verify_claim_wikidata(
    subject: str, relation: str, obj: str
) -> Tuple[bool, float, str]:
    """
    Verify a (subject, relation, object) triple against Wikidata.

    Returns
    -------
    (verified, confidence, description)
      - verified:    True if the fact was confirmed
      - confidence:  0.85 for API-verified facts
      - description: human-readable explanation or empty string
    """
    # Get QID for subject with smart disambiguation
    subj_qid = _search_entity_for_relation(subject, relation)
    if not subj_qid:
        return False, 0.0, ""

    # Get the property IDs to check
    properties = RELATION_TO_PROPERTIES.get(relation, [])

    # ── Try QID-based verification (exact entity match) ──────────────
    obj_qid = search_entity(obj)
    if obj_qid:
        for prop in properties:
            query = f"""
            SELECT ?item WHERE {{
              wd:{subj_qid} wdt:{prop} ?item .
              FILTER(?item = wd:{obj_qid})
            }} LIMIT 1
            """
            results = _sparql_query(query)
            if results:
                return True, 0.85, f"Wikidata: {subject} → {prop} → {obj}"

    # ── Try label-based matching (works when obj is descriptive text) ─
    verified, desc = _verify_by_labels(subj_qid, properties, obj)
    if verified:
        return True, 0.85, f"Wikidata: {subject} — {desc}"

    # ── Relation-specific fallbacks ──────────────────────────────────

    # capital_of: reverse lookup — check if the country's capital = subject
    if relation == "capital_of":
        obj_qid_country = _search_entity_for_relation(obj, "is")
        if obj_qid_country:
            verified, desc = _verify_by_labels(obj_qid_country, ["P36"], subject)
            if verified:
                return True, 0.85, f"Wikidata: {obj} capital → {desc}"

    # founded_by: try all founder-related properties
    if relation == "founded_by":
        for prop in ["P112", "P50", "P170", "P61"]:
            verified, desc = _verify_by_labels(subj_qid, [prop], obj)
            if verified:
                return True, 0.85, f"Wikidata: {subject} — {desc}"

    # discovered: also check P61, and try "notable work" reverse lookup
    if relation == "discovered":
        # Try: the object was discovered/invented by the subject
        obj_qid_disc = search_entity(obj)
        if obj_qid_disc:
            for prop in ["P61", "P170"]:
                verified, desc = _verify_by_labels(obj_qid_disc, [prop], subject)
                if verified:
                    return True, 0.85, f"Wikidata: {obj} — {desc}"

        # Try: subject's notable works include the object
        verified, desc = _verify_by_labels(subj_qid, ["P800"], obj)  # P800 = notable work
        if verified:
            return True, 0.85, f"Wikidata: {subject} — {desc}"

    # located_in: try multiple location properties including birthplace
    if relation == "located_in":
        for prop in ["P17", "P131", "P30", "P276", "P19", "P706"]:
            verified, desc = _verify_by_labels(subj_qid, [prop], obj)
            if verified:
                return True, 0.85, f"Wikidata: {subject} — {desc}"

    # For founded_by, also try reverse: object's notable works include subject
    if relation == "founded_by":
        obj_qid_person = _search_entity_for_relation(obj, "is")
        if obj_qid_person:
            verified, desc = _verify_by_labels(obj_qid_person, ["P800"], subject)
            if verified:
                return True, 0.85, f"Wikidata: {obj} — {desc}"

    return False, 0.0, ""


# ── Get facts about an entity ─────────────────────────────────────────────────

def get_entity_facts(name: str) -> List[Tuple[str, str, float, str]]:
    """
    Retrieve key facts about an entity from Wikidata.
    Returns list of (relation, object_label, confidence, description).
    """
    qid = search_entity(name)
    if not qid:
        return []

    facts = []
    for prop, rel_name in [("P31", "is"), ("P279", "is"), ("P17", "located_in"),
                           ("P131", "located_in"), ("P36", "capital_of"),
                           ("P112", "founded_by"), ("P50", "founded_by"),
                           ("P61", "discovered"), ("P800", "notable_work")]:
        query = f"""
        SELECT ?valLabel WHERE {{
          wd:{qid} wdt:{prop} ?val .
          SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en". }}
        }} LIMIT 5
        """
        results = _sparql_query(query)
        for r in results:
            label = r.get("valLabel", {}).get("value", "")
            if label and not label.startswith("Q"):
                facts.append((rel_name, label, 0.85, f"Wikidata {prop}"))

    return facts


# ── Fuzzy matching helper ─────────────────────────────────────────────────────

def _fuzzy_match(a: str, b: str) -> bool:
    """Case-insensitive comparison with normalization."""
    a = re.sub(r"[^a-z0-9\s]", "", a.lower().strip())
    b = re.sub(r"[^a-z0-9\s]", "", b.lower().strip())
    if not a or not b:
        return False
    return a == b or a in b or b in a


# ── Quick self-test ───────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("Testing Wikidata API integration...")
    print()

    tests = [
        ("Paris",        "capital_of",  "France"),
        ("Apple",        "founded_by",  "Steve Jobs"),
        ("Eiffel Tower", "located_in",  "Paris"),
        ("Einstein",     "discovered",  "Relativity"),
        ("Mars",         "is",          "Planet"),
        ("Tokyo",        "capital_of",  "Japan"),
        ("Tesla",        "founded_by",  "Elon Musk"),
    ]

    passed = 0
    for subj, rel, obj in tests:
        verified, conf, desc = verify_claim_wikidata(subj, rel, obj)
        status = "✓ VERIFIED" if verified else "✗ NOT FOUND"
        if verified:
            passed += 1
        print(f"  {status}  ({subj}) --[{rel}]--> ({obj})  conf={conf:.2f}")
        if desc:
            print(f"           {desc}")

    print(f"\n  {passed}/{len(tests)} tests passed.")
    print("Done.")
