import fs from "node:fs/promises";
import { SpreadsheetFile, Workbook } from "@oai/artifact-tool";

const root = new URL("..", import.meta.url).pathname.replace(/^\/(?:([A-Za-z]:))/, "$1");
const outputDir = `${root}/outputs`;
const payload = JSON.parse(await fs.readFile(`${outputDir}/report_data.json`, "utf8"));

const wb = Workbook.create();
const summary = wb.worksheets.add("Summary");
const drugs = wb.worksheets.add("National Drugs");
const states = wb.worksheets.add("State Summary");
const quality = wb.worksheets.add("Data Quality");
const sources = wb.worksheets.add("Sources");

const navy = "#123047";
const blue = "#2374AB";
const teal = "#2A9D8F";
const lightBlue = "#EAF3F8";
const lightGray = "#F3F5F7";
const amber = "#FFF3CD";
const red = "#F8D7DA";
const font = "Arial";

for (const sheet of [summary, drugs, states, quality, sources]) {
  sheet.showGridLines = false;
}
summary.tabColor = navy;
sources.tabColor = "#7A8791";

summary.getRange("A1:N27").format.font = { name: font, size: 10, color: "#22313B" };
summary.getRange("A2:N2").format.borders = { bottom: { style: "thin", color: blue } };
summary.getRange("A2").values = [["Medicare Part D Drug Cost & Prescribing Analytics"]];
summary.getRange("A2").format.font = { name: font, size: 16, bold: true, color: navy };
summary.getRange("A3").values = [["CMS Medicare Part D Prescribers — by Geography and Drug, 2024"]];
summary.getRange("A3").format.font = { name: font, size: 10, italic: true, color: "#5C6D78" };

const drugEnd = payload.national_drugs.length + 1;
summary.getRange("A5:B10").values = [
  ["National metric", "Value"],
  ["Total claims", null],
  ["30-day fills", null],
  ["Total drug cost", null],
  ["Distinct brand/generic rows", null],
  ["Cost per claim", null],
];
summary.getRange("B6:B9").formulas = [
  [`=SUM('National Drugs'!C2:C${drugEnd})`],
  [`=SUM('National Drugs'!D2:D${drugEnd})`],
  [`=SUM('National Drugs'!E2:E${drugEnd})`],
  [`=COUNTA('National Drugs'!A2:A${drugEnd})`],
];
summary.getRange("B10").formulas = [["=B8/B6"]];
summary.getRange("A5:B5").format = { fill: navy, font: { name: font, bold: true, color: "#FFFFFF" } };
summary.getRange("A6:A10").format.fill = lightBlue;
summary.getRange("B6:B7").format.numberFormat = "#,##0";
summary.getRange("B8").format.numberFormat = "$#,##0";
summary.getRange("B9").format.numberFormat = "#,##0";
summary.getRange("B10").format.numberFormat = "$#,##0.00";

const top = payload.national_drugs.slice(0, 10);
summary.getRange("A13:E23").values = [
  ["Brand", "Generic name", "Claims", "Total drug cost", "Cost per claim"],
  ...top.map((row) => [
    row.brnd_name,
    row.gnrc_name,
    row.tot_clms,
    row.tot_drug_cst,
    row.tot_drug_cst / row.tot_clms,
  ]),
];
summary.getRange("A13:E13").format = { fill: navy, font: { name: font, bold: true, color: "#FFFFFF" }, wrapText: true };
summary.getRange("C14:C23").format.numberFormat = "#,##0";
summary.getRange("D14:D23").format.numberFormat = "$#,##0";
summary.getRange("E14:E23").format.numberFormat = "$#,##0.00";
summary.getRange("A12").values = [["Highest-cost drugs"]];
summary.getRange("A12").format.font = { name: font, size: 12, bold: true, color: navy };

const chart = summary.charts.add("bar", [summary.getRange("A13:A23"), summary.getRange("D13:D23")]);
chart.title = "Total drug cost by brand";
chart.titleTextStyle.typeface = font;
chart.hasLegend = false;
chart.xAxis = { numberFormatCode: "$0.0,,,\"B\"", numberFormatSourceLinked: false, textStyle: { typeface: font } };
chart.yAxis = { textStyle: { typeface: font, fontSize: 9 } };
chart.setPosition("G5", "N23");
if (chart.series.items.length) chart.series.items[0].fill = blue;

summary.getRange("A26:B26").values = [[
  "Scope note",
  "National KPIs use CMS national rows only. State rows are not added to national rows. Beneficiary counts are not summed across drugs as unique people.",
]];
summary.getRange("A26").format = { fill: navy, font: { name: font, bold: true, color: "#FFFFFF" } };
summary.mergeCells("B26:N27");
summary.getRange("B26").format = { fill: lightBlue, wrapText: true, verticalAlignment: "center" };

const drugHeaders = ["Brand", "Generic name", "Claims", "30-day fills", "Total drug cost", "Beneficiary records", "Opioid flag", "Cost per claim"];
drugs.getRange("A1:H1").values = [drugHeaders];
drugs.getRange(`A2:H${drugEnd}`).values = payload.national_drugs.map((row) => [
  row.brnd_name, row.gnrc_name, row.tot_clms, row.tot_30day_fills, row.tot_drug_cst,
  row.tot_benes, row.opioid_drug_flag, null,
]);
drugs.getRange("H2").formulas = [["=IF(C2=0,\"n.a.\",E2/C2)"]];
drugs.getRange(`H2:H${drugEnd}`).fillDown();
drugs.getRange(`A1:H${drugEnd}`).format.font = { name: font, size: 10, color: "#22313B" };
drugs.getRange("A1:H1").format = { fill: navy, font: { name: font, bold: true, color: "#FFFFFF" }, wrapText: true };
drugs.getRange(`C2:C${drugEnd}`).format.numberFormat = "#,##0";
drugs.getRange(`D2:D${drugEnd}`).format.numberFormat = "#,##0.0";
drugs.getRange(`E2:E${drugEnd}`).format.numberFormat = "$#,##0";
drugs.getRange(`F2:F${drugEnd}`).format.numberFormat = "#,##0";
drugs.getRange(`H2:H${drugEnd}`).format.numberFormat = "$#,##0.00";
drugs.tables.add(`A1:H${drugEnd}`, true, "NationalDrugsTable").style = "TableStyleMedium2";
drugs.freezePanes.freezeRows(1);

const stateHeaders = ["Data year", "State code", "State name", "Claims", "30-day fills", "Total drug cost", "Beneficiary records", "Cost per claim", "Opioid claim share", "Opioid cost share"];
const stateEnd = payload.states.length + 1;
states.getRange("A1:J1").values = [stateHeaders];
states.getRange(`A2:J${stateEnd}`).values = payload.states.map((row) => [
  row.data_year, row.state_code, row.state_name, row.total_claims, row.total_30day_fills,
  row.total_drug_cost, row.beneficiary_records, null, row.opioid_claim_share, row.opioid_cost_share,
]);
states.getRange("H2").formulas = [["=IF(D2=0,\"n.a.\",F2/D2)"]];
states.getRange(`H2:H${stateEnd}`).fillDown();
states.getRange(`A1:J${stateEnd}`).format.font = { name: font, size: 10, color: "#22313B" };
states.getRange("A1:J1").format = { fill: navy, font: { name: font, bold: true, color: "#FFFFFF" }, wrapText: true };
states.getRange(`D2:E${stateEnd}`).format.numberFormat = "#,##0";
states.getRange(`F2:F${stateEnd}`).format.numberFormat = "$#,##0";
states.getRange(`G2:G${stateEnd}`).format.numberFormat = "#,##0";
states.getRange(`H2:H${stateEnd}`).format.numberFormat = "$#,##0.00";
states.getRange(`I2:J${stateEnd}`).format.numberFormat = "0.00%";
states.tables.add(`A1:J${stateEnd}`, true, "StateSummaryTable").style = "TableStyleMedium2";
states.freezePanes.freezeRows(1);

const qEnd = payload.quality.length + 1;
quality.getRange("A2:E2").values = [["Check", "Severity", "Failed rows", "Status", "Scope"]];
quality.getRange(`A3:E${qEnd + 1}`).values = payload.quality.map((row) => [row.check_name, row.severity, row.failed_rows, row.status, row.scope]);
quality.getRange(`A1:E${qEnd + 1}`).format.font = { name: font, size: 10, color: "#22313B" };
quality.getRange("A1").values = [["Data quality results"]];
quality.getRange("A1").format.font = { name: font, size: 14, bold: true, color: navy };
quality.getRange("A2:E2").format = { fill: navy, font: { name: font, bold: true, color: "#FFFFFF" } };
quality.getRange(`A3:E${qEnd + 1}`).conditionalFormats.addCustom('=$D3="REVIEW"', { fill: amber, font: { color: "#7A4B00" } });
quality.getRange(`A3:E${qEnd + 1}`).conditionalFormats.addCustom('=AND($B3="Critical",$D3="REVIEW")', { fill: red, font: { color: "#842029", bold: true } });

const metadata = payload.metadata;
sources.getRange("A2:B12").values = [
  ["Source detail", "Value"],
  ["Dataset", metadata.dataset],
  ["Publisher", metadata.publisher],
  ["Data year", metadata.data_year],
  ["Dataset version ID", metadata.dataset_version_id],
  ["Dataset page", metadata.dataset_page],
  ["Download URL", metadata.download_url],
  ["Downloaded at (UTC)", `'${metadata.downloaded_at_utc}`],
  ["File size (bytes)", metadata.file_size_bytes],
  ["SHA-256", metadata.sha256],
  ["License", metadata.license],
];
sources.getRange("A1").values = [["Published source and reproducibility metadata"]];
sources.getRange("A1:B12").format.font = { name: font, size: 10, color: "#22313B" };
sources.getRange("A1").format.font = { name: font, size: 14, bold: true, color: navy };
sources.getRange("A2:B2").format = { fill: navy, font: { name: font, bold: true, color: "#FFFFFF" } };
sources.getRange("A3:A12").format.fill = lightGray;
sources.getRange("B3:B12").format.wrapText = false;

summary.getRange("A1:N30").format.verticalAlignment = "center";
summary.getRange("A1:N30").format.autofitColumns();
summary.getRange("A1:N30").format.autofitRows();
summary.getRange("A:A").format.columnWidth = 26;
summary.getRange("B:B").format.columnWidth = 28;
summary.getRange("C:E").format.columnWidth = 16;
summary.getRange("G:N").format.columnWidth = 12;
summary.getRange("B26:N27").format.rowHeight = 34;

for (const sheet of [drugs, states, quality, sources]) {
  const used = sheet.getUsedRange();
  used.format.verticalAlignment = "center";
  used.format.autofitColumns();
  used.format.autofitRows();
}
drugs.getRange(`A1:B${drugEnd}`).format.columnWidth = 28;
states.getRange(`C1:C${stateEnd}`).format.columnWidth = 24;
quality.getRange(`A1:A${qEnd + 1}`).format.columnWidth = 46;
sources.getRange("A1:A12").format.columnWidth = 24;
sources.getRange("B1:B12").format.columnWidth = 110;

wb.recalculate();
await fs.mkdir(outputDir, { recursive: true });
const previewRanges = {
  "Summary": "A1:N27",
  "National Drugs": "A1:H30",
  "State Summary": "A1:J30",
  "Data Quality": `A1:E${qEnd + 1}`,
  "Sources": "A1:B12",
};
for (const [sheetName, range] of Object.entries(previewRanges)) {
  const preview = await wb.render({ sheetName, range, scale: 1, format: "png" });
  const slug = sheetName.toLowerCase().replaceAll(" ", "_");
  await fs.writeFile(`${outputDir}/preview_${slug}.png`, new Uint8Array(await preview.arrayBuffer()));
}
const output = await SpreadsheetFile.exportXlsx(wb);
await output.save(`${outputDir}/medicare_part_d_client_report.xlsx`);

const summaryCheck = await wb.inspect({ kind: "table", range: "Summary!A1:N27", include: "values,formulas", tableMaxRows: 30, tableMaxCols: 14 });
const errorCheck = await wb.inspect({ kind: "match", searchTerm: "#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A|#NUM!|#NULL!|#SPILL!|#CALC!", options: { useRegex: true, maxResults: 100 }, summary: "formula error scan" });
console.log(summaryCheck.ndjson);
console.log(errorCheck.ndjson);
