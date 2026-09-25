# Methodology

## Source

The project uses the 2024 Medicare Part D Prescribers — by Geography and Drug public-use file published by the Centers for Medicare & Medicaid Services.

## Processing

1. Download the versioned CMS CSV.
2. Record the source URL, version identifier, download timestamp, file size, and SHA-256 checksum.
3. Preserve the published raw fields in SQLite.
4. Convert documented numeric fields to numeric types.
5. Build national drug and state comparison marts in SQL.
6. Run data-quality checks before dashboard use.

## Metric rules

- National KPIs use only rows where `Prscrbr_Geo_Lvl = 'National'`.
- State comparisons use only rows where `Prscrbr_Geo_Lvl = 'State'`.
- National and state rows are never added together.
- Cost per claim uses total drug cost divided by total claims for the same population.
- Beneficiary counts are not summed across drugs to estimate unique beneficiaries.

