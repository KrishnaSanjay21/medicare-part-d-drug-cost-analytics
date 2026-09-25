# Executive summary

Part D Atlas converts the CMS Medicare Part D Prescribers — by Geography and Drug public-use file into a reproducible analytical product. The dashboard separates national drug analysis from state comparisons so totals are not double-counted.

The project is designed to answer four questions:

1. Which drugs account for the largest share of published Part D drug cost?
2. How do utilization and cost per claim vary across drugs?
3. How do aggregate cost and utilization differ across states?
4. Do the published data pass documented completeness and reconciliation checks?

## Verified 2024 findings

- CMS national rows contain **1.711 billion claims** and **$288.57 billion in total drug cost**, or **$168.65 per claim**.
- **Eliquis** has the highest published national drug cost at **$20.77 billion**, followed by Ozempic and Jardiance.
- California has the highest state-level aggregate drug cost at **$27.33 billion**.
- Five of seven SQL checks pass without exceptions. Two warning checks identify the same published row with a missing geography code; the source row remains unchanged and is excluded from geographic summaries.

## Recommended use

Use the dashboard to prioritize high-cost drugs for deeper review and to separate high utilization from high unit cost. Normalize state comparisons for population, enrollment, and case mix before using them for performance decisions.

The results are descriptive. They should support further investigation, not clinical, formulary, or coverage decisions by themselves.
