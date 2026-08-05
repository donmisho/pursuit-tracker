# Power Automate — the Excel export

One flow. Standard connectors only, so it stays inside your existing M365 licence.

## `PursuitTracker-ExportPortfolio`

Create it from <https://make.powerautomate.com> → **Create → Instant cloud flow →
Power Apps**, in the **same environment as the app**. A flow in a different environment
won't appear in the app's Add-data list, and that mismatch is easy to create and
annoying to spot.

> **Naming.** Power Apps strips non-alphanumeric characters when it binds a flow, so
> `PursuitTracker-ExportPortfolio` is referenced in Power Fx as
> `PursuitTrackerExportPortfolio`. That's the name used in
> `docs/04-screen-portfolio-list.md`.

### 1. Trigger — Power Apps (V2)

Add one input:

| Type | Name |
|---|---|
| Text | `RowsJson` |

### 2. Parse JSON

- **Content:** `RowsJson` (the trigger output)
- **Schema:**

```json
{
  "type": "array",
  "items": {
    "type": "object",
    "properties": {
      "PursuitId":       { "type": "string" },
      "PursuitName":     { "type": "string" },
      "Account":         { "type": "string" },
      "StageName":       { "type": "string" },
      "HealthName":      { "type": "string" },
      "Owner":           { "type": "string" },
      "SIs":             { "type": "string" },
      "Hype":            { "type": "string" },
      "NextActionName":  { "type": "string" },
      "NextActionDue":   { "type": "string" },
      "TargetDate":      { "type": "string" },
      "SfUrl":           { "type": "string" },
      "Fees":            { "type": "string" }
    }
  }
}
```

Every property is `string` because the app pre-formats dates, currency, and choice values
before serialising. Declaring `TargetDate` as a date here would fail the moment a pursuit
has none and the app sends `""` — which is three of your fourteen rows today.

### 3. Create CSV table

- **From:** the Parse JSON `Body`
- **Columns:** Custom, so the header row reads like a report rather than like a schema:

| Header | Value |
|---|---|
| Pursuit ID | `item()?['PursuitId']` |
| Pursuit | `item()?['PursuitName']` |
| Account | `item()?['Account']` |
| Stage | `item()?['StageName']` |
| Health | `item()?['HealthName']` |
| Owner | `item()?['Owner']` |
| Aligned SIs | `item()?['SIs']` |
| Hyperscalers | `item()?['Hype']` |
| Next action | `item()?['NextActionName']` |
| Next action due | `item()?['NextActionDue']` |
| Target decision | `item()?['TargetDate']` |
| Salesforce opportunity | `item()?['SfUrl']` |
| Estimated fees | `item()?['Fees']` |

Leaving Columns on **Automatic** works, but you get raw property names as headers and
no control over column order.

### 4. OneDrive for Business — Create file

- **Folder path:** `/Pursuit Tracker Exports`
- **File name:** `SI-pursuit-portfolio-@{formatDateTime(utcNow(),'yyyyMMdd-HHmm')}.csv`
- **File content:** the Create CSV table output

Timestamped because people export repeatedly during a review and a fixed filename means
each run silently overwrites the last.

### 5. OneDrive for Business — Create share link

- **File:** the `Id` from step 4
- **Link type:** View
- **Link scope:** Organization

### 6. Respond to a PowerApp or flow

| Type | Name | Value |
|---|---|---|
| Text | `downloadurl` | `@{concat(body('Create_share_link')?['link']?['webUrl'], '&download=1')}` |

`&download=1` is what makes the browser save the file instead of opening a OneDrive
preview tab. Without it, `Download()` in the app looks like it did nothing.

Save, then in Power Apps: **Data → Add data → the flow**, and wire
`btnDownloadExcel.OnSelect` per `docs/04-screen-portfolio-list.md`.

---

## CSV or genuine .xlsx?

The flow above produces CSV. It opens in Excel, it's one action, and it's instant
regardless of row count.

If you need a real workbook — formatting, formulas, multiple sheets — the standard-tier
route is **Excel Online (Business)**, which is included:

1. Put a template `.xlsx` in `/Pursuit Tracker Exports/_template.xlsx` containing a
   formatted table named `Portfolio` with matching headers.
2. In the flow: **OneDrive → Copy file** to a timestamped name.
3. **Apply to each** over the Parse JSON body → **Excel Online (Business) → Add a row
   into a table**.
4. Share-link the copy as above.

The cost is one API call per row inside a loop. Forty pursuits is a few seconds; a few
hundred starts to feel like a hang, and Power Automate's per-minute action limits come
into play. Set **Concurrency control** on the Apply to each to 20 if you go this way.

Start with CSV. Move to the template only if someone actually asks for formatting.

## What you get for free without any of this

The SharePoint list view has **Export to Excel** built in, and for an unfiltered dump of
one list it's already better than anything you'd build. The flow earns its place because
the mockup's footer promises the download follows the *visible* list — the app's
filtering, sorting, and the derived "next task due" column, none of which exist in
SharePoint.
