# Power BI handoff

Power BI Desktop requires Windows. The local Mac dashboard provides a working investigation interface; it is not a substitute for demonstrating Power BI skills. A Windows PC or Windows environment is needed for the native `.pbix` artifact.

## Sources

Run `scripts/export.py`, then import these CSV tables from `exports/`: vehicles, complaints, complaint_vehicles, complaint_components, recalls, recall_vehicles. Monthly reporting and review queue are independent audit/reference extracts. Do not append monthly rows to complaint rows.

CSV export excludes narratives and VINs. Import identifiers as text, dates as Date, severity counts as whole numbers, and booleans as True/False. Preserve nulls. Store the source folder as a Power Query parameter.

## Relationships

Use single-direction, one-to-many relationships:

- vehicles[vehicle_key] → complaint_vehicles[vehicle_key]
- complaints[odi_number] → complaint_vehicles[odi_number]
- complaints[odi_number] → complaint_components[odi_number]
- vehicles[vehicle_key] → recall_vehicles[vehicle_key]
- recalls[campaign_number] → recall_vehicles[campaign_number]
- A continuous Date table → complaints[received_date]

Use a separate Recall Date table for recalls[report_date] if needed. Avoid automatic bidirectional filtering across multiple bridge tables.

Vehicle and component slicers will not automatically filter the parent complaints table through single-direction bridges. Define the count explicitly:

```dax
Selected Complaints =
VAR VehicleIDs = VALUES(complaint_vehicles[odi_number])
VAR ComponentIDs = VALUES(complaint_components[odi_number])
RETURN
    CALCULATE(
        DISTINCTCOUNT(complaints[odi_number]),
        KEEPFILTERS(TREATAS(VehicleIDs, complaints[odi_number])),
        KEEPFILTERS(TREATAS(ComponentIDs, complaints[odi_number]))
    )

Selected Recall Campaigns =
VAR CampaignIDs = VALUES(recall_vehicles[campaign_number])
RETURN
    CALCULATE(
        DISTINCTCOUNT(recalls[campaign_number]),
        KEEPFILTERS(TREATAS(CampaignIDs, recalls[campaign_number]))
    )
```

Compare these measures with SQL for individual model-years, combined families, multi-component complaints, and date slices. Do not use COUNTROWS on a flattened complaint/component/recall join.

## Pages

1. Reporting trends: distinct reports, equal-period comparisons, coverage and refresh date.
2. Investigation groups: component windows, minimum volume, evidence reason, no reliability league table.
3. Recall context: campaign details with explicit model/year scope limitation.
4. Data quality: exclusions, missingness, source reconciliation, definitions.

The measures above are implementation guidance. They must be verified in Power BI before claiming a completed Power BI deliverable.

Official requirements: https://learn.microsoft.com/en-us/power-bi/fundamentals/desktop-get-the-desktop
