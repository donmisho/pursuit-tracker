# Screen — `scrMyActions`

Every action assigned to the signed-in user, across every pursuit — Open, Closed or All,
filtered by account and pursuit, sorted by due date or by opportunity. The other four
screens answer "what is happening on this pursuit"; this one answers "what do I owe anyone
this week".

```
scrMyActions
├── nav bar                        ◄── My Actions is the active tab
├── lblPageTitle / lblPageSub
├── drpMAView                      ◄── Open | Closed | All
├── drpMAAcct / drpMAPursuit       ◄── built from your own actions
├── drpMASort                      ◄── Due Date | Opportunity
├── btnFltClear
├── lblActionCount + btnRefreshActions
├── recHeaderRule + five column-header labels
├── galMyActions                   ◄── one row per action
│   ├── recRowDivider
│   ├── lblRowAccount                      Elevance Health
│   ├── lblRowOpp / lblRowSub              PUR-014 - Dynamics F&O / action · health
│   ├── lblRowDue                          due date, or the dependency wording
│   ├── lblRowStatus
│   ├── lblRowEffort
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

Laid out for Tablet (1366 × 768), "Scale to fit" off. Five columns, `X` relative to the
gallery and +24 for the header labels above it: Account 0/240 · Opportunity 256/520 ·
Due 792/130 · Status 938/160 · Effort 1114/110.

The filter row at `Y = 168`: View 68/130 · Account 278/190 · Pursuit 544/250 · Sort 872/150 ·
Clear Filters 1034/110 · count 1156/140 · refresh anchored right.

**Z-order**: `btnRowClick` is declared after the row content it covers, so the whole row is
clickable. The two empty-state labels come after the gallery, since they only show when it
has no rows and nothing under them is clickable then.

## What "mine" means

The owner column is text holding an email, not a Person column, so nothing normalises what
gets typed into it. Two mismatches show up in the real data: casing, and the domain — the
list holds `dmishory@westmonroe.com` while `User().Email` returns
`dmishory@westmonroepartners.com`. A row matches if the whole address matches
case-insensitively, **or** if the part before the `@` does:

```powerfx
Lower('Action Owner Entra ID') = Lower(gblUser.Email) ||
Lower(Left('Action Owner Entra ID' & "@", Find("@", 'Action Owner Entra ID' & "@") - 1)) =
    Lower(Left(gblUser.Email & "@", Find("@", gblUser.Email & "@") - 1))
```

The `& "@"` before each `Find` is what stops an address with no `@` from taking the whole
formula down: `Find` returns blank on no match and `Left(s, blank - 1)` errors. With the `@`
appended, a bare `dmishory` finds the one on the end and comes back whole.

Matching on the local part assumes one person owns a given mailbox name across the tenant's
domains. That holds here and it beats a screen that silently shows nothing — but the real
fix is in the list, and it's logged in `docs/OPEN-ITEMS.md`. An action owned by a different
name entirely still won't appear, which is why the empty state prints the address it
matched.

## The three views

`drpMAView` — **Open**, **Closed**, **All**, defaulting to Open. Closed is exactly
`Status = "Completed"`; everything else is open, including a blank status, since an action
nobody has triaged is still outstanding. The whole actions list loads either way and the
view filters `colMyActions` in memory: SharePoint doesn't delegate `<>` on a choice column,
so filtering in the query would silently truncate the set.

Closed rows render in `ClrTextFaint` and drop the At Risk pill — a completed action can't
be at risk.

## Account and pursuit filters

`drpMAAcct` and `drpMAPursuit` are built from `colMyActions`, not from the portfolio: an
account you own nothing on would only be an empty result waiting to happen. `btnFltClear`
resets all four dropdowns.

The pursuit list is **not** narrowed by the selected account. Picking an account and then a
pursuit outside it returns nothing, and the empty state says so rather than the screen
looking broken.

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
| `IsClosed` | `Status = "Completed"` — what the View filter reads |
| `DueWording` | "After proposal / quote", derived from `Predecessor Action ID` |
| `DueKey` | text sort key, due date first |
| `OppKey` | text sort key, account and pursuit first |

Pursuit identity comes from `colPursuitsMin` — the pursuits list reshaped to
`{ Key, Account, Name }` in one call — rather than a `LookUp` against SharePoint per action.
The pursuit name has its account prefix stripped the same way the portfolio list strips it,
so a row reads "Carelon Data Platform" over "Elevance Health" rather than the account twice.

## The sort

`drpMASort` offers **Due Date** and **Opportunity**, from `colFltSort`. `galMyActions.Items`
filters once into a `With`, then switches between two whole `Sort()` calls rather than
sorting on a conditional key:

```
=With(
    { rows: Filter(colMyActions, …view…, …account…, …pursuit…) },
    If(
        drpMASort.Selected.Value = "Opportunity",
        Sort(rows, OppKey, SortOrder.Ascending),
        Sort(rows, DueKey, SortOrder.Ascending)
    )
)
```

There is **no date filter**. The only conditions are the owner match and the three
dropdowns.

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

`TemplateSize` is 64. The opportunity column carries two lines; every other column is one,
top-aligned to the first.

| Control | Property | Formula |
|---|---|---|
| `lblRowAccount` | `Text` | `=Clip(ThisItem.Account, 32)` |
| | `X` / `Width` | `=0` / `=240` |
| | `Color` / `FontWeight` | `=If(ThisItem.IsClosed, ClrTextFaint, ClrText)` / Semibold |
| `lblRowOpp` | `Text` | `=Clip(ThisItem.Opportunity, 68)` |
| | `X` / `Width` | `=256` / `=520` |
| `lblRowSub` | `Text` | `=Clip(Trim(ThisItem.ActionTitle & If(IsBlank(ThisItem.HealthText), "", " · " & ThisItem.HealthText)), 84)` |
| | `Color` | `=If(ThisItem.HealthText = "At Risk" && !ThisItem.IsClosed, ClrRiskText, ClrTextFaint)` |
| | `Size` / `Y` | `=SizeMeta` / `=34` |
| `lblRowDue` | `Text` | `=Clip(DueLabel(ThisItem.Due, ThisItem.DueWording), 22)` |
| | `Color` | `=If(ThisItem.IsClosed, ClrTextFaint, !IsBlank(ThisItem.Due) && ThisItem.Due < Today(), ClrRiskText, ClrDate)` |
| | `X` / `Width` | `=792` / `=130` |
| `lblRowStatus` | `X` / `Width` | `=938` / `=160` |
| `lblRowEffort` | `X` / `Width` | `=1114` / `=110` |
| `btnRowClick` | `OnSelect` | `=Set(gblPursuitKey, ThisItem.PursuitKey); Set(gblNewPursuit, false); Navigate(scrPursuitWorkspace, ScreenTransition.None)` |

Every label is `Clip()`ped. Labels don't clip themselves — a Label whose text needs more room
than its `Height` allows keeps rendering and spills out of both ends onto its neighbours, and
a 64px row has no slack for that.

**Health rides in the subtitle rather than in a pill.** `lblRowSub` reads
"Draft executive proposal · At Risk", and the whole line turns `ClrRiskText` when health is
At Risk — one label instead of a pill plus its caption, and no guessing where variable-width
text ends. Closed rows drop the colour: a completed action can't be at risk.

**At risk is `Health`, not `Status`** — an in-progress action can be at risk, and so can a
not-started one.

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
