# SAA-C03 Practice Bench

A static, no-build practice exam runner for the AWS Certified Solutions Architect
Associate (SAA-C03) exam. One question at a time, optional 130-minute timer that
scales with set size, instant feedback, and an explanation after every answer.

## Running it

It fetches JSON over `fetch()`, so open it through a local server rather than
double-clicking `index.html` (otherwise the browser blocks the file reads):

```bash
python3 -m http.server -d saa-practice-exam 8000
```

Then open <http://localhost:8000>. This also works unmodified on GitHub Pages
or any static host.

## What's included

- **Mock Exam 1-7** (`data/exam-*.json`) — 421 single-answer questions sourced
  and adapted from [Iamrushabhshahh/aws-saa-c03-practice-questions](https://github.com/Iamrushabhshahh/aws-saa-c03-practice-questions),
  batched into (close to) real exam-sized sets of 65 with a matching timer
  scaled to 130 minutes per 65 questions. Every option on every question
  (1,684 total) has its own hand-written explanation — why the correct answer
  satisfies the question, and why each wrong option specifically fails — not
  just the source's rationale for the correct choice.
- **Curated drill** (`data/curated.json`) — 33 hand-written questions covering
  core SAA domains, untimed, same per-option explanation treatment.
- Options are shuffled per question at build time, so the correct answer isn't
  always in the same position.

## Limitations

The source dump's answer key only had reliable, unambiguous text for
single-answer questions. "Choose two/three" questions in that source
interleave the correct-option markers with per-option explanation prose in a
way that isn't safely parseable by script — rather than risk shipping a wrong
answer key, `scripts/build_questions.py` **drops multi-select questions
entirely** (60 of the original ~540 were excluded this way). Everything that
made it into `data/exam-*.json` was spot-checked by hand for correctness
against known SAA-C03 content, but given the scale (421 questions), treat it
as a supplement to official AWS material, not a replacement.

The per-option explanations in `data/exam-*.json` were authored by AI agents
against the source dump's own `"c": true` / `"c": false` labels. While doing
so, the agents flagged 6 questions (2 each in exam-2, exam-3, exam-4) where
the source's own answer key looked questionable against standard AWS
guidance — e.g. crediting Parameter Store rather than Secrets Manager for
automatic credential rotation, or Amazon Inspector rather than AWS Config for
detecting unencrypted EBS volumes. Rather than ship a disputed answer key,
**those 6 questions were removed outright** (hence exam-2/3/4 running 63
questions instead of 65). A smaller number of other questions had an *empty*
source rationale rather than a disputed one — those were kept, with the
explanation written from general AWS knowledge instead of paraphrased from an
existing answer; worth a slightly more skeptical read but not removed.

None of this changes any remaining `"c"` (correct-answer) flag — only the
wording of the `"w"` explanations. If you spot another wrong flag, remove or
fix it directly in the relevant `data/exam-N.json` and update its count in
`data/manifest.json` to match.

## Regenerating the data

```bash
git clone https://github.com/Iamrushabhshahh/aws-saa-c03-practice-questions scripts/repo-src
pdftotext "scripts/repo-src/AWS Certified Solutions Architect Associate SAA-C03.pdf" scripts/repo-src/full.txt
python3 scripts/build_questions.py scripts/repo-src
python3 scripts/build_curated.py
```

## Project layout

```
index.html          # shell + set picker + quiz UI mount point
style.css
app.js              # all quiz logic: picker, timer, grading, summary
data/
  manifest.json     # list of available mock exams
  exam-1..7.json     # 65 questions each; exam-2/3/4 have 63 (2 disputed
                      # questions removed each), exam-7 has the 37 leftover
  curated.json       # the 33 hand-written questions
scripts/
  build_questions.py # parses the source PDF + solution dump into exam-*.json
  build_curated.py   # writes curated.json from the hand-written question bank
```
