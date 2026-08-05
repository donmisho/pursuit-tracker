# Screen — `scrPortfolioList`

The same portfolio as a reportable table, plus the Excel download.

```
scrPortfolioList
├── nav bar
├── lblPageTitle / lblPageSub
├── btnDownloadExcel
├── recHeaderRule + six column-header labels
├── galPortfolioList             ◄── one row per pursuit
│   ├── lblRowTitle / lblRowSfLink
│   ├── lblRowStage
│   ├── recRowAvatar + lblRowInitials + lblRowOwner
│   ├── galRowSIs / galRowHype   ◄── chips
│   ├── lblRowNextTask + lblRowNextDue
│   └── recRowDivider
└── lblFooterNote
```

## Screen

| Property | Formula |
|---|---|
| `Fill` | `=ClrPage` |
| `OnVisible` | the same `LoadPortfolio` block the board uses (from `src/App.OnStart.powerfx`) |

## Header

| Control | Property | Formula |
|---|---|---|
| `lblPageTitle` | `Text` | `="SI pursuit management"` |
| `lblPageSub` | `Text` | `="A reportable view of the same portfolio shown on the board."` |
| `btnDownloadExcel` | `Text` | `="Download Excel"` |
| | `X` | `=Parent.Width - Self.Width - GapPage` |
| | `Fill` / `Color` / `HoverFill` | `=ClrAccent` / `=ClrAccentText` / `=ClrAccentHover` |
| | `DisplayMode` | `=If(CountRows(galPortfolioList.AllItems) = 0, DisplayMode.Disabled, DisplayMode.Edit)` |
| | `OnSelect` | see [The download](#the-download) |

## Column headers

Six labels at `Y = 218`, `Size = SizeMeta`, `Color = ClrTextMuted`, all-caps, above a
1px `recHeaderRule` (`Fill = ClrBorder`).

| Label | Text | X | Width |
|---|---|---|---|
| `lblHdrPursuit` | `="PURSUIT"` | 24 | 210 |
| `lblHdrStage` | `="STAGE"` | 244 | 200 |
| `lblHdrOwner` | `="OWNER"` | 454 | 190 |
| `lblHdrSIs` | `="ALIGNED SIS"` | 654 | 150 |
| `lblHdrHype` | `="HYPERSCALERS"` | 814 | 150 |
| `lblHdrNext` | `="NEXT TASK"` | 974 | 200 |

Those six fit a 1366-wide tablet layout. The mockup's horizontal scrollbar implies more
columns off-screen; galleries can't scroll horizontally, so that column set lives in the
export instead, which already carries account, health, target date, Salesforce, and fees.

## `galPortfolioList`

| Property | Formula |
|---|---|
| `Items` | `=Sort(colPortfolio, 'Pursuit Name', SortOrder.Ascending)` |
| `Layout` | Vertical |
| `TemplateSize` | `=110` |
| `X` / `Y` | `=GapPage` / `=248` |
| `Width` | `=Parent.Width - (GapPage * 2)` |
| `Height` | `=Parent.Height - Self.Y - 56` |
| `ShowScrollbar` | `=true` |

Sorting on `Pursuit Name` groups by account for free, because every name in your data is
prefixed with it — "ELEVANCE HEALTH: Carelon…" and "ELEVANCE HEALTH: Unified Data…" land
together.

### Row template

Each control's `X` and `Width` match its column header.

| Control | Property | Formula |
|---|---|---|
| `lblRowTitle` | `Text` | `=ThisItem.'Pursuit Name'` |
| | `Size` / `FontWeight` / `Color` / `Wrap` | `=SizeCardTitle` / `=FontWeight.Semibold` / `=ClrText` / `=true` |
| | `Height` | `=64` |
| | `OnSelect` | `=Set(gblPursuitKey, ThisItem.Title); Set(gblNewPursuit, false); Navigate(scrPursuitWorkspace, ScreenTransition.None)` |
| `lblRowSfLink` | `Text` | `=If(IsBlank(ThisItem.'Salesforce Opportunity URL'), "No Salesforce opportunity", "Salesforce opportunity linked")` |
| | `Size` / `Color` | `=SizeMeta` / `=ClrTextFaint` |
| `lblRowStage` | `Text` | `=ThisItem.'Workflow Stage'.Value` |
| | `Size` / `Color` / `Wrap` | `=SizeBody` / `=ClrTextMuted` / `=true` |
| `recRowAvatar` (Rectangle, all `Radius* = 12`) | `Fill` / `Width` / `Height` | `=ClrAvatar` / `=24` / `=24` |
| `lblRowInitials` | `Text` | `=Initials(ThisItem.OwnerName)` |
| | `Size` / `Color` / `Align` | `=SizeChip` / `=ClrAvatarText` / `=Align.Center` |
| `lblRowOwner` | `Text` | `=ThisItem.OwnerName` |
| | `Size` / `Color` | `=SizeBody` / `=ClrText` |
| `lblRowNextTask` | `Text` | `=Coalesce(ThisItem.NextAction.'Action Title', "—")` |
| | `Size` / `Color` / `Wrap` | `=SizeBody` / `=ClrText` / `=true` |
| `lblRowNextDue` | `Text` | `=If(IsBlank(ThisItem.NextAction), "", Text(ThisItem.NextAction.'Due Date', "mmmm d"))` |
| | `Size` / `Color` | `=SizeBody` / `=ClrDate` |
| `recRowDivider` | `Y` / `Height` / `Fill` | `=Parent.TemplateHeight - 1` / `=1` / `=ClrDivider` |

`lblRowSfLink` tests the URL rather than a sync-status column — there's no sync status
in the real schema, and eight of your fourteen pursuits have no Salesforce URL, so the
distinction is worth drawing.

### Chip galleries

`galRowSIs` (`Items = ThisItem.'Aligned SIs'`) and `galRowHype`
(`Items = ThisItem.Hyperscalers`), both `Layout` Vertical, `TemplateSize = 26`,
`Height = 78`, chip template as on the board.

Vertical rather than horizontal: the mockup stacks NiSource's two SIs rather than
running them across, and stacking degrades better at three partners.

## Footer

`lblFooterNote`, `Y = Parent.Height - 40`, `Size = SizeBody`, `Color = ClrTextMuted`:

```powerfx
="The download follows the visible list and is designed for offline review, reporting, and follow-up analysis."
```

---

## The download

The button hands the flow exactly what the gallery is showing —
`galPortfolioList.AllItems` reflects whatever filtering and sorting `Items` applies — so
the file matches the screen, as the footer promises.

Build `PursuitTracker-ExportPortfolio` first (`docs/06-flows.md`), then set
`btnDownloadExcel.OnSelect`:

```powerfx
Set(gblExporting, true);
Set(
    gblExport,
    PursuitTrackerExportPortfolio.Run(
        JSON(
            ShowColumns(
                AddColumns(
                    galPortfolioList.AllItems,
                    "PursuitId",     Title,
                    "PursuitName",   'Pursuit Name',
                    "Account",       'Account Name',
                    "StageName",     'Workflow Stage'.Value,
                    "HealthName",    Health.Value,
                    "Owner",         OwnerName,
                    "SIs",           SIsText,
                    "Hype",          HypeText,
                    "NextActionName", Coalesce(NextAction.'Action Title', ""),
                    "NextActionDue",  If(IsBlank(NextAction), "", Text(NextAction.'Due Date', "yyyy-mm-dd")),
                    "TargetDate",    Text('Target Decision Date', "yyyy-mm-dd"),
                    "SfUrl",         Coalesce('Salesforce Opportunity URL', ""),
                    "Fees",          Text('Estimated Fees', "[$-en-US]#,##0")
                ),
                "PursuitId", "PursuitName", "Account", "StageName", "HealthName", "Owner",
                "SIs", "Hype", "NextActionName", "NextActionDue", "TargetDate", "SfUrl", "Fees"
            ),
            JSONFormat.IgnoreUnsupportedTypes
        )
    )
);
Set(gblExporting, false);
If(
    IsBlank(gblExport.downloadurl),
    Notify("Export failed — the flow returned no link.", NotificationType.Error),
    Download(gblExport.downloadurl)
)
```

Four things worth knowing about that formula:

**`ShowColumns` after `AddColumns` is not redundant.** Without it `JSON()` serialises the
whole underlying record — the `NextAction` sub-record, the raw choice tables, and every
SharePoint system column. The payload balloons and "Create CSV table" in the flow emits
columns nobody asked for.

**`JSONFormat.IgnoreUnsupportedTypes` is required**, not decoration. Multi-choice columns
aren't JSON-serialisable and `JSON()` throws on them outright. Flattening to text first
(`SIsText`, `HypeText`) is what makes each record serialisable; the flag covers anything
left.

**Every added column is renamed, never reused.** `AddColumns` fails if a name already
exists on the record, so `"HealthName"` rather than `"Health"`, `"Account"` rather than
`"Account Name"`.

**Dates are pre-formatted as text.** `JSON()` emits ISO-8601 with a timezone, which Excel
reads as a string and left-aligns. `yyyy-mm-dd` opens as a date.

Add a loading state while the flow runs — a rectangle plus label with
`Visible = gblExporting`. The round trip is two to four seconds, and without feedback
people press the button twice and get two files.
