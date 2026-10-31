import re, json, random, difflib, sys, subprocess
from pathlib import Path

# Regenerating requires a local checkout of the source question dump:
#   git clone https://github.com/Iamrushabhshahh/aws-saa-c03-practice-questions repo-src
#   pdftotext "repo-src/AWS Certified Solutions Architect Associate SAA-C03.pdf" repo-src/full.txt
# Then run this script from the project root: python3 scripts/build_questions.py [path-to-repo-src]
SRC = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("repo-src")
PDF_TXT = SRC / "full.txt"
SOL_TXT = SRC / "AWS SAA-03 Solution.txt"

def load_pdf_questions():
    text = PDF_TXT.read_text(encoding="utf-8", errors="replace")
    text = text.replace("\x0c", "\n")
    text = re.sub(r"\nTopic \d+ - Exam [A-Z]\n", "\n", text)
    blocks = re.split(r"\nQuestion #(\d+)\s*\n", text)
    # blocks[0] is preamble, then pairs of (num, body)
    out = {}
    for i in range(1, len(blocks), 2):
        num = int(blocks[i])
        body = blocks[i+1]
        body = re.sub(r"^\s*Topic \d+\s*\n", "", body)
        # find option markers at start of line: "A. " .. "E. "
        matches = list(re.finditer(r"(?m)^([A-F])\.\s+", body))
        if not matches:
            continue
        qtext = body[:matches[0].start()].strip()
        qtext = re.sub(r"\s+\n", " ", qtext)
        qtext = re.sub(r"\n+", " ", qtext)
        qtext = re.sub(r"\s{2,}", " ", qtext).strip()
        opts = {}
        for j, m in enumerate(matches):
            letter = m.group(1)
            start = m.end()
            end = matches[j+1].start() if j+1 < len(matches) else len(body)
            otext = body[start:end]
            otext = re.sub(r"\s+\n", " ", otext)
            otext = re.sub(r"\n+", " ", otext)
            otext = re.sub(r"\s{2,}", " ", otext).strip()
            if otext:
                opts[letter] = otext
        multi = bool(re.search(r"\(Choose\s+(two|TWO|2|three|THREE|3)\.?\)", qtext, re.I))
        n_correct = 1
        mm = re.search(r"\(Choose\s+(two|TWO|2|three|THREE|3)\.?\)", qtext, re.I)
        if mm:
            w = mm.group(1).lower()
            n_correct = 3 if w in ("three", "3") else 2
        if len(opts) >= 2 and qtext:
            out[num] = {"q": qtext, "opts": opts, "n_correct": n_correct}
    return out

def load_solution_blocks():
    text = SOL_TXT.read_text(encoding="utf-8", errors="replace")
    blocks = re.split(r"\n-{3,}\n+", text)
    out = {}
    for b in blocks:
        b = b.strip()
        m = re.match(r"^(\d+)\]\s*(.*)$", b, re.S)
        if not m:
            continue
        num = int(m.group(1))
        rest = m.group(2)
        paras = [p.strip() for p in re.split(r"\n\s*\n", rest) if p.strip()]
        if len(paras) < 2:
            continue
        # question paragraph(s): everything up to and including the last paragraph containing '?'
        qend_idx = None
        for idx, p in enumerate(paras):
            if "?" in p:
                qend_idx = idx
        if qend_idx is None or qend_idx + 1 >= len(paras):
            continue
        remaining_text = "\n\n".join(paras[qend_idx + 1:])
        lines = remaining_text.split("\n")
        letter_line_re = re.compile(r"^\s*([A-F])\.\s+(.*)$")
        leading_letter_lines = []
        consumed = 0
        for i, line in enumerate(lines):
            if not line.strip():
                consumed = i + 1
                continue
            lm = letter_line_re.match(line)
            if lm:
                leading_letter_lines.append(lm.group(2).strip())
                consumed = i + 1
            else:
                break
        if leading_letter_lines:
            answer_texts = leading_letter_lines
            explanation = "\n".join(lines[consumed:]).strip()
        else:
            # no letter-prefixed lines: treat the first paragraph as one
            # unlabeled answer blob (single-answer style)
            rem_paras = [p.strip() for p in re.split(r"\n\s*\n", remaining_text) if p.strip()]
            answer_texts = [rem_paras[0]] if rem_paras else []
            explanation = "\n\n".join(rem_paras[1:]).strip()
        out[num] = {"answer_texts": answer_texts, "explanation": explanation}
    return out

def norm(s):
    s = s.lower()
    s = re.sub(r"[^a-z0-9 ]", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s

def best_match(ans_text, opts, exclude=()):
    ans_norm = norm(ans_text)
    scores = []
    for letter, otext in opts.items():
        if letter in exclude:
            continue
        onorm = norm(otext)
        ratio = difflib.SequenceMatcher(None, ans_norm, onorm).ratio()
        contains = 1.0 if (len(onorm) > 20 and onorm in ans_norm) else 0.0
        contains2 = 1.0 if (len(ans_norm) > 20 and ans_norm in onorm) else 0.0
        score = max(ratio, contains, contains2)
        scores.append((score, letter))
    scores.sort(reverse=True)
    return scores[0] if scores else (0.0, None)

def match_answers(pdf_q, sol):
    matched = {}
    dropped = []
    skipped_multi = 0
    for num, pq in pdf_q.items():
        if num not in sol:
            continue
        n_correct = pq["n_correct"]
        if n_correct != 1:
            # Choose-two/three dumps interleave correct-option markers with
            # per-option explanation prose in a way that isn't reliably
            # distinguishable by script; skip rather than risk a wrong key.
            skipped_multi += 1
            continue
        answer_texts = sol[num]["answer_texts"]
        opts = pq["opts"]
        if not answer_texts:
            dropped.append((num, 0.0))
            continue
        score, letter = best_match(answer_texts[0], opts)
        if letter is None or score < 0.35:
            dropped.append((num, score))
            continue
        matched[num] = {
            "q": pq["q"],
            "opts": opts,
            "correct": [letter],
            "explanation": sol[num]["explanation"],
        }
    print("Skipped multi-select (choose two/three):", skipped_multi)
    return matched, dropped

def build_final(matched, seed=42):
    rng = random.Random(seed)
    final = []
    for num in sorted(matched.keys()):
        m = matched[num]
        letters = sorted(m["opts"].keys())
        items = [{"t": m["opts"][l], "c": l in m["correct"]} for l in letters]
        rng.shuffle(items)
        final.append({
            "src_num": num,
            "q": m["q"],
            "multi": len(m["correct"]) > 1,
            "n_correct": len(m["correct"]),
            "o": items,
            "explain": m["explanation"],
        })
    return final

if __name__ == "__main__":
    pdf_q = load_pdf_questions()
    sol = load_solution_blocks()
    print("PDF questions parsed:", len(pdf_q))
    print("Solution blocks parsed:", len(sol))
    matched, dropped = match_answers(pdf_q, sol)
    print("Matched with confident answer:", len(matched))
    print("Dropped (low confidence):", len(dropped))
    if dropped:
        print("Sample dropped:", dropped[:10])
    final = build_final(matched)

    EXAM_SIZE = 65
    rng = random.Random(99)
    order = list(range(len(final)))
    rng.shuffle(order)  # mix topics across each mock exam instead of PDF order
    shuffled = [final[i] for i in order]

    out_dir = Path(__file__).resolve().parent.parent / "data"
    out_dir.mkdir(exist_ok=True)
    batches = [shuffled[i:i + EXAM_SIZE] for i in range(0, len(shuffled), EXAM_SIZE)]
    manifest = []
    for n, batch in enumerate(batches, start=1):
        fname = f"exam-{n}.json"
        (out_dir / fname).write_text(json.dumps(batch, ensure_ascii=False), encoding="utf-8")
        manifest.append({"file": fname, "label": f"Mock Exam {n}", "count": len(batch)})
        print(f"Wrote {fname}: {len(batch)} questions")
    (out_dir / "manifest.json").write_text(json.dumps({"exams": manifest}, ensure_ascii=False, indent=2), encoding="utf-8")
    print("Total questions used:", len(final), "across", len(batches), "batches")
