# Data dictionary

The analytical model retains the published CMS fields and adds transparent derived metrics.

| Field | Definition | Unit |
|---|---|---|
| `prscrbr_geo_lvl` | CMS aggregation level (`National` or `State`) | Category |
| `prscrbr_geo_cd` | Two-character state or territory code; blank for national rows | Code |
| `brnd_name` | Drug brand name published by CMS | Text |
| `gnrc_name` | Generic ingredient name published by CMS | Text |
| `tot_prscrbrs` | Distinct prescribers reported by CMS | Prescribers |
| `tot_clms` | Prescription fills including refills | Claims |
| `tot_30day_fills` | Standardized 30-day fills | Fills |
| `tot_drug_cst` | Total prescription drug cost from all payment sources represented by CMS | USD |
| `tot_benes` | Beneficiary count for the row; some values are suppressed | Beneficiary records |
| `lis_bene_cst_shr` | Low-income subsidy beneficiary cost sharing | USD |
| `nonlis_bene_cst_shr` | Non-LIS beneficiary cost sharing | USD |
| `opioid_drug_flag` | CMS opioid indicator | Y/N |
| `cost_per_claim` | `tot_drug_cst / tot_clms` | USD per claim |
| `cost_per_30day_fill` | `tot_drug_cst / tot_30day_fills` | USD per fill |
| `beneficiary_cost_share` | `(LIS + non-LIS cost sharing) / total drug cost` | Ratio |

`tot_drug_cst` is not the amount paid only by Medicare. It includes payments by plans, beneficiaries, government subsidies, and other third parties represented in the CMS source.

