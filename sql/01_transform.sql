DROP TABLE IF EXISTS mart_part_d_geo_drug;

CREATE TABLE mart_part_d_geo_drug AS
SELECT
    data_year,
    prscrbr_geo_lvl,
    prscrbr_geo_cd,
    prscrbr_geo_desc,
    brnd_name,
    gnrc_name,
    CAST(tot_prscrbrs AS REAL) AS tot_prscrbrs,
    CAST(tot_clms AS REAL) AS tot_clms,
    CAST(tot_30day_fills AS REAL) AS tot_30day_fills,
    CAST(tot_drug_cst AS REAL) AS tot_drug_cst,
    CAST(tot_benes AS REAL) AS tot_benes,
    CAST(ge65_tot_clms AS REAL) AS ge65_tot_clms,
    CAST(ge65_tot_30day_fills AS REAL) AS ge65_tot_30day_fills,
    CAST(ge65_tot_drug_cst AS REAL) AS ge65_tot_drug_cst,
    CAST(ge65_tot_benes AS REAL) AS ge65_tot_benes,
    CAST(lis_bene_cst_shr AS REAL) AS lis_bene_cst_shr,
    CAST(nonlis_bene_cst_shr AS REAL) AS nonlis_bene_cst_shr,
    opioid_drug_flag,
    opioid_la_drug_flag,
    antbtc_drug_flag,
    antpsyct_drug_flag,
    CAST(tot_drug_cst AS REAL) / NULLIF(CAST(tot_clms AS REAL), 0) AS cost_per_claim,
    CAST(tot_drug_cst AS REAL) / NULLIF(CAST(tot_30day_fills AS REAL), 0) AS cost_per_30day_fill,
    CAST(tot_clms AS REAL) / NULLIF(CAST(tot_benes AS REAL), 0) AS claims_per_beneficiary_record,
    CAST(ge65_tot_drug_cst AS REAL) / NULLIF(CAST(tot_drug_cst AS REAL), 0) AS age65_cost_share,
    (COALESCE(CAST(lis_bene_cst_shr AS REAL), 0) + COALESCE(CAST(nonlis_bene_cst_shr AS REAL), 0))
      / NULLIF(CAST(tot_drug_cst AS REAL), 0) AS beneficiary_cost_share
FROM raw_part_d_geo_drug;

CREATE INDEX idx_mart_geo ON mart_part_d_geo_drug(prscrbr_geo_lvl, prscrbr_geo_cd);
CREATE INDEX idx_mart_drug ON mart_part_d_geo_drug(brnd_name, gnrc_name);
CREATE INDEX idx_mart_flags ON mart_part_d_geo_drug(opioid_drug_flag, antbtc_drug_flag);

DROP VIEW IF EXISTS v_state_summary;
CREATE VIEW v_state_summary AS
SELECT
    m.data_year,
    s.state_code,
    m.prscrbr_geo_cd AS state_fips,
    m.prscrbr_geo_desc AS state_name,
    SUM(m.tot_clms) AS total_claims,
    SUM(m.tot_30day_fills) AS total_30day_fills,
    SUM(m.tot_drug_cst) AS total_drug_cost,
    SUM(m.tot_benes) AS beneficiary_records,
    SUM(m.tot_drug_cst) / NULLIF(SUM(m.tot_clms), 0) AS cost_per_claim,
    SUM(CASE WHEN m.opioid_drug_flag = 'Y' THEN m.tot_clms ELSE 0 END)
      / NULLIF(SUM(m.tot_clms), 0) AS opioid_claim_share,
    SUM(CASE WHEN m.opioid_drug_flag = 'Y' THEN m.tot_drug_cst ELSE 0 END)
      / NULLIF(SUM(m.tot_drug_cst), 0) AS opioid_cost_share
FROM mart_part_d_geo_drug AS m
JOIN state_reference AS s ON m.prscrbr_geo_cd = s.state_fips
WHERE m.prscrbr_geo_lvl = 'State' AND m.prscrbr_geo_desc <> ''
GROUP BY m.data_year, s.state_code, m.prscrbr_geo_cd, m.prscrbr_geo_desc;

DROP TABLE IF EXISTS pipeline_runs;
CREATE TABLE pipeline_runs (
    run_id INTEGER PRIMARY KEY AUTOINCREMENT,
    run_at_utc TEXT NOT NULL,
    source_rows INTEGER NOT NULL,
    data_year INTEGER NOT NULL,
    status TEXT NOT NULL
);
