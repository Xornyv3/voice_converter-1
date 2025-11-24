#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
translate_sentence.py — robust English→ASL glossing aligned to WLASL.

Key upgrades:
- Contraction handling that preserves WLASL-native forms (e.g., "don't want").
- Numbers: cardinals ("42"→"forty two") and ordinals ("1st"→"first").
- Morphology: plural -s/-es, gerund -ing, past -ed, 3rd person -s.
- Compound smoothing: "a lot (of)"→"a lot", "thank you", "last year", etc.
- Simple ASL reordering: WH to end; destination/topic fronting for GO-like verbs.
- Alias/synonym mapping constrained to existing WLASL gloss keys.
"""

from __future__ import annotations
import json, os, re, sys
from difflib import get_close_matches
try:
    from num2words import num2words  # pip install num2words
except Exception:
    def num2words(n: int) -> str:  # minimal safety net
        return str(n)
from moviepy.editor import VideoFileClip, concatenate_videoclips

# -------------------------
# Lexicon pieces (conservative)
# -------------------------

IRREGULARS = {
    "children":"child","teeth":"tooth","feet":"foot","mice":"mouse",
    "men":"man","women":"woman","people":"person","geese":"goose"
}

# Contractions we may expand. IMPORTANT: ones that exist as WLASL glosses
# (e.g., "don't want") will be preserved automatically later.
CONTRACTIONS = {
    "i'm":"i am","you're":"you are","he's":"he is","she's":"she is","it's":"it is",
    "we're":"we are","they're":"they are","i've":"i have","you've":"you have",
    "we've":"we have","they've":"they have","i'd":"i would","you'd":"you would",
    "he'd":"he would","she'd":"she would","we'd":"we would","they'd":"they would",
    "i'll":"i will","you'll":"you will","he'll":"he will","she'll":"she will",
    "we'll":"we will","they'll":"they will","can't":"cannot","won't":"will not",
    "isn't":"is not","aren't":"are not","wasn't":"was not","weren't":"were not",
    "don't":"do not","doesn't":"does not","didn't":"did not",
    "shouldn't":"should not","wouldn't":"would not","couldn't":"could not",
    "there's":"there is","that's":"that is","what's":"what is","who's":"who is",
}

# Stop words (we remove many, but keep pronouns/possessives that exist in WLASL)
STOPS    = {"a","an","the","is","are","am","of","for"}
WH_WORDS = {"what","where","who","when","why","how"}

# Small alias map → must map to a gloss that exists in WLASL (checked later)
ALIASES = {
    # quantifiers
    "lots":"a lot", "a lot of":"a lot", "plenty of":"plenty", "many":"many",
    "much":"much", "some":"some",
    # politeness / fixed
    "thanks":"thank you", "thankyou":"thank you", "thx":"thank you",
    # time
    "today":"today", "yesterday":"yesterday", "tomorrow":"tomorrow", "last year":"last year",
    "tonight":"tonight", "morning":"morning", "afternoon":"afternoon", "evening":"evening",
    # motion intents
    "go to":"go", "went to":"go", "going to":"go", "travel to":"travel",
    "come to":"come", "arrive to":"arrive", "walk to":"walk", "run to":"run",
    # negation patterns that ASL often simplifies around WANT/LIKE/etc.
    "do not want":"don't want", "dont want":"don't want",
}

# GO-like verbs used for simple destination fronting
VERBS_LOCATIVE = {"go","travel","walk","run","come","arrive","drive","fly","move","visit","return"}

# -------------------------
# Mapping construction
# -------------------------

def build_mapping(class_list_path, nslt_json_path, videos_dir):
    gloss2cid = {}
    with open(class_list_path, encoding="utf-8") as f:
        for line in f:
            parts = line.strip().split()
            if len(parts) < 2: continue
            gloss = " ".join(parts[1:]).lower()
            gloss2cid[gloss] = int(parts[0])

    vid_meta = json.load(open(nslt_json_path, encoding="utf-8"))
    cid2vids = {}
    for vid, meta in vid_meta.items():
        act = meta.get("action")
        if isinstance(act, list) and act:
            cid2vids.setdefault(int(act[0]), []).append(vid)

    mapping = {}
    # 1) WLASL-set clips
    for gloss, cid in gloss2cid.items():
        for vid in cid2vids.get(cid, []):
            path = os.path.join(videos_dir, f"{int(vid):05d}.mp4")
            if os.path.exists(path):
                mapping[gloss] = path
                break
    # 2) Extra custom clips (named files)
    for fname in os.listdir(videos_dir):
        if not fname.endswith(".mp4"): continue
        if re.fullmatch(r"\d{5}\.mp4", fname): continue
        key = os.path.splitext(fname)[0].lower().replace("_"," ")
        mapping.setdefault(key, os.path.join(videos_dir, fname))
    return mapping

# -------------------------
# Normalizers (all mapping-aware)
# -------------------------

ORDINAL_RE = re.compile(r"(\d+)(st|nd|rd|th)\b", flags=re.I)

def expand_contractions_mapping_aware(text: str, mapping_keys: set[str]) -> str:
    """
    Expand generic contractions EXCEPT when a WLASL multi-word gloss containing
    that contraction exists (e.g., keep "don't want").
    """
    # Protect known multi-word keys first by marking them
    protected = {}
    for k in (k for k in mapping_keys if "'" in k and " " in k):
        tag = f"__PROT__{len(protected)}__"
        protected[tag] = k
        text = re.sub(re.escape(k), tag, text, flags=re.I)

    # Expand remaining contractions safely
    def repl(m):
        form = m.group(0).lower()
        return CONTRACTIONS.get(form, form)
    text = re.sub(r"\b(" + "|".join(map(re.escape, CONTRACTIONS.keys())) + r")\b", repl, text, flags=re.I)

    # Restore protected
    for tag, k in protected.items():
        text = text.replace(tag, k)
    return text

def normalize_numbers_tokens(tokens: list[str]) -> list[str]:
    out = []
    for t in tokens:
        if t.isdigit():
            out.extend(num2words(int(t)).split())
        else:
            # ordinals like 1st, 2nd, 3rd, 11th
            m = ORDINAL_RE.fullmatch(t)
            if m:
                n = int(m.group(1))
                out.extend(num2words(n, ordinal=True).split())
            else:
                out.append(t)
    return out

def normalize_token(tok: str, mapping_keys: set[str]) -> str:
    lw = tok.lower()

    # Alias map (only if target exists in mapping)
    if lw in ALIASES and ALIASES[lw] in mapping_keys:
        return ALIASES[lw]

    # irregular plural → singular
    if lw in IRREGULARS and IRREGULARS[lw] in mapping_keys:
        return IRREGULARS[lw]

    # -ing (gerund)
    if lw.endswith("ing"):
        base = lw[:-3]
        if base in mapping_keys:       return base
        if base + "e" in mapping_keys: return base + "e"

    # past -ed (very naive but useful)
    if lw.endswith("ied") and (lw[:-3] + "y") in mapping_keys:
        return lw[:-3] + "y"          # tried → try
    if lw.endswith("ed"):
        base = lw[:-2]
        if base in mapping_keys:               return base
        if base.endswith("e") and base in mapping_keys:  # loved → love (already handled)
            return base
        if (base+"e") in mapping_keys:        return base+"e"  # moved → move
        if lw[:-1] in mapping_keys:           return lw[:-1]   # planned → plan

    # plural -es/-s
    if lw.endswith("es") and lw[:-2] in mapping_keys:
        return lw[:-2]
    if lw.endswith("s") and lw[:-1] in mapping_keys:
        return lw[:-1]

    # 3rd person -s on verbs
    if lw.endswith("es") and (lw[:-2]+"e") in mapping_keys:
        return lw[:-2]+"e"
    if lw.endswith("s") and (lw[:-1]+"e") in mapping_keys:
        return lw[:-1]+"e"

    # fuzzy tolerance to mapping
    close = get_close_matches(lw, mapping_keys, n=1, cutoff=0.87)
    if close:
        return close[0]

    return lw

# -------------------------
# Tokenization & greedy n-gram
# -------------------------

def tokenize_and_match(phrase: str, mapping: dict[str,str]) -> list[str]:
    text = phrase.lower()

    # Alias phrases first (multi-words) when target exists
    for src, dst in sorted(ALIASES.items(), key=lambda x: -len(x[0])):
        if dst in mapping:
            text = re.sub(rf"\b{re.escape(src)}\b", dst, text)

    # strip punctuation (keep apostrophes)
    text = re.sub(r"[^\w\s\-']", " ", text)

    # contractions (mapping-aware)
    text = expand_contractions_mapping_aware(text, set(mapping.keys()))

    words = text.split()
    words = normalize_numbers_tokens(words)

    # Greedy longest-first n-gram over existing mapping keys
    max_ng = max(len(k.split()) for k in mapping.keys()) if mapping else 1
    tokens, i, n = [], 0, len(words)
    while i < n:
        matched = False
        for L in range(min(max_ng, n - i), 0, -1):
            seq = " ".join(words[i:i+L])
            if seq in mapping:
                tokens.append(seq)
                i += L
                matched = True
                break
        if not matched:
            tokens.append(words[i])
            i += 1
    return tokens

# -------------------------
# ASL-friendly reordering
# -------------------------

def _destination_fronting(toks: list[str]) -> list[str]:
    """
    Basic pattern: [subject] (verb in VERBS_LOCATIVE) 'to' <place...>
    → <place...> [subject] (verb)
    Works on flat tokens, conservatively (only when pattern is obvious).
    """
    if len(toks) < 3:
        return toks
    # find 'to' segment
    try:
        idx_to = toks.index("to")
    except ValueError:
        return toks

    # verb must be just before or two before 'to'
    if idx_to == 0: 
        return toks
    # find nearest verb candidate before 'to'
    v_idx = idx_to - 1
    verb = toks[v_idx]
    if verb not in VERBS_LOCATIVE:
        # maybe subject verb 'to' (subject at 0)
        if v_idx >= 1 and toks[v_idx-1] in VERBS_LOCATIVE:
            v_idx -= 1
            verb = toks[v_idx]
        else:
            return toks

    # subject heuristics: token before verb if exists and not WH/stop
    subj = toks[v_idx-1] if v_idx-1 >= 0 else None

    # destination chunk = tokens after 'to'
    dest = toks[idx_to+1:]
    if not dest:
        return toks

    # Build reordered: dest + (subject?) + verb (+ leftovers before subject)
    before = toks[:max(0, v_idx-1)]
    out = []
    out.extend(dest)
    if subj:
        out.append(subj)
    out.append(verb)
    # prepend anything we cut
    out = before + out
    return out

def process_gloss(tokens: list[str], mapping: dict[str,str], manual_reorders: dict[str,list[str]]):
    key_full = " ".join(tokens).strip().lower()
    if key_full in manual_reorders:
        return manual_reorders[key_full]

    mk = set(mapping.keys())

    # per-token normalization
    toks = [normalize_token(t, mk) for t in tokens]

    # drop light stops but keep 'to' for destination rule pass 1
    toks_keep_to = [t for t in toks if t not in (STOPS - {"to"})]

    # destination/topic fronting
    toks_reordered = _destination_fronting(toks_keep_to)

    # now remove any leftover 'to'
    toks_reordered = [t for t in toks_reordered if t not in STOPS]

    # WH at end
    wh   = [t for t in toks_reordered if t in WH_WORDS]
    mids = [t for t in toks_reordered if t not in WH_WORDS]

    # classic 3-token OSV fallback (only if safe: all are single words, no WH)
    if not wh and len(mids) == 3 and all(" " not in t for t in mids):
        subj, verb, obj = mids
        return [obj, subj, verb]

    return mids + wh

# -------------------------
# Video generation
# -------------------------

def make_video(glosses: list[str], mapping: dict[str,str], out_path: str, threshold: float = 0.97):
    clips = []
    found = 0
    total = len(glosses)

    for g in glosses:
        gk = g.lower()
        if gk in mapping:
            clips.append(VideoFileClip(mapping[gk])); found += 1
            continue

        # try normalized variant
        norm = normalize_token(gk, set(mapping.keys()))
        if norm in mapping:
            clips.append(VideoFileClip(mapping[norm])); found += 1
            continue

        # Finger-spell as a last resort
        print(f"Finger-spelling for “{g}”")
        letters = [c for c in gk if c.isalpha()]
        letter_found = True
        for c in letters:
            if c in mapping:
                clips.append(VideoFileClip(mapping[c]))
            else:
                letter_found = False
                print(f"  • Pas de clip pour la lettre «{c}»")
        if letter_found:
            found += 1  # count as covered

    coverage = found / total if total else 0.0
    if coverage < threshold:
        print(f"⚠ Couverture {coverage*100:.1f}% < {threshold*100:.0f}%")

    video = concatenate_videoclips(clips, method="compose")
    # faster write: no audio, quiet logger
    video.write_videofile(out_path, codec="libx264", fps=25, audio=False, logger=None)
    print(f"✅ Vidéo générée : {out_path}  (coverage {coverage*100:.1f}%)")

# -------------------------
# Public API
# -------------------------

def generate_asl_video(
    phrase: str,
    class_list_path: str,
    nslt_json_path: str,
    videos_dir: str,
    out_path: str = "out.mp4",
    manual_reorders: dict | None = None,
    coverage_threshold: float = 0.97
) -> str:
    manual = { (k.lower() if isinstance(k,str) else k): v for k,v in (manual_reorders or {}).items() }

    mapping = build_mapping(class_list_path, nslt_json_path, videos_dir)
    if not mapping:
        raise RuntimeError("No WLASL mapping built — check paths/files.")

    # tokenize using mapping-aware routines
    tokens  = tokenize_and_match(phrase, mapping)
    glosses = process_gloss(tokens, mapping, manual)

    # merge adjacent duplicates (e.g., “go go”) to reduce visual stutter
    dedup = []
    for g in glosses:
        if not dedup or dedup[-1] != g:
            dedup.append(g)

    make_video(dedup, mapping, out_path, threshold=coverage_threshold)
    return out_path

# -------------------------
# CLI
# -------------------------

def main():
    if len(sys.argv) < 5:
        print(__doc__); sys.exit(1)
    cl, js, vdir, phrase, *rest = sys.argv[1:]
    out = rest[0] if rest else "out.mp4"
    mr  = rest[1] if len(rest)>1 else None

    manual = {}
    if mr and os.path.isfile(mr):
        raw = json.load(open(mr, encoding="utf-8"))
        manual = {k.lower(): v for k,v in raw.items()}

    mapping = build_mapping(cl, js, vdir)
    toks    = tokenize_and_match(phrase, mapping)
    glosses = process_gloss(toks, mapping, manual)

    print("→ ASL Gloss tokens :", glosses)
    make_video(glosses, mapping, out)

if __name__ == "__main__":
    main()
