# Private job-description intake

TASK-010 stores an untrusted vacancy as source data. It does not need the career profile or generate an application. ADR-020 permits this independent draft step while TASK-009 personal acceptance remains pending.

## File or paste

Set `JAE_DATA_DIR` to an existing absolute private directory outside the checkout.

```bash
uv run jae job-ingest --text vacancy.md --job-id example-ai-role \
  --company "Example Company" --title "AI Engineer" --external-id "EX-42" --locale en
uv run jae job-ingest --text - --job-id another-role
uv run jae job-show --job-id example-ai-role
uv run jae job-show --job-id example-ai-role --revision 1
```

For stdin, paste the JD and finish with EOF (Ctrl-D in a macOS terminal). The command returns JSON containing the local job ID, revision, draft state, duplicate flag and private path. `job-show` verifies file/record integrity and displays metadata/hashes; the posting text is available at the returned directory.

Only metadata explicitly supplied through `--company`, `--title`, `--external-id`, `--source-url` and `--locale` is recorded. Company/title/locale are not inferred from text. URLs remain plain metadata and are never fetched. Locale may be `en`, `de` or `unknown`.

Job IDs use 2–64 lowercase letters/digits/underscore/hyphen, starting with a letter. If omitted, the ID is derived from the raw content hash. **Reuse the returned ID for later edits**: without it, changed content has a different fallback identity. Separate IDs keep distinct vacancies separate even if their text matches.

## Files and revisions

```text
JAE_DATA_DIR/jobs/example-ai-role/revisions/r000001/
  job_description.raw.txt
  job_description.md
  job.json
```

`job_description.raw.txt` preserves exact UTF-8 input bytes, including original newlines and Unicode. Downstream quote offsets must refer to this file's decoded Unicode codepoints, not byte offsets or normalized Markdown.

`job_description.md` is a faithful source view with only NFC Unicode and CRLF/CR-to-LF normalization. It does not translate, rewrite, classify or remove requirement-bearing lines. Markdown/HTML, shell-like fragments and embedded instructions remain untrusted text.

`job.json` binds the source/normalized hashes, raw byte/codepoint counts, normalization version, supplied metadata, locale, capture time and record digest. Capture time is not an employer publication date. State is always `draft`; intake does not record an application submission or employer outcome.

An identical **current** source/metadata/locale combination returns the same revision and capture time. Changed raw text, metadata or locale creates the next revision without altering previous files. A return to older text creates a new current revision. Omitted metadata/locale is retained; supplied fields update only those fields. The API may explicitly clear an optional metadata value with `None`; the initial CLI has no clear-field option.

Before publication, a complete stage is re-read and verified, then renamed into the numbered revision directory. Interrupted writes leave no ready partial revision. Detected concurrent publication fails without replacing the other writer's revision; retry after the other command finishes. This is local single-writer tooling, not a multi-user service.

## Limits and integrity

Input is strictly UTF-8, nonempty and at most **200,000 bytes**. Malformed, empty/BOM-only and oversized text fails with exit 2. File/stdin reads are bounded; diagnostics do not echo the posting. Paths remain under the configured private root and symlink traversal is rejected. Altered/missing/unexpected revision files or record/hash mismatches block reads and duplicate imports.

No applicant fact approval, artifact approval, requirement match or real application status is inferred from a saved posting. Extraction/matching and the application tracker are separate later work.
