# Model-label coverage audit

Audited October 8, 2026: 40 official NHTSA available-model responses (four makes, five model years, complaint and recall lists). All responses passed source-count checks; repeated labels were deduplicated.

The loaded cohort is an exact-label cohort. Separate candidate labels below are excluded from ingestion. Substring matches require review; they are not a complete manufacturer model catalog.

| Make | Year | List | Related labels returned |
| --- | --- | --- | --- |
| HONDA | 2018 | Complaints | CIVIC: CIVIC, CIVIC SI, CIVIC TYPE R; ACCORD: ACCORD, ACCORD HYBRID |
| HONDA | 2018 | Recalls | CIVIC: CIVIC, CIVIC SI, CIVIC TYPE R; ACCORD: ACCORD, ACCORD HYBRID |
| HONDA | 2019 | Complaints | CIVIC: CIVIC, CIVIC HATCH, CIVIC HATCH TYPE-R, CIVIC SI; ACCORD: ACCORD, ACCORD HYBRID |
| HONDA | 2019 | Recalls | CIVIC: CIVIC, CIVIC HATCH, CIVIC HATCH TYPE-R, CIVIC SI; ACCORD: ACCORD, ACCORD HYBRID |
| HONDA | 2020 | Complaints | CIVIC: CIVIC, CIVIC HATCH, CIVIC HATCH TYPE-R, CIVIC HATCHBACK, CIVIC SI; ACCORD: ACCORD, ACCORD HYBRID |
| HONDA | 2020 | Recalls | CIVIC: CIVIC, CIVIC HATCH, CIVIC HATCH TYPE-R, CIVIC HATCHBACK, CIVIC SI; ACCORD: ACCORD, ACCORD HYBRID |
| HONDA | 2021 | Complaints | CIVIC: CIVIC, CIVIC HATCH, CIVIC HATCH TYPE-R; ACCORD: ACCORD, ACCORD HYBRID |
| HONDA | 2021 | Recalls | CIVIC: CIVIC, CIVIC HATCH, CIVIC HATCH TYPE-R; ACCORD: ACCORD, ACCORD HYBRID |
| HONDA | 2022 | Complaints | CIVIC: CIVIC, CIVIC HATCHBACK, CIVIC SEDAN SI; ACCORD: ACCORD, ACCORD HYBRID |
| HONDA | 2022 | Recalls | CIVIC: CIVIC, CIVIC HATCHBACK, CIVIC SEDAN SI; ACCORD: ACCORD, ACCORD HYBRID |
| TOYOTA | 2018 | Complaints | COROLLA: COROLLA, COROLLA IM; CAMRY: CAMRY, CAMRY HYBRID |
| TOYOTA | 2018 | Recalls | COROLLA: COROLLA, COROLLA IM; CAMRY: CAMRY, CAMRY HYBRID |
| TOYOTA | 2019 | Complaints | COROLLA: COROLLA; CAMRY: CAMRY, CAMRY HYBRID |
| TOYOTA | 2019 | Recalls | COROLLA: COROLLA; CAMRY: CAMRY, CAMRY HYBRID |
| TOYOTA | 2020 | Complaints | COROLLA: COROLLA, COROLLA HYBRID; CAMRY: CAMRY, CAMRY HYBRID |
| TOYOTA | 2020 | Recalls | COROLLA: COROLLA, COROLLA HYBRID; CAMRY: CAMRY, CAMRY HYBRID |
| TOYOTA | 2021 | Complaints | COROLLA: COROLLA; CAMRY: CAMRY, CAMRY HYBRID |
| TOYOTA | 2021 | Recalls | COROLLA: COROLLA; CAMRY: CAMRY, CAMRY HYBRID |
| TOYOTA | 2022 | Complaints | COROLLA: COROLLA, COROLLA CROSS, COROLLA HATCHBACK, COROLLA HYBRID; CAMRY: CAMRY, CAMRY HYBRID |
| TOYOTA | 2022 | Recalls | COROLLA: COROLLA, COROLLA CROSS, COROLLA HATCHBACK, COROLLA HYBRID; CAMRY: CAMRY, CAMRY HYBRID |
| MAZDA | 2018 | Complaints | MAZDA3: MAZDA3 |
| MAZDA | 2018 | Recalls | MAZDA3: MAZDA3 |
| MAZDA | 2019 | Complaints | MAZDA3: MAZDA3 |
| MAZDA | 2019 | Recalls | MAZDA3: MAZDA3 |
| MAZDA | 2020 | Complaints | MAZDA3: MAZDA3 |
| MAZDA | 2020 | Recalls | MAZDA3: MAZDA3 |
| MAZDA | 2021 | Complaints | MAZDA3: MAZDA3 |
| MAZDA | 2021 | Recalls | MAZDA3: MAZDA3 |
| MAZDA | 2022 | Complaints | MAZDA3: MAZDA3 |
| MAZDA | 2022 | Recalls | MAZDA3: MAZDA3 |
| VOLKSWAGEN | 2018 | Complaints | GOLF: E-GOLF, GOLF, GOLF GTI, GOLF R, GOLF SPORTWAGEN |
| VOLKSWAGEN | 2018 | Recalls | GOLF: E-GOLF, GOLF, GOLF GTI, GOLF R, GOLF SPORTWAGEN |
| VOLKSWAGEN | 2019 | Complaints | GOLF: E-GOLF, GOLF, GOLF GTI, GOLF R, GOLF SPORTWAGEN |
| VOLKSWAGEN | 2019 | Recalls | GOLF: E-GOLF, GOLF, GOLF GTI, GOLF R, GOLF SPORTWAGEN |
| VOLKSWAGEN | 2020 | Complaints | GOLF: GOLF, GOLF GTI |
| VOLKSWAGEN | 2020 | Recalls | GOLF: GOLF, GOLF GTI |
| VOLKSWAGEN | 2021 | Complaints | GOLF: GOLF, GOLF GTI |
| VOLKSWAGEN | 2021 | Recalls | GOLF: GOLF, GOLF GTI |
| VOLKSWAGEN | 2022 | Complaints | GOLF: GOLF GTI, GOLF R |
| VOLKSWAGEN | 2022 | Recalls | GOLF: GOLF GTI, GOLF R |

All configured labels appear in both lists for all scoped years except VOLKSWAGEN GOLF 2022, which appears in neither list. Absence from these issue-specific lists does not establish that a vehicle was never manufactured or sold.

## Scope decisions

Keep the six exact labels as the initial investigation cohort. Exclude separately listed hybrids, body styles, and performance models from claims about coverage. COROLLA CROSS is outside the passenger-car scope. GOLF SPORTWAGEN and E-GOLF require separate body-style/powertrain cohorts. Do not silently merge any variant into its base label: complaint IDs may overlap and distinct counting must be rechecked after an expansion.

MAZDA3 has no additional substring candidate in these lists. This does not prove trim or powertrain completeness. A missing related label cannot be interpreted as zero complaints for that variant.

The 2022 GOLF row remains a configured query with no list evidence. Do not interpret it as a monitored vehicle population with no failures. Mark it as unavailable label coverage in analysis.

## Reproduce

Run `python scripts/audit_coverage.py` in the project environment. Local raw responses and the SHA-256 provenance manifest are saved under data/raw and data/processed. The complaint/recall dataset is not modified by this audit.

[NHTSA API documentation](https://www.nhtsa.gov/nhtsa-datasets-and-apis) documents issue-specific model lists. Each queried URL and retrieval time is preserved in the local coverage_audit.json manifest.
