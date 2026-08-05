# Data model — the five `pursuit-tracker` lists

This is the schema the app is built against, derived from the three screen mockups.
Your lists already exist, so **treat this as a contract to reconcile against**, not as
something to create from scratch. Run `tools/dump-list-schema.js` (see
[reconciling](#reconciling-with-your-existing-lists)) to dump what you actually have.

Two naming rules matter more than they look:

- **Internal names are not display names.** SharePoint freezes the internal name at
  creation and never changes it. A column created as "Next Task" is internally
  `Next_x0020_Task`; renamed later to "Due", it is *still* `Next_x0020_Task`. Power Fx
  binds to the display name in the designer but breaks in confusing ways when two
  columns share one. Where this doc lists a name, it is the name you should see in
  Power Apps.
- **Every child list carries `PursuitKey` (Number) in addition to its Lookup column.**
  The Lookup column is what makes the list usable in the SharePoint UI. `PursuitKey` is
  a plain number holding the parent pursuit's `ID`, and it exists because SharePoint
  delegation on `Filter(list, LookupCol.Id = x)` is unreliable, while `Filter(list,
  PursuitKey = x)` delegates cleanly. If you skip it, the app works until you pass ~500
  tasks and then silently starts truncating. See `docs/07-gaps-and-decisions.md`.

---

## 1. `pursuit-tracker-Pursuits`

The spine. One item per pursuit; every board card and list row is one of these.

| Column | Type | Notes |
|---|---|---|
| `Title` | Single line | Full pursuit name — "Northwind FY27 workplace modernization" |
| `ShortName` | Single line | Breadcrumb form — "Northwind renewal" |
| `Account` | Single line | "Elevance Health", "NiSource" |
| `Portfolio` | Choice | "SI pursuit management" — the page heading; lets you run more than one board later |
| `Stage` | Choice | **Drives the board columns.** See below |
| `PursuitOwner` | Person | Single selection. Card avatars and the Owner column read `.DisplayName` |
| `TargetCloseDate` | Date only | "September 18" on the workspace |
| `Amount` | Currency | Not shown in the mockups; carried for the Excel export |
| `AlignedSIs` | Choice, **multiple** | Fujitsu, NTT Data, Accenture, Deloitte, Infosys, TCS, Capgemini, Other |
| `Hyperscalers` | Choice, **multiple** | Microsoft, AWS, GCP, Oracle, Other |
| `SalesforceOpportunityName` | Single line | "Northwind FY27 renewal" — the link text |
| `SalesforceOpportunityUrl` | Hyperlink | Target of that link |
| `SalesforceOpportunityId` | Single line | 18-char SFDC id, for the sync job |
| `SalesforceSyncStatus` | Choice | Synced / Pending / Not linked — the pill on the workspace card, and the "Salesforce opportunity linked" subtitle in the list |
| `SalesforceLastSynced` | Date and Time | |
| `BoardOrder` | Number | Card order within a stage column. See the note under Stage |
| `IsActive` | Yes/No | Default Yes. Closed pursuits drop off the board without being deleted |

### Stage drives the board

The board columns are **not** hard-coded in the app. `App.OnStart` reads
`Choices('pursuit-tracker-Pursuits'.Stage)`, so adding a stage in SharePoint adds a
column to the board with no app edit. The mockup shows three:

1. `WM account team assimilation`
2. `Partner introduction`
3. `Preliminary scoping`

Keep them in the order you want them to appear on the board — SharePoint preserves
choice order, and the app renders them in that order.

### On `BoardOrder`

Canvas apps have no native drag-and-drop, so nothing writes to `BoardOrder`
automatically. It sorts cards within a column and is worth keeping even if you never
hand-edit it: without it, cards reorder unpredictably as items are patched. The app
sorts by `BoardOrder` then `Title`. Read
`docs/07-gaps-and-decisions.md` before you expect to drag anything.

---

## 2. `pursuit-tracker-Tasks`

Feeds the "Actions and dependencies" table on the workspace **and** the "Next task due"
line on every board card and list row.

| Column | Type | Notes |
|---|---|---|
| `Title` | Single line | "Confirm buying committee" |
| `Pursuit` | Lookup → Pursuits (`Title`) | Human-facing join |
| `PursuitKey` | Number | Delegable join. Must equal `Pursuit.Id` |
| `Phase` | Choice | Qualify / Proposal / Review / Close |
| `Effort` | Choice | Small / Medium / Large / XL |
| `Status` | Choice | Not started / In progress / At risk / Complete / Blocked |
| `DueDate` | Date only | Sorts "next task due" |
| `DueDescription` | Single line | For dependency-relative due dates. The mockup shows "After proposal" in the date slot for Legal review — when this is filled the app renders it *instead of* `DueDate` |
| `AssignedTo` | Person | |
| `DependsOnKey` | Number | `ID` of a blocking task in this same list. Optional |

"Next task due" = the earliest `DueDate` among tasks for that pursuit whose `Status`
is not Complete. Tasks with only a `DueDescription` and no `DueDate` never win that
race, which is the behavior you want.

The "At risk" pill in the mockup is `Status = "At risk"`. It is a status, not a
derived-from-date flag — a task overdue by a week still shows its real status.

---

## 3. `pursuit-tracker-Updates`

The "Status updates" feed.

| Column | Type | Notes |
|---|---|---|
| `Title` | Single line | First ~60 chars of the update. SharePoint requires a Title; the app writes it automatically |
| `Pursuit` | Lookup → Pursuits | |
| `PursuitKey` | Number | |
| `UpdateText` | Multiple lines, **plain text** | The body. Plain, not rich — rich text returns HTML that a Label renders as literal markup |
| `Source` | Choice | Manual / Voice / Teams / Email / Agent — renders as "voice update" in the byline |
| `AuthorName` | Single line | Do **not** rely on SharePoint's `Author`. Updates written by your Copilot agent would be attributed to the agent's identity, not the person who dictated them |
| `UpdateDate` | Date and Time | Drives "Today" / "Yesterday" / a date |

---

## 4. `pursuit-tracker-Documents`

The "Documents and links" card. Links only — this is deliberately not a document
library, because the mockup links out to material that lives in Teams, SharePoint, and
partner systems.

| Column | Type | Notes |
|---|---|---|
| `Title` | Single line | "Working proposal deck" |
| `Pursuit` | Lookup → Pursuits | |
| `PursuitKey` | Number | |
| `Url` | Hyperlink | |
| `DocType` | Choice | Deck / Notes / Solution outline / Contract / Other |
| `Source` | Choice | SharePoint / Teams / External |
| `SortOrder` | Number | Display order |

---

## 5. `pursuit-tracker-AIOverviews`

Both the "AI overview" card and the "AI overview history" panel read this list. One
item per *version* — history is rows, not a version field on a single row.

| Column | Type | Notes |
|---|---|---|
| `Title` | Single line | "Version 3" |
| `Pursuit` | Lookup → Pursuits | |
| `PursuitKey` | Number | |
| `VersionNumber` | Number | |
| `OverviewText` | Multiple lines, **plain text** | The narrative body |
| `IsCurrent` | Yes/No | Exactly one true per pursuit — the app enforces this on write |
| `GeneratedDate` | Date and Time | "Today", "August 1" |
| `SourceSummary` | Single line | "Salesforce + 4 materials" — the provenance line under the overview |
| `MaterialsCount` | Number | Feeds `SourceSummary` if you'd rather compose it in the app |

`IsCurrent` is the one piece of integrity the app has to maintain itself: writing a new
version must flip the previous one to No in the same operation. The Patch pattern is in
`docs/05-screen-pursuit-workspace.md`. If a write fails halfway you get two current
versions and the overview card shows whichever sorts first — worth a periodic check.

---

## Reconciling with your existing lists

I can't read SharePoint lists through the connector available to me, so I built against
the mockups. To get your real schema in about ten seconds, with no app registration and
no IT involvement:

1. Sign in to <https://westmonroepartners1.sharepoint.com/sites/PursuitTracking> in a
   browser as you normally would.
2. Open DevTools (F12) → Console.
3. Paste the contents of `tools/dump-list-schema.js` and press Enter.

It calls SharePoint's own REST API using your existing session, walks every list whose
title starts with `pursuit-tracker`, and prints display name, internal name, type, and
choice values for each column — plus a copy-pasteable summary. It only reads.

Send me that output and I'll reconcile the formulas in `docs/` against your real column
names. Until then, assume every `'pursuit-tracker-...'` reference in this repo needs a
find-and-replace pass.
