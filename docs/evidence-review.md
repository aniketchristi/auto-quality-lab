# Evidence review protocol

The first review packet compares growth-only, equal-budget volume-only, and overlapping selections at three fixed receipt cutoffs: December 31, 2024; June 30, 2025; and December 31, 2025. It uses the default 90-day window and minimum of 10 reports. Within each cutoff, sample up to three groups per stratum and up to three recent complaints per group.

Selection uses SHA-256 ranks with a published seed, not a random choice that changes between runs. Identical inputs yield identical selections. The packet stores a hash of the source manifest. It contains narratives and must remain local in the Git-ignored data/processed directory. Run `python scripts/prepare_review.py` to generate it. The script refuses to overwrite a packet with completed review work.

## What to record

Read each narrative and assign a short symptom code describing the reported behavior. Record whether it supports the listed component as yes, no, or uncertain. Evidence specificity is specific, vague, or insufficient. Note reporting delays and whether the complaint supplies enough detail to distinguish a recurring symptom from an unrelated issue. Keep review notes free of names, addresses, contact details, and VINs.

Leave review_status as pending until a person has read the evidence. Mark completed only after the fields have been considered. Unknown or ambiguous evidence should stay explicit; it is not a negative finding. Do not label a complaint as a verified defect or a confirmed campaign match based on narrative similarity.

## How to interpret the review

The sample is intentionally small and stratified by selection method. It does not estimate population prevalence, precision, or recall. The reviewer sees the selection stratum, so assessment is not blinded. Complaints can recur across components or cutoffs; review assignments are not independent incidents. Report distinct complaint counts alongside assignment counts.

After reviewing, compare symptom consistency and evidence specificity across strata. Use those observations to choose investigation case studies, including an ambiguous example. Confirm any recall context with campaign documents before making claims. Add a second reviewer or blind the stratum in a later round if the project needs a stronger comparison.
