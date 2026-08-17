# Screen — `scrPortfolioBoard`

The kanban. One column per workflow stage, cards sorted by target decision date.

```
scrPortfolioBoard
├── nav bar                       navBg, navBrand, three tabs
├── lblPageTitle                     "SI pursuit management"
├── lblPageSub                       instruction line
├── btnNewPursuit                    "New pursuit"
└── galStages                    ◄── horizontal gallery, one item per stage
    ├── colBg + recStageAccent
    ├── lblStageName / lblStageCount
    ├── recDropTarget + lblDropHint   "Move here", only while a card is picked up
    └── galCards                 ◄── vertical gallery, the pursuits in this stage
        ├── recCard + recHealth
        ├── lblMoveHandle            pick up / put down
        ├── lblCardAccount           account, bold
        ├── lblCardTitle             pursuit name, smaller
        ├── lblSICap  + galCardSIs   ◄── "SI:"  + chips
        ├── lblHSCap  + galCardHype  ◄── "HS:"  + chips
        ├── recCardDivider
        └── lblNextCap + lblNextTask + lblNextTaskDue
```

Three nested galleries is the deepest canvas apps allow, and this uses all of it.

**If the paste is rejected**, it is almost always one of two controls. `galStages` is a
horizontal gallery with a nested vertical gallery (`galCards`) — insert both by hand from
the Insert pane and paste the property formulas in. `recCard` is a `Classic/Button` used as
a rounded panel — if the `Radius*` properties are rejected, drop them and accept square
corners. Every control and formula below works as a property table either way.

**Z-order**, since document order is z-order and the YAML no longer says so: `btnCardClick`
covers the whole card and so comes after the card's content; `lblMoveHandle` comes after
`btnCardClick` so the handle still gets its own clicks; `lblDropHint` sits on top of
`recDropTarget` and carries the same `OnSelect`, because without it the label swallows the
click and "Move Here" does nothing.

---

## Screen

| Property | Formula |
|---|---|
| `Fill` | `=ClrPage` |
| `OnVisible` | paste the `LoadPortfolio` block from `src/App.OnStart.powerfx` (everything below the banner comment), then `Set(gblMoving, LookUp('pursuit-tracker-pursuits', ID < 0))` |

Reloading on every visit is what makes a stage change from elsewhere in the app show up
when you come back.

## `colStages` is a literal table

Board columns come from a hard-coded six-row table in the `LoadPortfolio` block, not from
`Choices('pursuit-tracker-pursuits'.'Workflow Stage')`.

`Choices()` is the better design and the commented line is kept right above it: board order
would be a list setting rather than an app edit, and adding a stage wouldn't mean touching
three files. It isn't in use because the record `Choices()` returns doesn't type as text on
this column — `Text(C.Value)` raises *"Expected text or number"*, the collection resolves to
`Error`, and every read of `ThisItem.Stage` fails after it. What that looks like on screen is
a board with no columns, no cards, and no error message, which is worse than a stage list you
have to edit by hand.

The literal has to match the SharePoint choice set **exactly** — casing, spacing, the missing
space in `Proposal/Quote`. A stage in the table that isn't in the column renders an empty
column; a stage in the column that isn't in the table hides those pursuits entirely.

## Page header

| Control | Property | Formula |
|---|---|---|
| `lblPageTitle` | `Text` | `="SI pursuit management"` |
| | `X` / `Y` | `=GapPage` / `=64 + GapPage` |
| | `Size` / `FontWeight` / `Color` | `=SizePageTitle` / `=FontWeight.Semibold` / `=ClrText` |
| `lblPageSub` | `Text` | `=If(IsBlank(gblMoving), "Select the move handle on a pursuit, then choose its new stage.", "Moving " & gblMoving.'Pursuit Name' & " — choose a stage, or press the handle again to cancel.")` |
| | `Y` | `=lblPageTitle.Y + lblPageTitle.Height` |
| | `Size` / `Color` | `=SizeBody` / `=ClrTextMuted` |
| `btnNewPursuit` | `Text` | `="New pursuit"` |
| | `X` | `=Parent.Width - Self.Width - GapPage` |
| | `Fill` / `Color` / `HoverFill` | `=ClrAccent` / `=ClrAccentText` / `=ClrAccentHover` |
| | `OnSelect` | `=Set(gblPursuitKey, Blank()); Set(gblNewPursuit, true); Navigate(scrPursuitWorkspace, ScreenTransition.None)` |

The subtitle differs from the mockup's "Drag pursuits into the current workflow stage."
Canvas apps have no drag-and-drop, and the label would be a promise the app can't keep —
reasoning and alternatives in `docs/07-gaps-and-decisions.md`.

## `galStages` — the columns

| Property | Formula |
|---|---|
| `Items` | `=colStages` |
| `Layout` | Horizontal |
| `TemplateSize` | `=(Parent.Width - (GapPage * 2)) / BoardColumns` |
| `TemplatePadding` | `=8` |
| `ShowScrollbar` | `=true` |
| `X` / `Y` | `=GapPage` / `=170` |
| `Width` | `=Parent.Width - (GapPage * 2)` |
| `Height` | `=Parent.Height - Self.Y - GapPage` |

`colStages` is built in `App.OnStart` from
`Choices('pursuit-tracker-pursuits'.'Workflow Stage')`, so board columns and their order
are a SharePoint list setting, not an app edit. No sort here on purpose — the choice
order *is* the workflow order, and sorting alphabetically would put Preliminary Scoping
before Proposal/Quote.

`App.OnStart` also handles two edge cases the raw `Choices()` call doesn't: an empty
choice list (which renders a blank board with no error) and pursuits carrying a
typed-in stage that isn't in the list.

**Column width is the canvas divided by `BoardColumns` (5), not a fixed number.** All
five stages fit at any window size and the board never scrolls sideways; widen the browser
and the columns widen with it. A sixth stage added in SharePoint starts scrolling again —
raise `BoardColumns` in `src/App.Formulas.powerfx` to match.

That only works if nothing inside the column is fixed-width, so everything from the stage
header down to the chips sizes off `colBg.Width` or `recCard.Width`. The one number still
hard-coded is the card *height* (228), which doesn't depend on the column count.

### Inside the column template

| Control | Property | Formula |
|---|---|---|
| `colBg` (Rectangle) | `Width` / `Height` | `=Parent.TemplateWidth - 12` / `=Parent.Height - 8` |
| | `Fill` / `BorderColor` / `BorderThickness` | `=ClrColumn` / `=ClrBorder` / `=1` |
| | all four `Radius*` | `=RadiusCard` |
| `recStageAccent` (Rectangle) | `Height` / `Width` | `=3` / `=colBg.Width` |
| | `Fill` | `=StageAccent(ThisItem.Stage)` |
| `lblStageName` | `Text` | `=ThisItem.Stage` |
| | `Size` / `FontWeight` / `Color` | `=SizeBody` / `=FontWeight.Semibold` / `=ClrText` |
| `lblStageCount` | `Text` | `=CountRows(Filter(colPortfolio, 'Workflow Stage'.Value = ThisItem.Stage))` |
| | `Align` / `Color` | `=Align.Right` / `=ClrTextMuted` |

### The drop target

Visible only while a card is picked up, and never on the column it's already in.

| Control | Property | Formula |
|---|---|---|
| `recDropTarget` | `Visible` | `=Not(IsBlank(gblMoving)) && gblMoving.'Workflow Stage'.Value <> ThisItem.Stage` |
| | `Fill` | `=ColorFade(ClrAccent, 0.75)` |
| | `BorderColor` / `BorderStyle` / `BorderThickness` | `=ClrAccent` / `=BorderStyle.Dashed` / `=1` |
| | `Height` | `=44` |
| `lblDropHint` | `Text` / `Visible` | `="Move here"` / `=recDropTarget.Visible` |
| | `Color` / `Align` | `=ClrAccent` / `=Align.Center` |
| | `OnSelect` | **the same formula as `recDropTarget`** — see below |

`recDropTarget.OnSelect`:

```powerfx
Patch(
    'pursuit-tracker-pursuits',
    LookUp('pursuit-tracker-pursuits', Title = gblMoving.Title),
    { 'Workflow Stage': { Value: ThisItem.Stage } }
);
Set(gblMoving, Blank());
// Re-read rather than patching the local collection: the item may have changed
// underneath us, and a stale board is worse than a half-second pause.
ClearCollect(
    colPortfolio,
    AddColumns(
        'pursuit-tracker-pursuits' As P,
        OwnerName, Coalesce(LookUp(colPeople, Email = P.'WM Pursuit Owner Entra ID').Name, P.'WM Pursuit Owner Entra ID'),
        NextActionTitle, First(Sort(Filter(colActions, 'Pursuit ID' = P.Title, Status.Value <> "Completed", Not(IsBlank('Due Date'))), 'Due Date', SortOrder.Ascending)).'Action Title',
        NextActionDue,   First(Sort(Filter(colActions, 'Pursuit ID' = P.Title, Status.Value <> "Completed", Not(IsBlank('Due Date'))), 'Due Date', SortOrder.Ascending)).'Due Date',
        SIsText,  Concat(P.'Aligned SIs', Value, ", "),
        HypeText, Concat(P.Hyperscalers, Value, ", ")
    )
);
Notify("Moved to " & ThisItem.Stage, NotificationType.Success, 2000)
```

**`lblDropHint` carries the identical handler.** The label is drawn over the rectangle
and is declared after it, so it wins the click — canvas controls capture their own pointer
events whether or not they do anything with them. With the handler only on the rectangle,
"Move here" looks live and does nothing. Duplicating it is uglier than reordering but
keeps both jobs intact: the rectangle draws the dashed border, the label draws the text,
and either one accepts the click.

There's no `BoardOrder` column in the real schema, so a move sets the stage and nothing
else — order within a column comes from the target decision date. That's one fewer thing
to maintain and one fewer thing to get out of sync.

### `btnCardClick`

The same trap sat on the card itself. `recCard` has the open-workspace handler, but every
label on the card is declared after it and sits on top, so only the bare strips between
labels were clickable. A transparent `Classic/Button` now covers the card and carries the
handler:

| Property | Formula |
|---|---|
| `Text` / `Fill` | `=""` / `=Color.Transparent` |
| `Width` / `Height` | `=282` / `=206` |
| `HoverFill` / `PressedFill` | `=RGBA(255, 255, 255, 0.03)` / `=RGBA(255, 255, 255, 0.06)` |
| `OnSelect` | `=Set(gblPursuitKey, ThisItem.Title); Set(gblNewPursuit, false); Navigate(scrPursuitWorkspace, ScreenTransition.None)` |

`lblMoveHandle` moved to the **end** of the card template so it stays above the click
layer — otherwise picking a card up would open it instead.

This is the third time this pattern has come up: any control that needs to be clickable
has to be declared *after* everything it overlaps. Document order is z-order.

## `galCards` — the cards

| Property | Formula |
|---|---|
| `Items` | `=Sort(Filter(colPortfolio, 'Workflow Stage'.Value = ThisItem.Stage), If(IsBlank('Target Decision Date'), Date(2099, 12, 31), 'Target Decision Date'), SortOrder.Ascending)` |
| `Layout` | Vertical |
| `TemplateSize` | `=240` |
| `TemplatePadding` | `=6` |
| `Width` | `=colBg.Width - 20` |
| `Height` | `=colBg.Height - 60` |
| `ShowScrollbar` | `=true` |

Three of your fourteen pursuits have no target decision date. Sorting on the raw column
would float those to the top of their column, because blank sorts before every real
date — the substitution pushes them to the bottom instead, which is where an undated
pursuit belongs.

`Sort` rather than `SortByColumns` throughout: `SortByColumns` takes column names as
strings, and these columns have spaces in their display names and meaningless
`field_n` internal names. `Sort` takes an expression and resolves the same way the rest
of the app does.

### Inside the card template

Card is 228 tall in a 240 template. Every horizontal measurement is relative to
`recCard.Width`, which is relative to the column, which is the canvas divided by five —
so a card at 1366 and a card at 2560 are the same layout at different scales.

The title gets three lines rather than two: narrower columns mean the same text wraps
further, and the `Clip` budgets came down with the width (88 characters for the title, 52
for the next action).

`Wrap` is explicitly `false` on the account line, both partner captions and the chip
labels. Labels wrap by default, which is why "HS:" was rendering as "HS" with a stray ":"
underneath it and "Internal/West Monroe" was breaking mid-word inside its chip.

| Control | Property | Formula |
|---|---|---|
| `recCard` (Classic/Button) | `Text` | `=""` |
| | `Fill` / `HoverFill` / `PressedFill` | `=ClrCard` / `=ClrCardHover` / `=ClrCardHover` |
| | `Height` | `=206` |
| | `BorderColor` | `=If(gblMoving.Title = ThisItem.Title, ClrAccent, ClrBorder)` |
| | `BorderThickness` | `=If(gblMoving.Title = ThisItem.Title, 2, 1)` |
| | `OnSelect` | `=Set(gblPursuitKey, ThisItem.Title); Set(gblNewPursuit, false); Navigate(scrPursuitWorkspace, ScreenTransition.None)` |
| `recHealth` (Rectangle) | `Fill` | `=If(ThisItem.Health.Value = "At risk", ClrRiskFill, Color.Transparent)` |
| `lblMoveHandle` | `Text` / `Color` | `="⋮⋮"` / `=If(gblMoving.Title = ThisItem.Title, ClrAccent, ClrTextFaint)` |
| | `OnSelect` | `=Set(gblMoving, If(gblMoving.Title = ThisItem.Title, Blank(), ThisItem))` |
| `lblCardAccount` | `Text` | `=Clip(ThisItem.'Account Name', 26)` |
| | `Size` / `FontWeight` / `Color` | `=SizeCardTitle` / `=FontWeight.Semibold` / `=ClrText` |
| `lblCardTitle` | `Text` | see below |
| | `Size` / `Color` / `Wrap` | `=SizeBody` / `=ClrText` / `=true` |
| `lblSICap` / `lblHSCap` | `Text` | `="SI:"` / `="HS:"` |
| | `Size` / `Color` | `=SizeMeta` / `=ClrTextMuted` |
| `lblNextCap` | `Text` | `="NEXT ACTION"` — `Size = SizeMeta`, `Color = ClrTextMuted` |
| `lblNextTask` | `Text` | `=If(IsBlank(ThisItem.NextActionTitle), "No open actions", Clip(ThisItem.NextActionTitle, 68))` |
| | `Color` | `=If(IsBlank(ThisItem.NextActionTitle), ClrTextFaint, ClrText)` |
| `lblNextTaskDue` | `Text` | `=If(IsBlank(ThisItem.NextActionDue), "", Text(ThisItem.NextActionDue, "mmmm d"))` |
| | `Color` | `=ClrDate` |

The owner is gone from the card. Every pursuit in the data has the same owner, so the
avatar and name were 24 pixels of vertical space spent restating a constant. It's still
on the workspace.

### The two title lines

`lblCardAccount` shows `Account Name` unchanged — that column is already properly cased
(Frazier, Elevance Health, CD&R).

`lblCardTitle` shows the pursuit name with its account prefix stripped:

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

Every pursuit name in the data repeats its account as an ALL-CAPS prefix —
"FRAZIER: MatixCare AWS Platform Buld". With the account on its own line that prefix is
both redundant and the only shouty text on the card, so it comes off. What's left is
already mixed case.

Stripping the prefix is deliberately not the same as title-casing. `Proper()` would fix
"FRAZIER" but wreck "AWS" → "Aws", "SAP" → "Sap", "CD&R" → "Cd&R", and "MatixCare" →
"Matixcare". Removing the one part that's reliably wrong beats reformatting the parts
that are already right.

Two separators are in use — `ACCOUNT: name` on twelve rows and `ACCOUNT - name` on
NiSource — so both are handled, colon first. `Find(": ")` returns the *first* match,
which is what you want for "ELEVANCE HEALTH: Carelon - Unified Data…": it keeps the inner
hyphen intact.

### `galCardSIs` and `galCardHype` — the chips

| Property | `galCardSIs` | `galCardHype` |
|---|---|---|
| `Items` | `=ThisItem.'Aligned SIs'` | `=ThisItem.Hyperscalers` |
| `X` / `Y` | `=44` / `=70` | `=44` / `=98` |
| `Layout` | Horizontal | Horizontal |
| `TemplateSize` | `=76` | `=76` |
| `Width` / `Height` | `=224` / `=24` | `=224` / `=24` |

Each sits to the right of its caption, so a pursuit with no partners shows a bare
"SI:" rather than a hole in the layout — which reads as missing data instead of a
rendering bug. Nine of your fourteen have no SI, and eleven have no hyperscaler.

Inside: `recChip` (Rectangle, `Fill = ClrChip`, all `Radius* = RadiusChip`) and `lblChip`
(`Text = ThisItem.Value`, `Size = SizeChip`, `Color = ClrChipText`,
`Align = Align.Center`).

`Items` is evaluated in the *card's* scope, so `ThisItem` there is the pursuit; inside
this gallery's own template `ThisItem` is the individual choice value. That scope shift
is the most common reason a chip row renders empty.

Fixed `TemplateSize` clips long names — "Internal/West Monroe" and "NTT Data" both
appear in your data and only one fits. Variable-width chips need the label's rendered
text width, which canvas doesn't expose, so the practical fix is shorter choice values.

## Why the next action is two scalar columns, not one record

`colPortfolio` carries `NextActionTitle` and `NextActionDue` rather than a single
`NextAction` record column. The record version type-checks in `AddColumns` but doesn't
survive `ClearCollect` into a collection with its type intact, and the failure is
downstream and cryptic — `Text(ThisItem.NextAction.'Due Date', "mmmm d")` reports
*"incorrect format specifier for 'Text'"*, because the untyped field arrives as text and
`Text()` won't take a format string for text input. `Coalesce` on the title fails the same
way.

The cost is running the same `First(Sort(Filter(...)))` twice per row. At fourteen
pursuits against an in-memory collection that's free.

Separately: **`IsBlank()` doesn't accept a record.** `IsBlank(ThisItem.NextAction)` reports
*"function 'If' has invalid arguments"* from the `If` that wraps it, which points at the
wrong function. Testing `IsBlank(ThisItem.NextActionTitle)` — a scalar — is both correct
and what the label actually cares about.

## Why every wrapping label is clipped and top-aligned

Power Apps labels have no text-overflow setting. A label whose text needs more lines than
its `Height` allows does not clip — it keeps rendering — and because the default
`VerticalAlign` is **Middle**, the overflow spills out of *both* ends and lands on top of
whatever sits above and below. On the card that read as the pursuit name printing through
the account line and down into the SI row.

Two changes, both needed:

**`VerticalAlign: =VerticalAlign.Top`** on every wrapping label. Stops the upward spill
and makes the first line land where the layout expects it.

**`Clip(text, n)`** — a helper in `src/App.Formulas.powerfx` that trims to `n` characters
and appends an ellipsis. Stops the downward spill. The budgets are sized to the box: 72
characters for the card title (254px wide at `SizeBody`, about two lines), 26 for the
account, 68 for the next action.

The budgets are character counts, not measured text, so a name in all wide characters
will still run a line long. Power Apps exposes no way to measure rendered text, so the
alternative is `AutoHeight` plus a variable-height template, which a fixed-position card
layout can't use. If a title clips too eagerly, raise the number.

## Filters

Three dropdowns above the board and above the list: **SI**, **HS**, **Active**, plus a
Clear button. Each defaults to `All`.

They filter `colPortfolio` in memory, so there is no second query, nothing to reload, and
no delegation limit in play — the collection is already whole.

```powerfx
Filter(
    colPortfolio,
    'Workflow Stage'.Value = ThisItem.Stage,
    drpFltSI.Selected.Value = "All" || drpFltSI.Selected.Value in SIsText,
    drpFltHype.Selected.Value = "All" || drpFltHype.Selected.Value in HypeText,
    drpFltActive.Selected.Value = "All" || drpFltActive.Selected.Value = ActiveText
)
```

The same three lines appear in `galCards.Items` and `lblStageCount.Text` on the board, and
in `galPortfolioList.Items` on the list — so a stage header's count always matches the
cards under it.

**No globals and no OnChange handlers.** The galleries read `drpFltSI.Selected.Value`
directly, so selecting a value recalculates them the way a spreadsheet cell recalculates.
A global would need three OnChange handlers per screen kept in step with each other.

**SI and HS test `in` against the flattened text columns**, not the multi-choice tables.
`"Fujitsu" in SIsText` is a substring test over `"Fujitsu, NTT Data"`, which is both
simpler and avoids reaching into a choice table inside a predicate — the thing that has
broken repeatedly on this app. `ActiveText` was added to `colPortfolio` for the same
reason, including in the two inline rebuilds that run after a card is moved; without it
there, the filters would break the moment someone moved a card.

The SI and HS option lists come from `colLookups`, so **a value that isn't in the lookup
list can't be filtered on** even if it's in the SharePoint column. `Active` uses its own
three values, which are fixed in the column.

### Why not SharePoint views

A view would mean a round trip per filter change, a separate data source per combination,
and no way to combine three of them. In-memory filtering over a collection that's already
loaded is faster and composes.
