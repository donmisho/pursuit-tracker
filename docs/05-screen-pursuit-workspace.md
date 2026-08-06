# Screen — `scrPursuitWorkspace`

The detail page. Two equal columns: every pursuit field on the left, actions and status
updates on the right.

```
scrPursuitWorkspace
├── nav bar (four tabs)
├── lblBreadcrumb / lblAccount / lblPursuitName / btnEditDetails
├── LEFT  — cardDetails    every pursuit field, read-only, two per row
└── RIGHT — cardActions    btnAddAction + galActions   (top half)
          — cardUpdates    btnAddUpdate + galUpdates   (bottom half)
   EDIT PANEL              recPanelScrim + recPanel + pursuit/action/update fields
                           + btnPanelDelete / btnPanelCancel / btnPanelSave
```

Two equal columns, each `(Parent.Width - GapPage * 3) / 2`. Documents and the AI
overview moved to `scrPursuitDocsAI` — see `docs/05a-screen-documents-ai.md`.

Every card is a `Classic/Button` with `Text` `=""` (the only classic control with radius
properties) and a heading Label at `Size = SizeCardTitle`, `FontWeight = Semibold`.

Both columns are anchored to `Parent.Width`, so the layout follows the window rather than
assuming 1366. 119 controls.

---

## Screen `OnVisible`

```powerfx
Set(gblPursuit, LookUp('pursuit-tracker-pursuits', Title = gblPursuitKey));

// This pursuit's actions, with the dependency wording used when an action has no due
// date but does name a predecessor. Sorting happens on the gallery, not here -- the
// two-key sort (completed last, then due date) is a display concern.
ClearCollect(
    colActions_P,
    AddColumns(
        Filter('pursuit-tracker-actions', 'Pursuit ID' = gblPursuitKey) As A,
        DueWording,
        If(
            !IsBlank(A.'Due Date') || IsBlank(A.'Predecessor Action ID'),
            "",
            "After " & Lower(
                LookUp('pursuit-tracker-actions', Title = A.'Predecessor Action ID').'Workflow Stage'.Value
            )
        )
    )
);

ClearCollect(
    colUpdates,
    Sort(Filter('pursuit-tracker-status-updates', 'Pursuit ID' = gblPursuitKey), 'Update Date', SortOrder.Descending)
);

// Update authors are email strings and aren't necessarily pursuit owners, so colPeople
// (built at startup from owners only) won't have them. Top it up here.
ForAll(
    Distinct(colUpdates, 'Created By Entra ID') As E,
    If(
        IsBlank(E.Value) || !IsBlank(LookUp(colPeople, Email = E.Value)),
        false,
        Collect(colPeople, { Email: E.Value, Name: IfError(Office365Users.UserProfileV2(E.Value).displayName, E.Value) })
    )
);

Set(gblPanel, If(gblNewPursuit, "pursuit", ""));
Set(gblEditKey, "")
```

Every filter is `'Pursuit ID' = gblPursuitKey` — text equality on a text column, which
SharePoint delegates.

The collection is `colActions_P` rather than `colActions` because `colActions` holds every
action in the system, loaded by `LoadPortfolio` for the board's next-task calculation.
Reusing the name would empty the board's data as a side effect of opening a pursuit.

## `cardDetails` — the left column

One card, every field read-only, two per row, **in the order the columns appear in
`pursuit-tracker-pursuits`**:

| | Left | Right |
|---|---|---|
| 1 | Pursuit ID | Account |
| 2 | Salesforce opportunity | Opportunity link |
| 3 | Pursuit owner | Workflow stage |
| 4 | Health | Target decision date |
| 5 | Aligned SIs | Hyperscalers |
| 6 | Deal value | Active |
| 7 | Created | Modified |

Field width is `(cardDetails.Width - 60) / 2`, so the pairs stay side by side at any
window size. Everything is a Label — editing is the details panel's job, and a card of
disabled inputs reads as broken rather than as read-only.

Created and Modified are SharePoint's own columns; they need no schema change.

Deal value is `Estimated Fees` formatted as currency, and reads "Not set" rather than
`$0` when empty — every row is currently empty, and `$0` would look like a real number.

## `galActions` — sorted by status, then due date

```powerfx
Sort(
    Sort(colActions_P, If(IsBlank('Due Date'), Date(2099, 12, 31), 'Due Date'), SortOrder.Ascending),
    If(Status.Value = "Completed", 1, 0),
    SortOrder.Ascending
)
```

Two nested `Sort` calls, inner first: due date ascending, then completed-last on top of
it. Power Fx sorts are stable, so the inner ordering survives inside each group. There's
no multi-key `Sort`, and `SortByColumns` can't take an expression — this is the way to get
a compound sort out of Power Fx.

Undated actions substitute `Date(2099, 12, 31)` so they sink to the bottom of the open
group rather than floating to the top, which is what a blank date would otherwise do.

## `galUpdates` — newest first, with the time

`Sort(colUpdates, 'Update Date', SortOrder.Descending)`. The stamp line shows
`mmm d, yyyy · h:mm AM/PM` plus the update type rather than "Today" — on a feed where two
updates can land in the same afternoon, the relative form hides the ordering it's meant to
convey.

## The edit panel

One slide-over, three modes on this screen. `gblPanel` holds which: `"pursuit"`,
`"action"`, `"update"`, or `""` for closed. The `"doc"` mode lives on the documents screen. `gblEditKey` holds the `ACT-nnn` / document title /
`UPD-nnn` being edited, or `""` for a new record — that single variable drives three
things: whether Save patches or collects, whether Delete is offered, and what the panel
header says.

640 wide over a dimming scrim. The pursuit mode lays its 13 fields out in two columns;
the three child modes use one.

### Getting in

| From | Control | Opens |
|---|---|---|
| Header | `btnEditDetails` | pursuit details, all fields |
| Actions card | `btnAddAction` (+ Add) | blank action |
| Actions gallery | `btnActionRow` — transparent, covers the row | that action |
| Updates card | `btnAddUpdate` | blank update |
| Updates gallery | `btnUpdateEdit` | that update |

Every one of those handlers does the same three things: set the mode, set `gblEditKey`,
set the record global (`gblEditAction` / `gblEditUpdate`), then `Reset()` every input in
that mode. The documents screen repeats the pattern with `gblEditDoc`.

**The `Reset()` calls are not optional.** A `Classic/TextInput` keeps whatever the user
last typed even after its `Default` formula changes to a different record's value. Without
the resets, opening action B after editing action A shows A's text. It's the single
easiest way to build a form that silently saves the wrong record.

### Fields

**Pursuit** — every column in `pursuit-tracker-pursuits` except `Title`, which is
generated: Account Name, Pursuit Name, Workflow Stage, Health, Owner email, Target
Decision Date, Active, Salesforce Opportunity ID, Salesforce Opportunity URL, Aligned SIs,
Hyperscalers, Estimated Fees, AI Overview Current Version.

**Action** — Action Title, Workflow Stage, Status, Health, Effort Size, Due Date, Owner
email, Predecessor Action ID, Notes. `Completed Date` isn't a field: Save sets it to
`Now()` when Status becomes Completed and clears it otherwise, which is one fewer thing to
keep consistent by hand.

**Update** — Update Text, Update Type, Risk / Decision. `Update Date` and
`Created By Entra ID` are set on create and left alone on edit, so editing a typo doesn't
re-date the entry.

Owner fields are plain text inputs rather than people pickers. The columns hold email
strings, not Person values, so a combo box would mean converting between a user record and
an address in both directions for no gain.

## The lookup list

`pursuit-tracker-lookups` — one row per allowed value, so adding a workflow stage is a row
in a list rather than an edit to five column definitions.

| Column | Internal | Holds |
|---|---|---|
| Title | `Title` | the lookup type, e.g. `Workflow Stage`. Displayed as "Lookup Type" |
| Value | `field_1` | the value the app writes |
| Sort Order | `field_2` | display order within a type |
| Active | `field_3` | `Yes` to show it |

**Formulas use `Title`, not "Lookup Type".** The import renamed the `LinkTitle` *display*
column, which is what the SharePoint view shows; the underlying field is still `Title`,
the same as `PUR-001` is in the pursuits list.

It loads once in `App.OnStart`:

```powerfx
ClearCollect(
    colLookups,
    ForAll(
        Sort('pursuit-tracker-lookups', 'Sort Order', SortOrder.Ascending) As L,
        { LookupType: L.Title, Value: L.Value }
    )
);
```

Once, into a collection, rather than per dropdown — at 28 rows the whole list is one call,
and reading it per control would mean twelve.

### `Active` isn't in the filter

It can't be. The column is a Choice with an **empty choice set** and fill-in enabled, and a
Choice column with no defined choices never reaches the Power Apps schema — referencing it
fails at author time with *"Name isn't valid. 'Active' isn't recognized"*, and because the
`Filter` returns an error the whole `ClearCollect` goes red with it.

Every row is active today, so nothing is lost yet. To get retirement back, make `Active` a
real column in SharePoint — a Yes/No column, or a Choice with `Yes` and `No` actually
defined — refresh the data source in the Data pane, then wrap the source:

```powerfx
Filter('pursuit-tracker-lookups', Active)                  // Yes/No
Filter('pursuit-tracker-lookups', Active.Value = "Yes")    // Choice
```

Until then, deleting a row is how a value is retired.

### Why `ForAll` and not `ShowColumns`

`Choices()` returns a **single-column table whose column is named `Value`**. That's the
shape a `Classic/DropDown` displays without being told which field to show, and it's why
every save branch reads `drpPurStage.Selected.Value`.

`ForAll(Filter(colLookups, LookupType = "Workflow Stage") As L, { Value: L.Value })`
returns exactly that same shape. So the binding is a one-line change per control and **not
a single save formula had to change** — which is the whole reason to project rather than
hand the dropdown the four-column table and pick a display field.

`ShowColumns` is the obvious way to write that projection and it doesn't work here. It
throws *"ShowColumns has some invalid arguments"* against a SharePoint source whose column
set it can't pin down at author time, and again against the choice tables the combo boxes
read for their default selection. `ForAll` over a record literal is the same projection
with the shape stated explicitly, which is what makes it type cleanly — and it's the
pattern `colStages` and `colPeople` already use.

The lookup type arrives as `LookupType`, not `Title`. `Title` is a SharePoint column name
in all five other lists and reads as the wrong thing here; `Type` is a Power Fx keyword.

### What each dropdown binds to

| Screen / mode | Control | Lookup Type |
|---|---|---|
| Pursuit | `drpPurStage` | `Workflow Stage` |
| Pursuit | `drpPurHealth` | `Health` |
| Pursuit | `cmbPurSIs` | `Systems Integrator` |
| Pursuit | `cmbPurHype` | `Hyperscaler` |
| Action | `drpActStage` | `Workflow Stage` |
| Action | `drpActStatus` | `Action Status` |
| Action | `drpActHealth` | `Health` |
| Action | `drpActEffort` | `Effort Size` |
| Update | `drpUpdType` | — still `Choices('pursuit-tracker-status-updates'.'Update Type')` |
| Update | `drpUpdRisk` | — still `Choices(…'Risk / Decision')` |
| Documents | `drpDocType` | — still `Choices('pursuit-tracker-documents'.'Document Type')` |
| Documents | `drpDocAi` | — still `Choices(…'Include in AI Overview')` |

Stage and Health are deliberately shared between the pursuit and the action rather than
split into `Pursuit Health` / `Action Health`. An action that's off track on a pursuit
that's on track is a comparison you want to be able to make, and it stops being one the
moment the two vocabularies can drift.

### The multi-selects needed one more change

`cmbPurSIs` and `cmbPurHype` write to multi-choice columns, and they were passing
`SelectedItems` straight into the `Patch`. That worked only because `Items` was
`Choices()` — the records carried the column's type with them. A projected table doesn't,
and an untyped table into a multi-choice column is the silent-bounce failure again. Both
writes are now explicit:

```powerfx
'Aligned SIs': ForAll(cmbPurSIs.SelectedItems As S, { Value: S.Value }),
```

The record literal takes its type from the `Patch` target, which is the one place the
binding is guaranteed. `DefaultSelectedItems` is projected the same way, so both sides of
the combo box are `{Value}` and the existing selections still highlight.

## Four dropdowns have no lookup type

`Update Type`, `Risk / Decision`, `Document Type` and `Include in AI Overview` aren't in
the list, so they stay on `Choices()` — which is what they do today, so nothing regressed.

`Include in AI Overview` is a yes/no flag rather than a vocabulary and doesn't belong in a
lookup list at all. The other three would fit; they just need rows.

## The values don't match the columns yet

**This is the thing to settle before anyone edits a pursuit.** The columns are still Choice
columns, and the app still writes a text value into them. Where the lookup list and the
column disagree, the write either bounces or — because fill-in is enabled — quietly
succeeds and creates a second spelling of the same concept.

| Lookup list says | Column / code says | What breaks |
|---|---|---|
| `Unassigned / Intake` | `Unassigned` | `StageAccent` falls through to grey; the pursuit lands in no board column |
| `Proposal / Quote` | `Proposal/Quote` | same |
| `Complete` | `Completed` | the actions sort stops sinking completed rows; the board's next-action calculation starts counting finished work |
| `Review / Decision` | not a choice | new |
| `Completed / Closed` | not a choice | new |

`On track` / `At risk` / `Off track` and the SI and hyperscaler values all match.

Three of those strings are compiled into the app, not just the data:
`StageAccent` in `App.Formulas`, the `colStages` fallback in `App.OnStart`, and
`Status.Value <> "Completed"` in six places across the board and the workspace.

The cheapest fix is to make the **lookup list** match what's already in the columns and the
data — change `Unassigned / Intake` to `Unassigned`, `Proposal / Quote` to
`Proposal/Quote`, `Complete` to `Completed`. Nothing else moves.

Going the other way — making the columns and the code match the list — means editing the
choice sets, updating fourteen pursuit rows and every action row, and changing those three
places in the app. Worth doing if the new names are the ones you actually want, but it's a
data migration, not a settings change.

### And the board only fits five columns

`BoardColumns = 5`. Seven stages means two of them are off the right edge. If
`Review / Decision` and `Completed / Closed` are real stages, either the board needs to
divide by 7 (columns get narrow — the cards are already tight at 5) or closed pursuits need
to drop off the board and live in the list. Say which and I'll build it.

### Saving

`btnPanelSave.OnSelect` is one `Switch`-shaped `If` over `gblPanel`. Each branch either
`Collect`s (when `gblEditKey = ""`) or `Patch`es, then checks `Errors()` on that list:

```powerfx
If(
    IsEmpty(Errors('pursuit-tracker-pursuits')),
    …reload, close the panel…,
    Notify("Save failed: " & First(Errors('pursuit-tracker-pursuits')).Message, NotificationType.Error)
)
```

**Power Apps swallows write failures.** A `Patch` that a column type rejects returns blank
and carries on — no error, no dialog, nothing in the UI. The button looks broken when it
isn't; it ran and the write bounced. Checking `Errors()` after every write and surfacing
the message is the difference between a two-minute fix and an afternoon.

The panel also stays open on failure, so whatever was typed isn't lost.

The field record is written out inline in both the Collect and the Patch branch rather
than built once into a variable. It's more text, but a global holding a record of control
values loses its type binding to the data source — multi-choice columns in particular go
through as an untyped table and the write bounces silently, which is exactly the failure
above.

New IDs follow the existing convention —
`"ACT-" & Text(Max(...) + 1, "000")` over the highest existing three-digit suffix. Same
pattern for `PUR-`, `DOC-` and `UPD-`. It assumes the three-digit format holds; at 999 it
starts colliding.

`DisplayMode` on Save is bound to the one field that can't be empty in each mode — account
and pursuit name, action title, update text — so the button is dead until the record is
viable.

### Deleting

`btnPanelDelete` is visible only for the child modes and only when editing an
existing record, so it can't appear on a new record or on the pursuit. It `Remove`s the row
and reloads.

**There is no delete for a pursuit.** Removing one would orphan its actions, documents,
updates and AI history — SharePoint has no cascade, and a silent four-list cleanup buried
in a button is the kind of thing you discover a month later. Delete a pursuit in the
SharePoint list, where what else is attached is visible.

### Add mode

`btnAddPursuit` on the board and the list both set `gblPursuitKey` to blank and
`gblNewPursuit` to true, then navigate here. `OnVisible` opens the details panel
immediately, the header reads "New pursuit", and the + Add buttons on the child cards are
disabled until the pursuit exists — there's no `Pursuit ID` to attach a child to yet.

Saving generates the `PUR-nnn`, sets `gblPursuitKey`, and clears `gblNewPursuit`, at which
point the screen behaves like any other pursuit.

## The scrim has to be RGBA, not ColorFade

`recPanelScrim` uses `=RGBA(0, 0, 0, 0.55)`.

`ColorFade(ClrPage, -0.4)` looks like the obvious way to dim the page behind the panel and
is wrong: `ColorFade` darkens a colour, it doesn't make it translucent. Applied to a page
background that's already near-black it returns solid black at full opacity, so the screen
behind the panel doesn't dim — it disappears. Only an alpha channel gives you a scrim, and
only `RGBA` has one.
