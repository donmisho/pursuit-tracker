# Screen — `scrPortfolioList`

The same portfolio as a reportable table, plus the Excel download.

```
scrPortfolioList
├── nav bar
├── lblPageTitle / lblPageSub
├── btnDownloadExcel
├── recHeaderRule + seven column-header labels
├── galPortfolioList             ◄── one row per pursuit
│   ├── recRowDivider
│   ├── lblRowAccount
│   ├── lblRowTitle / lblRowSfLink
│   ├── lblRowStage
│   ├── lblRowOwner
│   ├── galRowSIs / galRowHype   ◄── chips
│   ├── lblRowNextTask + lblRowNextDue
│   ├── btnRowClick              ◄── transparent, on top: whole row navigates
│   └── btnRowMenu + recRowMenu + btnMenuWorkspace + btnMenuSalesforce
└── lblFooterNote
```

**Z-order**: `btnRowClick` is declared after the row content it covers and before the `⋯`
menu, so the whole row is clickable but the menu still receives its own clicks.

There is no owner avatar. The initials circle (`recRowAvatar` + `lblRowInitials`) was
removed — a 24px disc repeating down a reporting table is decoration, and the name is
already spelled out beside it.

## Screen

| Property | Formula |
|---|---|
| `Fill` | `=ClrPage` |
| `OnVisible` | the same `LoadPortfolio` block the board uses (from `src/App.OnStart.powerfx`), then `Set(gblRowMenu, "")` |

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

Seven labels at `Y = 218`, `Size = SizeMeta`, `Color = ClrTextMuted`, all-caps, above a
1px `recHeaderRule` (`Fill = ClrBorder`).

| Label | Text | X | Width |
|---|---|---|---|
| `lblHdrAccount` | `="ACCOUNT"` | 24 | 150 |
| `lblHdrPursuit` | `="PURSUIT"` | 184 | 230 |
| `lblHdrStage` | `="STAGE"` | 458 | 170 |
| `lblHdrOwner` | `="OWNER"` | 638 | 180 |
| `lblHdrSIs` | `="SI"` | 828 | 130 |
| `lblHdrHype` | `="HS"` | 968 | 130 |
| `lblHdrNext` | `="NEXT ACTION"` | 1108 | 210 |

The `⋯` column between Pursuit and Stage has no header — a header over a control that's
the same on every row is noise.

Partner headers shortened to `SI` and `HS` to match the board card captions, which buys
back the width the account column needs.

## `galPortfolioList`

| Property | Formula |
|---|---|
| `Items` | `=Sort(colPortfolio, 'Account Name' & " " & 'Pursuit Name', SortOrder.Ascending)` |
| `Layout` | Vertical |
| `TemplateSize` | `=110` |
| `X` / `Y` | `=GapPage` / `=250` |
| `Width` | `=Parent.Width - (GapPage * 2)` |
| `Height` | `=Parent.Height - 250 - 56` |
| `ShowScrollbar` | `=true` |

Sorting on account-then-name rather than name alone. Sorting on the pursuit name used to
group an account's pursuits for free, because the name carried the account as a prefix.
Now that the prefix is stripped for display the sort has to say so explicitly — otherwise
Elevance's "Carelon…" and "Unified Data…" end up filed under C and U.

### Row template

`X` and `Width` on each control match its column header, minus the gallery's own `X`.

| Control | Property | Formula |
|---|---|---|
| `lblRowAccount` | `Text` | `=Clip(ThisItem.'Account Name', 40)` |
| | `X` / `Width` / `Height` | `=0` / `=150` / `=46` |
| | `Size` / `FontWeight` / `Color` / `Wrap` | `=SizeBody` / `=FontWeight.Semibold` / `=ClrText` / `=true` |
| `lblRowTitle` | `Text` | the prefix-stripping formula (below) |
| | `X` / `Width` / `Height` | `=160` / `=230` / `=54` |
| | `Size` / `Color` / `Wrap` | `=SizeBody` / `=ClrText` / `=true` |
| `lblRowSfLink` | `Text` | `=If(IsBlank(ThisItem.'Salesforce Opportunity URL'), "No Salesforce opportunity", "Salesforce opportunity linked")` |
| | `Size` / `Color` | `=SizeMeta` / `=ClrTextFaint` |
| `lblRowStage` | `Text` | `=Clip(ThisItem.'Workflow Stage'.Value, 52)` |
| | `X` / `Width` | `=434` / `=170` |
| `lblRowOwner` | | `X` `=646`. No initials circle — a 24px disc repeating down a reporting table is decoration, and the name is spelled out next to it |
| `galRowSIs` / `galRowHype` | `X` | `=804` / `=944` |
| | `Width` / `Height` / `TemplateSize` | `=130` / `=84` / `=28` |
| `lblRowNextTask` | `Text` | `=If(IsBlank(ThisItem.NextActionTitle), "No open actions", Clip(ThisItem.NextActionTitle, 58))` |
| | `Color` | `=If(IsBlank(ThisItem.NextActionTitle), ClrTextFaint, ClrText)` |
| `lblRowNextDue` | `Text` | `=If(IsBlank(ThisItem.NextActionDue), "", Text(ThisItem.NextActionDue, "mmmm d"))` |
| `recRowDivider` | `Y` / `Width` | `=Parent.TemplateHeight - 1` / `=Parent.Width - 20` |

Pursuit text drops from `SizeCardTitle` to `SizeBody` — the same size as Stage. The
account carries the emphasis now, so two competing bold columns would just fight.

`lblRowTitle.Text`:

```powerfx
With(
    { n: ThisItem.'Pursuit Name' },
    Trim(
        If(
            !IsBlank(Find(": ", n)),  Mid(n, Find(": ", n) + 2),
            !IsBlank(Find(" - ", n)), Mid(n, Find(" - ", n) + 3),
            n
        )
    )
)
```

Wrapped in `Clip(..., 96)` and top-aligned, like every wrapping label in the app — see
the note at the end of `docs/03-screen-portfolio-board.md` for why that's necessary.

Same treatment as the board card, and for the same reason: with the account in its own
column the ALL-CAPS prefix is redundant, and `Proper()` would wreck AWS, SAP, CD&R and
MatixCare on the way to fixing it. Chip galleries are 124 wide now rather than 92, so
"Internal/West Monroe" and "Databricks" stop clipping.

## Whole-row click

`btnRowClick` is a transparent `Classic/Button` covering the row:

| Property | Formula |
|---|---|
| `Text` | `=""` |
| `X` / `Y` | `=0` / `=0` |
| `Width` / `Height` | `=Parent.Width - 20` / `=Parent.TemplateHeight - 1` |
| `Fill` | `=Color.Transparent` |
| `HoverFill` / `PressedFill` | `=RGBA(255, 255, 255, 0.04)` / `=RGBA(255, 255, 255, 0.07)` |
| `BorderThickness` | `=0` |
| `OnSelect` | `=Set(gblRowMenu, ""); Set(gblPursuitKey, ThisItem.Title); Set(gblNewPursuit, false); Navigate(scrPursuitWorkspace, ScreenTransition.None)` |

**It sits on top of the row content, not behind it.** That's the part worth understanding:
canvas controls capture their own pointer events, so a click target underneath the labels
would only fire in the gaps between them — and the gaps are exactly where nobody clicks.
Transparent fill means it paints nothing; the hover fill is a 4%-white wash that reads as
a row highlight.

Z-order in the source file is document order, so anything that must stay clickable has to
appear *after* `btnRowClick`. That's the `⋯` button and its menu, and nothing else.

`lblRowTitle` no longer carries its own `OnSelect` — the click layer covers it.

## The `⋯` menu

A per-row popover rather than a real context menu, which canvas doesn't have. `gblRowMenu`
holds the `PUR-nnn` of the open row, so at most one menu is open at a time and every other
row's controls stay hidden.

| Control | Property | Formula |
|---|---|---|
| `btnRowMenu` | `Text` / `X` / `Y` | `="⋯"` / `=396` / `=12` |
| | `Fill` / `Color` | `=Color.Transparent` / `=ClrTextMuted` |
| | `OnSelect` | `=Set(gblRowMenu, If(gblRowMenu = ThisItem.Title, "", ThisItem.Title))` |
| `recRowMenu` | `Visible` | `=gblRowMenu = ThisItem.Title` |
| | `X` / `Y` / `Width` / `Height` | `=396` / `=40` / `=230` / `=70` |
| | `Fill` / `BorderColor` | `=ClrColumn` / `=ClrBorder` |
| `btnMenuWorkspace` | `Text` | `="Open pursuit workspace"` |
| | `Visible` | `=gblRowMenu = ThisItem.Title` |
| | `OnSelect` | `=Set(gblRowMenu, ""); Set(gblPursuitKey, ThisItem.Title); Set(gblNewPursuit, false); Navigate(scrPursuitWorkspace, ScreenTransition.None)` |
| `btnMenuSalesforce` | `Text` | `=If(IsBlank(ThisItem.'Salesforce Opportunity URL'), "No Salesforce opportunity", "Open Salesforce opportunity")` |
| | `Visible` | `=gblRowMenu = ThisItem.Title` |
| | `DisplayMode` | `=If(IsBlank(ThisItem.'Salesforce Opportunity URL'), DisplayMode.Disabled, DisplayMode.Edit)` |
| | `OnSelect` | `=Set(gblRowMenu, ""); Launch(ThisItem.'Salesforce Opportunity URL')` |

The Salesforce entry is disabled rather than hidden when a pursuit has no URL, and says so
— eight of your fourteen have none, and a menu that changes height depending on the row is
harder to use than one that greys an option out.

Two behaviours worth knowing. The menu opens *downward inside the row*, so it's 110px of
vertical space at most; at 70px it fits. And it closes on any row click, because
`btnRowClick.OnSelect` clears `gblRowMenu` before it navigates — there's no click-away
handler on the screen itself, so a menu left open while you scroll stays open until you
click something.

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
                    PursuitId,     Title,
                    PursuitName,   'Pursuit Name',
                    Account,       'Account Name',
                    StageName,     'Workflow Stage'.Value,
                    HealthName,    Health.Value,
                    Owner,         OwnerName,
                    SIs,           SIsText,
                    Hype,          HypeText,
                    NextName,      Coalesce(NextActionTitle, ""),
                    NextDue,       If(IsBlank(NextActionDue), "", Text(NextActionDue, "yyyy-mm-dd")),
                    TargetDate,    Text('Target Decision Date', "yyyy-mm-dd"),
                    SfUrl,         Coalesce('Salesforce Opportunity URL', ""),
                    Fees,          Text('Estimated Fees', "[$-en-US]#,##0")
                ),
                PursuitId, PursuitName, Account, StageName, HealthName, Owner,
                SIs, Hype, NextName, NextDue, TargetDate, SfUrl, Fees
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
whole underlying record — the raw choice tables and every SharePoint system column. The payload balloons and "Create CSV table" in the flow emits
columns nobody asked for.

**`JSONFormat.IgnoreUnsupportedTypes` is required**, not decoration. Multi-choice columns
aren't JSON-serialisable and `JSON()` throws on them outright. Flattening to text first
(`SIsText`, `HypeText`) is what makes each record serialisable; the flag covers anything
left.

**Every added column is renamed, never reused.** `AddColumns` fails if a name already
exists on the record, so `HealthName` rather than `Health`, `Account` rather than
`'Account Name'`.

**Column names are identifiers, not strings.** Current Power Fx wants
`AddColumns(t, OwnerName, ...)`; older Studio versions want `AddColumns(t, "OwnerName", ...)`
and reject the identifier form. If you hit "The function 'AddColumns' has some invalid
arguments", put the quotes back — here, in `App.OnStart`, in the board's
`recDropTarget.OnSelect`, and in the workspace's `colActions_P` build.

**Dates are pre-formatted as text.** `JSON()` emits ISO-8601 with a timezone, which Excel
reads as a string and left-aligns. `yyyy-mm-dd` opens as a date.

Add a loading state while the flow runs — a rectangle plus label with
`Visible = gblExporting`. The round trip is two to four seconds, and without feedback
people press the button twice and get two files.
