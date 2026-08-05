# Screen — `scrPortfolioList`

The same portfolio as a reportable table, plus the Excel download.

```
scrPortfolioList
├── [TopNav.pa.yaml]
├── lblPageTitle / lblPageSub
├── btnDownloadExcel
├── recHeaderRule + six column-header labels
├── galPortfolioList             ◄── one row per pursuit
│   ├── lblRowTitle / lblRowSfLink
│   ├── lblRowStage
│   ├── cirRowAvatar + lblRowInitials + lblRowOwner
│   ├── galRowSIs                ◄── SI chips
│   ├── galRowHype               ◄── hyperscaler chips
│   ├── lblRowNextTask + lblRowNextDue
│   └── recRowDivider
└── lblFooterNote
```

## Screen

| Property | Formula |
|---|---|
| `Fill` | `=ClrPage` |
| `OnVisible` | the same `LoadPortfolio` block used by the board (from `src/App.OnStart.powerfx`) |

## Header

| Control | Property | Formula |
|---|---|---|
| `lblPageTitle` | `Text` | `="SI pursuit management"` |
| `lblPageSub` | `Text` | `="A reportable view of the same portfolio shown on the board."` |
| `btnDownloadExcel` | `Text` | `="Download Excel"` |
| | `X` | `=Parent.Width - Self.Width - GapPage` |
| | `Fill` / `Color` / `HoverFill` | `=ClrAccent` / `=ClrAccentText` / `=ClrAccentHover` |
| | `DisplayMode` | `=If(CountRows(galPortfolioList.AllItems) = 0, DisplayMode.Disabled, DisplayMode.Edit)` |
| | `OnSelect` | see [Download](#the-download) |

## Column headers

Six labels at `Y = 218`, `Size = SizeMeta`, `Color = ClrTextMuted`, all-caps text, above
a 1px `recHeaderRule` (`Fill = ClrBorder`).

| Label | Text | X | Width |
|---|---|---|---|
| `lblHdrPursuit` | `="PURSUIT"` | 24 | 210 |
| `lblHdrStage` | `="STAGE"` | 244 | 200 |
| `lblHdrOwner` | `="OWNER"` | 454 | 190 |
| `lblHdrSIs` | `="ALIGNED SIS"` | 654 | 150 |
| `lblHdrHype` | `="HYPERSCALERS"` | 814 | 150 |
| `lblHdrNext` | `="NEXT TASK"` | 974 | 200 |

Those six columns fit a 1366-wide tablet layout with the gutter. The mockup shows a
horizontal scrollbar under the table, implying more columns off to the right — canvas
apps can't scroll a gallery horizontally, so that's the one piece of this screen that
doesn't reproduce. Options are in `docs/07-gaps-and-decisions.md`; the short version is
that the Excel download is the honest home for the wider column set, and it's already
built to carry more fields than the screen shows.

## `galPortfolioList`

| Property | Formula |
|---|---|
| `Items` | `=SortByColumns(colPortfolio, "Title", SortOrder.Ascending)` |
| `Layout` | Vertical |
| `TemplateSize` | `=110` |
| `X` / `Y` | `=GapPage` / `=248` |
| `Width` | `=Parent.Width - (GapPage * 2)` |
| `Height` | `=Parent.Height - Self.Y - 56` |
| `ShowScrollbar` | `=true` |

### Row template

Each control's `X` and `Width` match its column header above.

| Control | Property | Formula |
|---|---|---|
| `lblRowTitle` | `Text` | `=ThisItem.Title` |
| | `Size` / `FontWeight` / `Color` / `Wrap` | `=SizeCardTitle` / `=FontWeight.Semibold` / `=ClrText` / `=true` |
| | `Height` | `=64` |
| | `OnSelect` | `=Set(gblPursuitId, ThisItem.ID); Set(gblNewPursuit, false); Navigate(scrPursuitWorkspace, ScreenTransition.None)` |
| `lblRowSfLink` | `Text` | `=If(ThisItem.SalesforceSyncStatus.Value = "Not linked", "No Salesforce opportunity", "Salesforce opportunity linked")` |
| | `Size` / `Color` | `=SizeMeta` / `=ClrTextFaint` |
| `lblRowStage` | `Text` | `=ThisItem.Stage.Value` |
| | `Size` / `Color` / `Wrap` | `=SizeBody` / `=ClrTextMuted` / `=true` |
| `cirRowAvatar` (Circle) | `Fill` / `Width` / `Height` | `=ClrAvatar` / `=24` / `=24` |
| `lblRowInitials` | `Text` | `=Concat(FirstN(Split(ThisItem.PursuitOwner.DisplayName, " "), 2), Left(Value, 1))` |
| | `Size` / `Color` / `Align` | `=SizeChip` / `=ClrAvatarText` / `=Align.Center` |
| `lblRowOwner` | `Text` | `=ThisItem.PursuitOwner.DisplayName` |
| | `Size` / `Color` | `=SizeBody` / `=ClrText` |
| `lblRowNextTask` | `Text` | `=Coalesce(ThisItem.NextTask.Title, "—")` |
| | `Size` / `Color` / `Wrap` | `=SizeBody` / `=ClrText` / `=true` |
| `lblRowNextDue` | `Text` | `=If(IsBlank(ThisItem.NextTask), "", DueLabel(ThisItem.NextTask.DueDate, ThisItem.NextTask.DueDescription))` |
| | `Size` / `Color` | `=SizeBody` / `=ClrDate` |
| `recRowDivider` | `Y` / `Height` / `Fill` | `=Parent.TemplateHeight - 1` / `=1` / `=ClrDivider` |

### Chip galleries

`galRowSIs` (`Items = ThisItem.AlignedSIs`) and `galRowHype`
(`Items = ThisItem.Hyperscalers`), both `Layout` Vertical, `TemplateSize = 26`,
`Height = 78`.

Vertical, not horizontal — the mockup stacks NiSource's two SIs and Evergreen's two
hyperscalers rather than running them across, and vertical stacking degrades better
when a pursuit picks up a third partner.

Each contains `recChip` (`Fill = ClrChip`, all `Radius* = RadiusChip`, `Height = 22`)
and `lblChip` (`Text = ThisItem.Value`, `Size = SizeChip`, `Color = ClrChipText`,
`Align = Align.Center`).

## Footer

`lblFooterNote`, `Y = Parent.Height - 40`, `Size = SizeBody`, `Color = ClrTextMuted`:

```powerfx
="The download follows the visible list and is designed for offline review, reporting, and follow-up analysis."
```

---

## The download

The button hands the flow exactly what the gallery is showing —
`galPortfolioList.AllItems`, which reflects any filtering or sorting applied to `Items`
— so the file always matches the screen, as the footer promises.

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
                    "Pursuit",      Title,
                    "Account",      Account,
                    "StageName",    Stage.Value,
                    "Owner",        PursuitOwner.DisplayName,
                    "AlignedSIs",   SIsText,
                    "Hyperscalers", HypeText,
                    "NextTaskName", Coalesce(NextTask.Title, ""),
                    "NextTaskDue",  If(IsBlank(NextTask), "", DueLabel(NextTask.DueDate, NextTask.DueDescription)),
                    "TargetClose",  Text(TargetCloseDate, "yyyy-mm-dd"),
                    "Salesforce",   Coalesce(SalesforceOpportunityName, ""),
                    "SyncStatus",   SalesforceSyncStatus.Value
                ),
                "Pursuit", "Account", "StageName", "Owner", "AlignedSIs", "Hyperscalers",
                "NextTaskName", "NextTaskDue", "TargetClose", "Salesforce", "SyncStatus"
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

Three things worth knowing about that formula:

**`ShowColumns` after `AddColumns` is not redundant.** Without it, `JSON()` serialises
the entire underlying record — including the `NextTask` sub-record, the raw multi-choice
tables, and every SharePoint system column. The payload balloons, and "Create CSV table"
in the flow produces columns nobody asked for.

**`JSONFormat.IgnoreUnsupportedTypes` is required**, not optional. Person and
multi-choice columns aren't JSON-serialisable and `JSON()` throws on them outright.
Flattening them into text first (`SIsText`, `.DisplayName`) is what makes the record
serialisable; the flag covers anything left.

**Dates are pre-formatted as text.** `JSON()` emits ISO-8601 with a timezone, which
Excel reads as a string and left-aligns. Passing `yyyy-mm-dd` gives you something Excel
parses as a date on open.

Add a loading state while the flow runs: a rectangle plus label with
`Visible = gblExporting`. The round trip is two to four seconds, and without feedback
people press the button again and get two files.
