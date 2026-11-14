# TASK-011 synthetic candidate oracle

These 16 English and 16 German short postings and literal labels were authored
before the extraction implementation. They are synthetic, not applicant data.
Separate review must approve these expectations independently of parser output.

Each expected row preserves a complete literal source clause, candidate kind,
section context and detected lexical signal kinds. Kind is a draft annotation,
not an assertion that the employer requires a positive skill. Every output has
unspecified priority and needs_review, including explicit required/preferred and
negative wording; those interpretations belong to TASK-012/014.

Responsibilities and benefits/context override lexical signal kinds. Mixed
education/years clauses stay ambiguous. OR alternatives remain in one source
clause. Unknown headings reset context, unrecognized prose remains visible,
and repeated quotes are distinct occurrences. Wrapped lines and CRLF remain
literal source text. Signal surface forms are not canonical skill concepts.

The corpus proves these exact examples, not general EN/DE NLP accuracy.
