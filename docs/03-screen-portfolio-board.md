# Screen — `scrPortfolioBoard`

The kanban. One column per `Stage` choice, cards sorted within each column.

```
scrPortfolioBoard
├── [TopNav.pa.yaml]                 nav bar, pasted
├── lblPageTitle                     "SI pursuit management"
├── lblPageSub                       instruction line
├── btnNewPursuit                    "New pursuit"
└── galStages                    ◄── horizontal gallery, one item per stage
    ├── colBg                        column background
    ├── lblStageName
    ├── lblStageCount
    ├── recDropTarget  + lblDropHint  "Move here", only while a card is picked up
    └── galCards                 ◄── vertical gallery, the pursuits in this stage
        ├── recCard                  card background
        ├── icoMove                  pick up / put down
        ├── lblCardTitle
        ├── cirAvatar + lblInitials
        ├── lblOwner
        ├── galCardSIs           ◄── horizontal gallery of SI chips
        ├── recCardDivider
        ├── lblNextTask
        └── lblNextTaskDue
```

Three nested galleries is the deepest canvas apps allow, and this uses all of it.

---

## Screen

| Property | Formula |
|---|---|
| `Fill` | `=ClrPage` |
| `OnVisible` | paste the `LoadPortfolio` block from `src/App.OnStart.powerfx` (everything below the `LoadPortfolio` banner comment), then `Set(gblMoving, Blank())` |

Re-running the load on every visit is what makes a stage change from the workspace
screen show up when you come back to the board.

## Page header

| Control | Property | Formula |
|---|---|---|
| `lblPageTitle` | `Text` | `="SI pursuit management"` |
| | `X` / `Y` | `=GapPage` / `=64 + GapPage` |
| | `Size` / `FontWeight` / `Color` | `=SizePageTitle` / `=FontWeight.Semibold` / `=ClrText` |
| `lblPageSub` | `Text` | `=If(IsBlank(gblMoving), "Select the move handle on a pursuit, then choose its new stage.", "Moving " & gblMoving.Title & " — choose a stage, or press the handle again to cancel.")` |
| | `Y` | `=lblPageTitle.Y + lblPageTitle.Height` |
| | `Size` / `Color` | `=SizeBody` / `=ClrTextMuted` |
| `btnNewPursuit` | `Text` | `="New pursuit"` |
| | `X` | `=Parent.Width - Self.Width - GapPage` |
| | `Fill` / `Color` / `HoverFill` | `=ClrAccent` / `=ClrAccentText` / `=ClrAccentHover` |
| | `OnSelect` | `=Set(gblPursuitId, Blank()); Set(gblNewPursuit, true); Navigate(scrPursuitWorkspace, ScreenTransition.None)` |

The subtitle differs from the mockup, which reads "Drag pursuits into the current
workflow stage." Canvas apps have no drag-and-drop and the label would be a promise the
app can't keep — the reasoning and the alternatives are in
`docs/07-gaps-and-decisions.md`.

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

`colStages` comes from `Choices('pursuit-tracker-Pursuits'.Stage)`, so the board's
columns are whatever the SharePoint choice column says they are — in the order
SharePoint stores them.

### Inside the column template

| Control | Property | Formula |
|---|---|---|
| `colBg` (Rectangle) | `Width` / `Height` | `=Parent.TemplateWidth - 12` / `=Parent.Height - 8` |
| | `Fill` / `BorderColor` / `BorderThickness` | `=ClrColumn` / `=ClrBorder` / `=1` |
| | all four `Radius*` | `=RadiusCard` |
| `recStageAccent` (Rectangle) | `Height` / `Width` | `=3` / `=colBg.Width` |
| | `Fill` | `=StageAccent(ThisItem.Value)` |
| `lblStageName` | `Text` | `=ThisItem.Value` |
| | `Size` / `FontWeight` / `Color` | `=SizeBody` / `=FontWeight.Semibold` / `=ClrText` |
| `lblStageCount` | `Text` | `=CountRows(Filter(colPortfolio, Stage.Value = ThisItem.Value))` |
| | `Align` / `Color` | `=Align.Right` / `=ClrTextMuted` |

### The drop target

Only visible while a card is picked up, and never on the column the card is already in.

| Control | Property | Formula |
|---|---|---|
| `recDropTarget` (Rectangle) | `Visible` | `=Not(IsBlank(gblMoving)) && gblMoving.Stage.Value <> ThisItem.Value` |
| | `Fill` | `=ColorFade(ClrAccent, 0.75)` |
| | `BorderColor` / `BorderStyle` / `BorderThickness` | `=ClrAccent` / `=BorderStyle.Dashed` / `=1` |
| | `Height` | `=44` |
| | `OnSelect` | see below |
| `lblDropHint` | `Text` | `="Move here"` |
| | `Visible` | `=recDropTarget.Visible` |
| | `Color` / `Align` | `=ClrAccent` / `=Align.Center` |

`recDropTarget.OnSelect`:

```powerfx
Patch(
    'pursuit-tracker-Pursuits',
    LookUp('pursuit-tracker-Pursuits', ID = gblMoving.ID),
    {
        Stage: { Value: ThisItem.Value },
        BoardOrder: Coalesce(
            Max(Filter(colPortfolio, Stage.Value = ThisItem.Value), BoardOrder),
            0
        ) + 10
    }
);
Set(gblMoving, Blank());
// Re-read rather than patching the local collection: the SharePoint item may have
// changed underneath us, and a stale board is worse than a half-second pause.
ClearCollect(
    colPortfolio,
    AddColumns(
        Filter('pursuit-tracker-Pursuits', IsActive = true, Portfolio.Value = gblPortfolio) As P,
        "NextTask",
        First(Sort(Filter(colOpenTasks, PursuitKey = P.ID, Not(IsBlank(DueDate))), DueDate, SortOrder.Ascending)),
        "SIsText",  Concat(P.AlignedSIs, Value, ", "),
        "HypeText", Concat(P.Hyperscalers, Value, ", ")
    )
);
Notify("Moved to " & ThisItem.Value, NotificationType.Success, 2000)
```

New cards land at the bottom of the target column: `Max(...) + 10`, with gaps of ten so
you can hand-insert between two cards later without renumbering the column.

## `galCards` — the cards

| Property | Formula |
|---|---|
| `Items` | `=SortByColumns(Filter(colPortfolio, Stage.Value = ThisItem.Value), "BoardOrder", SortOrder.Ascending, "Title", SortOrder.Ascending)` |
| `Layout` | Vertical |
| `TemplateSize` | `=178` |
| `TemplatePadding` | `=6` |
| `Width` | `=colBg.Width - 20` |
| `Height` | `=colBg.Height - 60` |
| `ShowScrollbar` | `=true` |

`Title` is the tie-breaker so two cards with the same `BoardOrder` — which will happen
the first time you load real data, since the column starts empty — hold a stable order
instead of shuffling on every refresh.

### Inside the card template

| Control | Property | Formula |
|---|---|---|
| `recCard` | `Fill` | `=ClrCard` |
| | `BorderColor` | `=If(gblMoving.ID = ThisItem.ID, ClrAccent, ClrBorder)` |
| | `BorderThickness` | `=If(gblMoving.ID = ThisItem.ID, 2, 1)` |
| | all four `Radius*` | `=RadiusCard` |
| | `OnSelect` | `=Set(gblPursuitId, ThisItem.ID); Set(gblNewPursuit, false); Navigate(scrPursuitWorkspace, ScreenTransition.None)` |
| `icoMove` (Icon, `Reorder`) | `Color` | `=If(gblMoving.ID = ThisItem.ID, ClrAccent, ClrTextFaint)` |
| | `X` | `=recCard.Width - Self.Width - 10` |
| | `Tooltip` | `="Move to another stage"` |
| | `OnSelect` | `=Set(gblMoving, If(gblMoving.ID = ThisItem.ID, Blank(), ThisItem))` |
| `lblCardTitle` | `Text` | `=ThisItem.Title` |
| | `Size` / `FontWeight` / `Color` | `=SizeCardTitle` / `=FontWeight.Semibold` / `=ClrText` |
| | `Wrap` / `Height` | `=true` / `=44` |
| `cirAvatar` (Circle) | `Fill` / `Width` / `Height` | `=ClrAvatar` / `=24` / `=24` |
| `lblInitials` | `Text` | `=Concat(FirstN(Split(ThisItem.PursuitOwner.DisplayName, " "), 2), Left(Value, 1))` |
| | `Size` / `Color` / `Align` | `=SizeChip` / `=ClrAvatarText` / `=Align.Center` |
| `lblOwner` | `Text` | `=ThisItem.PursuitOwner.DisplayName` |
| | `Size` / `Color` | `=SizeBody` / `=ClrTextMuted` |
| `recCardDivider` | `Height` / `Fill` | `=1` / `=ClrDivider` |
| `lblNextTask` | `Text` | `="Next task due: " & Coalesce(ThisItem.NextTask.Title, "—")` |
| | `Size` / `Color` / `Wrap` | `=SizeBody` / `=ClrText` / `=true` |
| `lblNextTaskDue` | `Text` | `=If(IsBlank(ThisItem.NextTask), "No open tasks", DueLabel(ThisItem.NextTask.DueDate, ThisItem.NextTask.DueDescription))` |
| | `Size` / `Color` | `=SizeBody` / `=ClrDate` |

`icoMove` sits on top of `recCard`, so its `OnSelect` wins and picking up a card doesn't
also navigate away from the board.

`lblInitials` splits the display name and takes the first letter of the first two words
— "Don Mishory" → "DM". Names with a middle name or a suffix still give two letters,
which is what you want; single-word display names give one.

### `galCardSIs` — the chips

| Property | Formula |
|---|---|
| `Items` | `=ThisItem.AlignedSIs` |
| `Layout` | Horizontal |
| `TemplateSize` | `=76` |
| `Height` | `=22` |

Inside: `recChip` (Rectangle, `Fill = ClrChip`, all `Radius* = RadiusChip`) and
`lblChip` (`Text = ThisItem.Value`, `Size = SizeChip`, `Color = ClrChipText`,
`Align = Align.Center`).

`Items` is evaluated in the *card's* scope, so `ThisItem` there is the pursuit. Inside
this gallery's own template `ThisItem` is the individual choice value. That scope shift
is the single most confusing thing about nested galleries in Power Fx and the most
common reason a chip row renders empty.

A fixed `TemplateSize` means long SI names clip. Variable-width chips need
`Self.Width` bound to the label's text width, which canvas doesn't expose — the
practical fix is to keep the choice values short in SharePoint.
