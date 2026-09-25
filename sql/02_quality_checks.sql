DROP TABLE IF EXISTS data_quality_results;
CREATE TABLE data_quality_results AS
WITH checks AS (
    SELECT 'Source row count is positive' AS check_name,
           'Critical' AS severity,
           CASE WHEN COUNT(*) > 0 THEN 0 ELSE 1 END AS failed_rows,
           'raw_part_d_geo_drug' AS scope
    FROM raw_part_d_geo_drug

    UNION ALL
    SELECT 'Required geography fields are populated', 'Warning', COUNT(*), 'mart_part_d_geo_drug'
    FROM mart_part_d_geo_drug
    WHERE prscrbr_geo_lvl = '' OR prscrbr_geo_desc = ''

    UNION ALL
    SELECT 'Drug names are populated', 'Critical', COUNT(*), 'mart_part_d_geo_drug'
    FROM mart_part_d_geo_drug
    WHERE brnd_name IN ('', 'Unknown') OR gnrc_name IN ('', 'Unknown')

    UNION ALL
    SELECT 'Claims and costs are non-negative', 'Critical', COUNT(*), 'mart_part_d_geo_drug'
    FROM mart_part_d_geo_drug
    WHERE tot_clms < 0 OR tot_30day_fills < 0 OR tot_drug_cst < 0

    UNION ALL
    SELECT 'National drug keys are unique', 'Warning', COUNT(*), 'National rows'
    FROM (
        SELECT data_year, brnd_name, gnrc_name
        FROM mart_part_d_geo_drug
        WHERE prscrbr_geo_lvl = 'National'
        GROUP BY data_year, brnd_name, gnrc_name
        HAVING COUNT(*) > 1
    )

    UNION ALL
    SELECT 'State geographies map to reporting codes', 'Warning', COUNT(*), 'State rows'
    FROM mart_part_d_geo_drug AS m
    LEFT JOIN state_reference AS s ON m.prscrbr_geo_cd = s.state_fips
    WHERE m.prscrbr_geo_lvl = 'State' AND (m.prscrbr_geo_desc = '' OR s.state_code IS NULL)

    UNION ALL
    SELECT 'Beneficiary cost share does not exceed total drug cost', 'Warning', COUNT(*), 'mart_part_d_geo_drug'
    FROM mart_part_d_geo_drug
    WHERE COALESCE(lis_bene_cst_shr, 0) + COALESCE(nonlis_bene_cst_shr, 0) > tot_drug_cst + 0.01
)
SELECT
    check_name,
    severity,
    failed_rows,
    CASE WHEN failed_rows = 0 THEN 'PASS' ELSE 'REVIEW' END AS status,
    scope
FROM checks;
