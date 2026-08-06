# Screen — `scrPursuitWorkspace`

The detail page. A wide left rail (Salesforce, AI overview, actions) and a narrower
right rail (alignment, documents, updates, overview history).

```
scrPursuitWorkspace
├── nav bar
├── lblBreadcrumb / lblTitle / lblSubtitle
├── btnAddAction / btnAddUpdate
├── LEFT RAIL
│   ├── cardSalesforce   — link, linked pill, owner, target decision date
│   ├── cardOverview     — overview text, Refresh, provenance line
│   └── cardActions      — galActions
└── RIGHT RAIL
    ├── cardAlignment    — galAlignSIs, galAlignHype
    ├── cardDocuments    — galDocs
    ├── cardUpdates      — galUpdates
    └── cardHistory      — galHistory
```

Every card is a Rectangle (`Fill = ClrCard`, `BorderColor = ClrBorder`,
`BorderThickness = 1`, all `Radius* = RadiusCard`) with a heading Label at
`Size = SizeCardTitle`, `FontWeight = Semibold`, `Color = ClrText`.

Left rail `X = GapPage`, `Width = 640`. Right rail `X = 688`, `Width = 400`.

---

## Screen `OnVisible`

```powerfx
Set(gblPursuit, LookUp('pursuit-tracker-pursuits', Title = gblPursuitKey));

// This pursuit's actions, with the dependency wording the mockup shows in place of a
// date. There's no free-text due column in the schema -- when an action has no due date
// but does name a predecessor, "after <the predecessor's stage>" is the best available
// rendering of "Legal review comes after the proposal".
ClearCollect(
    colActions_P,
    AddColumns(
        Sort(
            Filter('pursuit-tracker-actions', 'Pursuit ID' = gblPursuitKey),
            If(IsBlank('Due Date'), Date(2099, 12, 31), 'Due Date'),
            SortOrder.Ascending
        ) As A,
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
ClearCollect(
    colDocs,
    Sort(Filter('pursuit-tracker-documents', 'Pursuit ID' = gblPursuitKey), 'Added Date', SortOrder.Descending)
);
ClearCollect(
    colHistory,
    Sort(Filter('pursuit-tracker-ai-history', 'Pursuit ID' = gblPursuitKey), 'Version Number', SortOrder.Descending)
);
// The app never writes this list, so nothing in it guarantees exactly one current
// version. Prefer the flag; fall back to the highest version number when it's missing
// or ambiguous, so the card always shows something rather than going blank.
Set(gblOverview, LookUp(colHistory, 'Is Current'.Value = "Yes"));
If(IsBlank(gblOverview), Set(gblOverview, First(colHistory)));
If(IsBlank(gblOverview), Set(gblOverview, LookUp('pursuit-tracker-ai-history', ID < 0)));

// Update authors are email strings too, and they aren't necessarily pursuit owners, so
// colPeople (built at startup from owners only) won't have them. Top it up here.
ForAll(
    Distinct(colUpdates, 'Created By Entra ID') As E,
    If(
        IsBlank(E.Value) || !IsBlank(LookUp(colPeople, Email = E.Value)),
        false,
        Collect(colPeople, { Email: E.Value, Name: IfError(Office365Users.UserProfileV2(E.Value).displayName, E.Value) })
    )
);

// Add mode arrives from the board or list with a blank key -- open the details panel
// straight away, since an empty workspace with nothing to fill in is a dead end.
Set(gblPanel, If(gblNewPursuit, "pursuit", ""));
Set(gblEditKey, "");
```

Every filter is `'Pursuit ID' = gblPursuitKey` — text equality on a text column, which
SharePoint delegates. That's the payoff of the schema keying on `PUR-001` rather than on
list item IDs.

The collection is `colActions_P` rather than `colActions` because `colActions` already
holds every action in the system, loaded by `LoadPortfolio` for the board's next-task
calculation. Reusing the name would empty the board's data as a side effect of opening a
pursuit.

## Header

| Control | Property | Formula |
|---|---|---|
| `lblBreadcrumb` | `Text` | `="SI pursuit management"` — `Size = SizeMeta`, `Color = ClrTextFaint` |
| `lblAccount` | `Text` | `=If(gblNewPursuit, "New pursuit", Clip(gblPursuit.'Account Name', 40))` |
| | `Size` / `FontWeight` / `Color` | `=SizePageTitle` / `=FontWeight.Semibold` / `=ClrText` |
| `lblPursuitName` | `Text` | the prefix-stripping formula, wrapped in `Clip(..., 90)` |
| | `Size` / `Color` | `=SizeCardTitle` / `=ClrTextMuted` |
| `btnEditDetails` | `Text` | `=If(gblNewPursuit, "Enter details", "Edit details")` |
| | `OnSelect` | `=Set(gblPanel, "pursuit"); Reset(txtPurAccount); …` (one `Reset` per field) |

Account leads at 26pt with the pursuit name under it at 15pt, rather than one run-on
line. Same prefix-stripping as the board and list, so "ELEVANCE HEALTH: Carelon — …"
renders as **Elevance Health** over "Carelon - Unified Data and Analytics Platform…".

## `cardSalesforce`

| Control | Property | Formula |
|---|---|---|
| `lnkSfOpp` (Label) | `Text` | `=Coalesce(gblPursuit.'Salesforce Opportunity ID', "No opportunity linked")` |
| | `Color` / `Underline` | `=If(IsBlank(gblPursuit.'Salesforce Opportunity URL'), ClrTextMuted, ClrLink)` / `=Not(IsBlank(gblPursuit.'Salesforce Opportunity URL'))` |
| | `DisplayMode` | `=If(IsBlank(gblPursuit.'Salesforce Opportunity URL'), DisplayMode.View, DisplayMode.Edit)` |
| | `OnSelect` | `=Launch(gblPursuit.'Salesforce Opportunity URL')` |
| `lblSfHint` | `Text` | `="Synced CRM information: account, opportunity owner, amount, close date, and stage"` |
| | `Size` / `Color` / `Wrap` | `=SizeMeta` / `=ClrTextFaint` / `=true` |
| `recSyncPill` | `Fill` | `=If(IsBlank(gblPursuit.'Salesforce Opportunity URL'), ClrChip, ClrOkFill)` |
| | all `Radius*` | `=RadiusChip` |
| `lblSyncPill` | `Text` | `=If(IsBlank(gblPursuit.'Salesforce Opportunity URL'), "Not linked", "Linked")` |
| | `Color` | `=If(IsBlank(gblPursuit.'Salesforce Opportunity URL'), ClrChipText, ClrOkText)` |
| `lblOwnerCap` | `Text` | `="PURSUIT OWNER"` — `Size = SizeMeta`, `Color = ClrTextMuted` |
| `recWsAvatar` (Rectangle, all `Radius* = 12`) / `lblWsInitials` | `Text` | `=Initials(Coalesce(LookUp(colPeople, Email = gblPursuit.'WM Pursuit Owner Entra ID').Name, gblPursuit.'WM Pursuit Owner Entra ID'))` |
| `lblWsOwnerName` | `Text` | `=Coalesce(LookUp(colPeople, Email = gblPursuit.'WM Pursuit Owner Entra ID').Name, gblPursuit.'WM Pursuit Owner Entra ID')` |
| `lblWsOwnerOrg` | `Text` | `="West Monroe · Entra ID"` — `Size = SizeMeta`, `Color = ClrTextFaint` |
| `lblCloseCap` | `Text` | `="TARGET DECISION"` |
| `lblCloseDate` | `Text` | `=If(IsBlank(gblPursuit.'Target Decision Date'), "Not set", Text(gblPursuit.'Target Decision Date', "mmmm d"))` |
| | `Size` / `FontWeight` / `Color` | `=SizeCardTitle` / `=FontWeight.Semibold` / `=ClrText` |

The mockup's link reads "Northwind FY27 renewal" — an opportunity *name*. The schema
carries the opportunity ID and URL but no name, so the link shows the ID
(`006PP00000lnpSvYAI`), which is accurate but not friendly. If the label matters, add a
`Salesforce Opportunity Name` text column and point `lnkSfOpp.Text` at it; nothing else
changes.

The sync pill infers from the URL rather than reading a sync-status column, because
there isn't one. It's honest about the only fact available: whether this pursuit is
linked to Salesforce at all. Eight of your fourteen currently aren't.

## `cardOverview`

| Control | Property | Formula |
|---|---|---|
| `lblOverviewHead` | `Text` | `="AI overview"` |
| `lblOverviewBody` | `Text` | `=Coalesce(gblOverview.'Overview Text', "No overview has been generated for this pursuit yet.")` |
| | `Size` / `Color` / `Wrap` / `AutoHeight` | `=SizeBody` / `=ClrText` / `=true` / `=true` |
| `lblOverviewMeta` | `Text` | `=If(IsBlank(gblOverview), "", "Version " & gblOverview.'Version Number' & " · refreshed " & Lower(RelativeDay(gblOverview.'Refreshed Date')) & " · prior versions retained in history")` |
| | `Size` / `Color` / `Wrap` | `=SizeMeta` / `=ClrTextFaint` / `=true` |

**Display only — there is no Refresh button.** SharePoint's native AI populates
`Overview Text`, `Version Number`, `Refreshed Date`, and `Is Current`; the app reads them
and writes nothing back. That removes the one part of this build that couldn't be finished
on standard connectors, and it removes the version-management code with it — no version
numbering, no `Is Current` flip, no transaction ordering to worry about.

Two consequences worth knowing:

**Nothing enforces one current version per pursuit.** The app used to guarantee that by
demoting before inserting. Now whatever populates the list owns that invariant, which is
why `OnVisible` falls back to the highest `Version Number` when the flag is missing — the
card degrades to "probably right" rather than to blank.

**The provenance line no longer names its sources.** With `Source Summary` removed it
reads "Version 3 · refreshed today · prior versions retained in history". The mockup's
"from Salesforce and four attached materials" phrasing needs a column to read it from; if
you want it back, the closest free substitute is counting documents where
`Include in AI Overview` is `Yes`, which the workspace already loads:
`CountRows(Filter(colDocs, 'Include in AI Overview'.Value = "Yes")) & " included documents"`.
That counts what's flagged now, not what the overview was actually built from, so it will
drift as documents are added — which is why it isn't the default.

**One thing to check on the SharePoint side: `Overview Text` is a 255-character Text
column** until you convert it (`docs/01-data-model.md`, required change 1). The sample row
is 197 characters and the mockup's overview is about 430. SharePoint truncates rather than
erroring, and since the AI is writing the column rather than the app, you'd only notice by
reading a cut-off overview in the app.

## `cardActions` — `galActions`

| Property | Formula |
|---|---|
| `Items` | `=colActions_P` |
| `TemplateSize` | `=56` |

| Control | Property | Formula |
|---|---|---|
| `lblActionTitle` | `Text` | `=ThisItem.'Action Title'` — `FontWeight = Semibold`, `Color = ClrText`, `Wrap = true` |
| | `Color` | `=If(ThisItem.Status.Value = "Completed", ClrTextFaint, ClrText)` |
| `lblActionStage` | `Text` | `=ThisItem.'Workflow Stage'.Value` — `Color = ClrTextMuted` |
| `lblActionEffort` | `Text` | `=ThisItem.'Effort Size'.Value` — `Color = ClrText` |
| `recActionPill` | `Visible` | `=ThisItem.Health.Value = "At risk"` |
| | `Fill` / all `Radius*` | `=ClrRiskFill` / `=RadiusChip` |
| `lblActionPill` | `Text` / `Visible` | `="At risk"` / `=recActionPill.Visible` |
| | `Color` / `Align` | `=ClrRiskText` / `=Align.Center` |
| `lblActionDue` | `Text` | `=DueLabel(ThisItem.'Due Date', ThisItem.DueWording)` |
| | `Visible` / `Color` | `=Not(recActionPill.Visible)` / `=ClrTextMuted` |
| `recActionDivider` | `Y` / `Height` / `Fill` | `=Parent.TemplateHeight - 1` / `=1` / `=ClrDivider` |

The pill reads `Health`, not `Status` — those are separate columns, and ACT-002 is
`In progress` / `At risk`, which is the mockup's red pill on "Draft executive proposal".
An earlier version of this doc had it on `Status`, which would never have fired.

Pill and due date share a slot, matching the mockup where "Draft executive proposal"
shows its pill and "Confirm buying committee" shows Aug 12. A task that is both at risk
and dated shows the risk, the more urgent of the two.

Completed actions stay in the list, greyed. ACT-003 is completed and still shows its
dependency relationship, which is the point of the panel.

## `cardAlignment`

| Control | Property | Formula |
|---|---|---|
| `lblSICap` | `Text` | `="SYSTEMS INTEGRATORS"` — `Size = SizeMeta`, `Color = ClrTextMuted` |
| `galAlignSIs` | `Items` | `=gblPursuit.'Aligned SIs'` |
| `lblHypeCap` | `Text` | `="HYPERSCALERS"` |
| `galAlignHype` | `Items` | `=gblPursuit.Hyperscalers` |

Both: `Layout` Horizontal, `TemplateSize = 76`, `Height = 26`, chip template as on the
board.

The mockup's "+ Other" chips are SharePoint's fill-in-choice behaviour surfacing in the
UI, and these columns do have it enabled — a text input that patches a new value works.
I've left it out. Fill-in choices are how you end up with both "Proposal/Quote" and
"Proposal / Quote" in the same system, and now that the choice lists have real values,
adding to them deliberately in SharePoint is worth the extra thirty seconds.

## `cardDocuments` — `galDocs`

| Property | Formula |
|---|---|
| `Items` | `=colDocs` |
| `TemplateSize` | `=44` |

| Control | Property | Formula |
|---|---|---|
| `lblDocLink` | `Text` | `=ThisItem.Title` |
| | `Color` / `Underline` | `=ClrLink` / `=true` |
| | `OnSelect` | `=Launch(SafeUrl(ThisItem.'Document URL'))` |
| `lblDocType` | `Text` | `=ThisItem.'Document Type'.Value & If(ThisItem.'Include in AI Overview'.Value = "Yes", " · in overview", "")` |
| | `Size` / `Color` | `=SizeMeta` / `=ClrTextFaint` |

`SafeUrl` prepends `https://` when the stored URL has no scheme, which DOC-001's doesn't.
Without it `Launch()` treats the value as a relative path and opens a broken address.

In the mockup the three document links run together as one wrapped block
("Working proposal deckDiscovery notesNTT solution outline"). One gallery row per
document gives each its own hit target, which is what that layout is reaching for.

## `cardUpdates` — `galUpdates`

| Property | Formula |
|---|---|
| `Items` | `=colUpdates` |
| `TemplateSize` | `=96` |

| Control | Property | Formula |
|---|---|---|
| `lblUpdateBody` | `Text` | `=ThisItem.'Update Text'` — `Color = ClrText`, `Wrap = true`, `Height = 44` |
| `recUpdateTag` | `Visible` | `=Not(IsBlank(ThisItem.'Risk / Decision'.Value))` |
| | `Fill` | `=If(ThisItem.'Risk / Decision'.Value = "Risk", ClrRiskFill, ClrChip)` |
| `lblUpdateTag` | `Text` / `Visible` | `=ThisItem.'Risk / Decision'.Value` / `=recUpdateTag.Visible` |
| | `Color` | `=If(ThisItem.'Risk / Decision'.Value = "Risk", ClrRiskText, ClrChipText)` |
| `lblUpdateMeta` | `Text` | `=RelativeDay(ThisItem.'Update Date') & " · " & Lower(ThisItem.'Update Type'.Value) & " · " & Coalesce(LookUp(colPeople, Email = ThisItem.'Created By Entra ID').Name, ThisItem.'Created By Entra ID')` |
| | `Size` / `Color` | `=SizeMeta` / `=ClrTextFaint` |

That byline renders UPD-001 as "Today · voice update · Don Mishory", matching the mockup
— `Update Type` already holds "Voice update", so no special-casing is needed.

`Risk / Decision` isn't in the mockups. UPD-001 is tagged `Risk`, and a status feed that
can't show which updates are risks is a feed people skim past. Delete the two controls if
you want the mockup exactly.

## `cardHistory` — `galHistory`

| Property | Formula |
|---|---|
| `Items` | `=colHistory` |
| `TemplateSize` | `=64` |

| Control | Property | Formula |
|---|---|---|
| `lblVersion` | `Text` | `="Version " & ThisItem.'Version Number' & If(ThisItem.'Is Current'.Value = "Yes", " · current", "")` |
| | `FontWeight` / `Color` | `=FontWeight.Semibold` / `=If(ThisItem.'Is Current'.Value = "Yes", ClrText, ClrTextMuted)` |
| `lblVersionMeta` | `Text` | `=RelativeDay(ThisItem.'Refreshed Date')` |
| | `Size` / `Color` | `=SizeMeta` / `=ClrTextFaint` |
| `recVersionDivider` | `Y` / `Height` / `Fill` | `=Parent.TemplateHeight - 1` / `=1` / `=ClrDivider` |
| (template) | `OnSelect` | `=Set(gblOverview, ThisItem)` |

Selecting a version displays it in the overview card. It doesn't make it current — the
app doesn't write to this list at all. `OnVisible` resets to the current one.

This whole card is read-only display over rows the AI already wrote, so it costs nothing
to keep. Delete it if you'd rather the workspace showed only the current narrative.

---

## The edit panel

One slide-over, four modes. `gblPanel` holds which: `"pursuit"`, `"action"`, `"doc"`,
`"update"`, or `""` for closed. `gblEditKey` holds the `ACT-nnn` / document title /
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
| Documents card | `btnAddDoc` | blank document link |
| Documents gallery | `btnDocEdit` | that document |
| Updates card | `btnAddUpdate` | blank update |
| Updates gallery | `btnUpdateEdit` | that update |

Every one of those handlers does the same three things: set the mode, set `gblEditKey`,
set the record global (`gblEditAction` / `gblEditDoc` / `gblEditUpdate`), then `Reset()`
every input in that mode.

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

**Document** — Title, Document Type, Document URL, Include in AI Overview. `Document ID`,
`Added Date` and `Added By Entra ID` are set on create.

**Update** — Update Text, Update Type, Risk / Decision. `Update Date` and
`Created By Entra ID` are set on create and left alone on edit, so editing a typo doesn't
re-date the entry.

Owner fields are plain text inputs rather than people pickers. The columns hold email
strings, not Person values, so a combo box would mean converting between a user record and
an address in both directions for no gain.

### Saving

`btnPanelSave.OnSelect` is one `Switch`-shaped `If` over `gblPanel`. Each branch either
`Collect`s (when `gblEditKey = ""`) or `Patch`es, then re-runs the `ClearCollect` for that
list so the card behind the panel is correct before the panel closes.

New IDs follow the existing convention —
`"ACT-" & Text(Max(...) + 1, "000")` over the highest existing three-digit suffix. Same
pattern for `PUR-`, `DOC-` and `UPD-`. It assumes the three-digit format holds; at 999 it
starts colliding.

`DisplayMode` on Save is bound to the one field that can't be empty in each mode — account
and pursuit name, action title, document title, update text — so the button is dead until
the record is viable.

### Deleting

`btnPanelDelete` is visible only for the three child modes and only when editing an
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

