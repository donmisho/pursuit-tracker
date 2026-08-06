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

---

## Screen

| Property | Formula |
|---|---|
| `Fill` | `=ClrPage` |
| `OnVisible` | paste the `LoadPortfolio` block from `src/App.OnStart.powerfx` (everything below the banner comment), then `Set(gblMoving, LookUp('pursuit-tracker-pursuits', ID < 0))` |

Reloading on every visit is what makes a stage change from elsewhere in the app show up
when you come back.

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
| `TemplateSize` | `=BoardColWidth` |
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

Your five stages plus the horizontal scroll means about three and a half columns visible
at 1366 wide. That's expected; the gallery scrolls.

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
| `TemplateSize` | `=218` |
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

Card is 206 tall in a 218 template — up from 170/178, to fit two partner rows and a
labelled next action.

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
