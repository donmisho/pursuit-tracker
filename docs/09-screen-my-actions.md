# Screen — `scrMyActions`

Every open action assigned to the signed-in user, across every pursuit, sorted by due date
or by opportunity. The other four screens answer "what is happening on this pursuit"; this
one answers "what do I owe anyone this week".

```
scrMyActions
├── nav bar                        ◄── My Actions is the active tab
├── lblPageTitle / lblPageSub
├── lblSortCap + drpMASort         ◄── Due Date | Opportunity
├── lblActionCount + btnRefreshActions
├── recHeaderRule + four column-header labels
├── galMyActions                   ◄── one row per open action
│   ├── recRowDivider
│   ├── lblRowAction / lblRowMeta          stage · effort
│   ├── lblRowOpp / lblRowAccount          PUR-014 - Dynamics F&O / account
│   ├── lblRowStatus
│   ├── recRowPill + lblRowPill            At Risk
│   ├── lblRowDue                          due date, or the dependency wording
│   └── btnRowClick                ◄── transparent, on top: opens the pursuit workspace
├── lblEmptyTitle / lblEmptyHint   ◄── only when colMyActions is empty
└── lblFooterNote
```

## Screen

| Property | Formula |
|---|---|
| `Fill` | `=ClrPage` |
| `OnVisible` | `src/screens/scrMyActions.OnVisible.powerfx`, pasted whole |

Create a blank screen named exactly `scrMyActions` before pasting anything, including the
other four screens — their nav buttons `Navigate(scrMyActions, …)`, and `Navigate()` to a
screen that doesn't exist is an error Studio can't resolve on its own.

Laid out for Tablet (1366 × 768), "Scale to fit" off. Columns, `X` relative to the gallery
and +24 for the header labels above it: Action 0/420 · Opportunity 436/380 · Status 832/200,
with the At Risk pill and the due date anchored to the right edge.

**Z-order**: `btnRowClick` is declared after the row content it covers, so the whole row is
clickable. The two empty-state labels come after the gallery, since they only show when it
has no rows and nothing under them is clickable then.

## What "mine" and "open" mean

**Mine** is `Lower('Action Owner Entra ID') = Lower(gblUser.Email)`. The owner column is a
text column holding an email, not a Person column, so nothing normalises what gets typed
into it — `Don.Mishory@…` and `don.mishory@…` are different strings to SharePoint and the
comparison is case-folded on both sides to compensate. It cannot compensate for a different
address: an action owned by an alias, or by a name rather than an address, will not appear.
That is why the empty state prints the address it matched instead of just saying "nothing
found" — the difference between "no work" and "wrong email in the list" is the only thing
worth knowing when the screen is blank.

**Open** is `Status.Value <> "Completed"`, filtered in memory. SharePoint doesn't delegate
`<>` on a choice column, so doing it in the query would silently truncate the set; the whole
actions list is pulled and filtered locally, exactly as the board and the list screens do.
A blank status counts as open — an action nobody has triaged is still outstanding.

## `colMyActions`

Built in `OnVisible`, one row per matching action, every column a scalar. Choice columns are
flattened to `.Value` here rather than in the gallery: a choice-valued column doesn't survive
into a collection with its type intact, which is the same trap `NextActionTitle` /
`NextActionDue` avoid in `App.OnStart`.

| Column | Holds |
|---|---|
| `ActionKey` | `ACT-007` |
| `PursuitKey` | `PUR-014` — what `btnRowClick` writes to `gblPursuitKey` |
| `ActionTitle` | "Draft executive proposal" |
| `StageText` / `StatusText` / `HealthText` / `EffortText` | flattened choice values |
| `Account` | the account name, from the pursuit |
| `Opportunity` | `PursuitLabel(key, name)` → `PUR-014 - Dynamics F&O` |
| `Due` | the raw `Due Date`, for display and the overdue test |
| `DueWording` | "After proposal / quote", derived from `Predecessor Action ID` |
| `DueKey` | text sort key, due date first |
| `OppKey` | text sort key, account and pursuit first |

Pursuit identity comes from `colPursuitsMin` — the pursuits list reshaped to
`{ Key, Account, Name }` in one call — rather than a `LookUp` against SharePoint per action.
The pursuit name has its account prefix stripped the same way the portfolio list strips it,
so a row reads "Carelon Data Platform" over "Elevance Health" rather than the account twice.

## The sort

`drpMASort` offers **Due Date** and **Opportunity**, from `colFltSort`. `galMyActions.Items`
switches between two whole `Sort()` calls rather than sorting once on a conditional key:

```
=If(
    drpMASort.Selected.Value = "Opportunity",
    Sort(colMyActions, OppKey, SortOrder.Ascending),
    Sort(colMyActions, DueKey, SortOrder.Ascending)
)
```

Both keys are single text columns computed at load, which is what makes one `Sort()` per
branch enough:

- `DueKey` = `yyyy-mm-dd` · account · `ACT-id`. Dates sort as text only in that format, which
  is why it isn't the display format. Actions with no due date carry `2099-12-31`, so they
  land at the bottom instead of the top.
- `OppKey` = account · pursuit name · `PUR-id` · `yyyy-mm-dd` · `ACT-id`. Grouping by
  opportunity still reads soonest-first inside each opportunity, because the date is part of
  the key rather than left to the previous sort.

Both end in the `ACT-id`, so rows that tie on everything else still come out in the same
order every render. Power Fx doesn't promise `Sort()` is stable, so a nested-`Sort` version
of this — sort by date, then re-sort by opportunity — would be relying on an accident.

## Row template

`TemplateSize` is 64. Two lines on the left, two in the middle, one each on the right.

| Control | Property | Formula |
|---|---|---|
| `lblRowAction` | `Text` | `=Clip(ThisItem.ActionTitle, 62)` |
| | `X` / `Width` | `=0` / `=420` |
| `lblRowMeta` | `Text` | stage, then `· effort` when there is one |
| `lblRowOpp` | `Text` | `=Clip(ThisItem.Opportunity, 52)` |
| | `X` / `Width` | `=436` / `=380` |
| `lblRowAccount` | `Text` | `=Clip(ThisItem.Account, 52)` |
| `lblRowStatus` | `X` / `Width` | `=832` / `=200` |
| `recRowPill` / `lblRowPill` | `Visible` | `=ThisItem.HealthText = "At Risk"` |
| `lblRowDue` | `Text` | `=Clip(DueLabel(ThisItem.Due, ThisItem.DueWording), 24)` |
| | `Color` | `=If(!IsBlank(ThisItem.Due) && ThisItem.Due < Today(), ClrRiskText, ClrDate)` |
| `btnRowClick` | `OnSelect` | `=Set(gblPursuitKey, ThisItem.PursuitKey); Set(gblNewPursuit, false); Navigate(scrPursuitWorkspace, ScreenTransition.None)` |

Every label is `Clip()`ped. Labels don't clip themselves — a Label whose text needs more room
than its `Height` allows keeps rendering and spills out of both ends onto its neighbours, and
a 64px row has no slack for that.

**At risk is `Health`, not `Status`** — an in-progress action can be at risk, and so can a
not-started one. Same pill as the workspace.

**The row opens the pursuit workspace, not the action.** The workspace's edit panel is opened
by `btnActionRow`, whose `OnSelect` `Reset()`s nine controls on that screen; `Reset()` can't
reach controls on a screen you aren't on, and `scrPursuitWorkspace.OnVisible` clears
`gblPanel` and `gblEditKey` on arrival anyway. So the row sets the pursuit and navigates, and
the action is one more click from there.

## Refresh

`btnRefreshActions` carries a copy of the `OnVisible` file's three `ClearCollect`s behind a
`Refresh('pursuit-tracker-actions')`. Canvas apps have no user-defined behaviour functions,
so a load that has to run both on arrival and on demand exists twice — the same duplication
`LoadPortfolio` has across `App.OnStart` and two `OnVisible`s. **Change both copies.**

There is no `+`. Actions are created in the pursuit workspace, where the pursuit they belong
to is unambiguous.

## Nav

The other four screens each gained a `btnNavActions` at `X = 970`, `Width = 150`, which is
why adding this screen means repasting them. Nothing on this screen depends on a pursuit
being selected, so the tab is never disabled — unlike Workspace and Documents & AI, which
grey out until `gblPursuitKey` holds something.
