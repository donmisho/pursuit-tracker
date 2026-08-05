# Screen — `scrPursuitWorkspace`

The detail page. Two columns: a wide left rail (Salesforce, AI overview, actions) and a
narrower right rail (alignment, documents, updates, overview history).

```
scrPursuitWorkspace
├── [TopNav.pa.yaml]
├── lblBreadcrumb / lblTitle / lblSubtitle
├── btnAddTask / btnAddUpdate
├── LEFT RAIL
│   ├── cardSalesforce   — link, sync pill, owner, target close
│   ├── cardOverview     — AI overview text, Refresh, provenance line
│   └── cardActions      — galTasks
└── RIGHT RAIL
    ├── cardAlignment    — galAlignSIs, galAlignHype, + Other
    ├── cardDocuments    — galDocs
    ├── cardUpdates      — galUpdates
    └── cardHistory      — galHistory
```

Every card is a Rectangle (`Fill = ClrCard`, `BorderColor = ClrBorder`,
`BorderThickness = 1`, all `Radius* = RadiusCard`) with a heading Label at
`Size = SizeCardTitle`, `FontWeight = Semibold`, `Color = ClrText`.

Left rail `X = GapPage`, `Width = 640`. Right rail `X = 688`, `Width = 400`.

---

## Screen

| Property | Formula |
|---|---|
| `Fill` | `=ClrPage` |
| `OnVisible` | below |

```powerfx
Set(gblPursuit, LookUp('pursuit-tracker-Pursuits', ID = gblPursuitId));

ClearCollect(
    colTasks,
    SortByColumns(
        Filter('pursuit-tracker-Tasks', PursuitKey = gblPursuitId),
        "DueDate", SortOrder.Ascending
    )
);
ClearCollect(
    colUpdates,
    SortByColumns(
        Filter('pursuit-tracker-Updates', PursuitKey = gblPursuitId),
        "UpdateDate", SortOrder.Descending
    )
);
ClearCollect(
    colDocs,
    SortByColumns(
        Filter('pursuit-tracker-Documents', PursuitKey = gblPursuitId),
        "SortOrder", SortOrder.Ascending
    )
);
ClearCollect(
    colHistory,
    SortByColumns(
        Filter('pursuit-tracker-AIOverviews', PursuitKey = gblPursuitId),
        "VersionNumber", SortOrder.Descending
    )
);
Set(gblOverview, LookUp(colHistory, IsCurrent = true));

// Panel state — both editors start closed.
Set(gblPanel, "");
```

Filtering on `PursuitKey` rather than `Pursuit.Id` is the delegation decision from
`docs/01-data-model.md`. With the lookup form, SharePoint returns the first 500 rows of
the *whole* list and filters locally, so a pursuit's tasks quietly disappear once the
Tasks list passes 500 items across all pursuits.

## Header

| Control | Property | Formula |
|---|---|---|
| `lblBreadcrumb` | `Text` | `=gblPortfolio & " / " & gblPursuit.ShortName` |
| | `Size` / `Color` | `=SizeBody` / `=ClrTextFaint` |
| `lblTitle` | `Text` | `=gblPursuit.Title` |
| | `Size` / `FontWeight` / `Color` | `=SizePageTitle` / `=FontWeight.Semibold` / `=ClrText` |
| `lblSubtitle` | `Text` | `="Pursuit details are supplied from Salesforce."` |
| | `Size` / `Color` | `=SizeBody` / `=ClrTextMuted` |
| `btnAddTask` | `Text` | `="Add task"` |
| | `Fill` / `Color` / `BorderColor` / `BorderThickness` | `=ClrCard` / `=ClrText` / `=ClrBorder` / `=1` |
| | `OnSelect` | `=Set(gblPanel, "task"); Reset(txtTaskTitle)` |
| `btnAddUpdate` | `Text` | `="Add update"` |
| | `Fill` / `Color` | `=ClrAccent` / `=ClrAccentText` |
| | `OnSelect` | `=Set(gblPanel, "update"); Reset(txtUpdateBody)` |

## `cardSalesforce`

| Control | Property | Formula |
|---|---|---|
| `lnkSfOpp` (Label) | `Text` | `=gblPursuit.SalesforceOpportunityName` |
| | `Color` / `Underline` | `=ClrLink` / `=true` |
| | `DisplayMode` | `=If(IsBlank(gblPursuit.SalesforceOpportunityUrl), DisplayMode.View, DisplayMode.Edit)` |
| | `OnSelect` | `=Launch(gblPursuit.SalesforceOpportunityUrl)` |
| `lblSfHint` | `Text` | `="Synced CRM information: account, opportunity owner, amount, close date, and stage"` |
| | `Size` / `Color` / `Wrap` | `=SizeMeta` / `=ClrTextFaint` / `=true` |
| `recSyncPill` | `Fill` | `=If(gblPursuit.SalesforceSyncStatus.Value = "Synced", ClrOkFill, ClrChip)` |
| | all `Radius*` | `=RadiusChip` |
| `lblSyncPill` | `Text` | `=gblPursuit.SalesforceSyncStatus.Value` |
| | `Color` | `=If(gblPursuit.SalesforceSyncStatus.Value = "Synced", ClrOkText, ClrChipText)` |
| `lblOwnerCap` | `Text` | `="PURSUIT OWNER"` — `Size = SizeMeta`, `Color = ClrTextMuted` |
| `cirOwner` + `lblOwnerInitials` | | same pattern as the board card |
| `lblOwnerName` | `Text` | `=gblPursuit.PursuitOwner.DisplayName` |
| `lblOwnerOrg` | `Text` | `="West Monroe · Entra ID"` — `Size = SizeMeta`, `Color = ClrTextFaint` |
| `lblCloseCap` | `Text` | `="TARGET CLOSE"` |
| `lblCloseDate` | `Text` | `=Text(gblPursuit.TargetCloseDate, "mmmm d")` |
| | `Size` / `FontWeight` / `Color` | `=SizeCardTitle` / `=FontWeight.Semibold` / `=ClrText` |

## `cardOverview`

| Control | Property | Formula |
|---|---|---|
| `lblOverviewHead` | `Text` | `="AI overview"` |
| `btnRefreshOverview` | `Text` | `="Refresh overview"` |
| | `Fill` / `Color` | `=ClrAccent` / `=ClrAccentText` |
| | `OnSelect` | see below |
| `lblOverviewBody` | `Text` | `=Coalesce(gblOverview.OverviewText, "No overview has been generated for this pursuit yet.")` |
| | `Size` / `Color` / `Wrap` / `AutoHeight` | `=SizeBody` / `=ClrText` / `=true` / `=true` |
| `lblOverviewMeta` | `Text` | `="Current version refreshed " & Lower(RelativeDay(gblOverview.GeneratedDate)) & " from " & gblOverview.SourceSummary & " · Prior versions retained in history"` |
| | `Size` / `Color` / `Wrap` | `=SizeMeta` / `=ClrTextFaint` / `=true` |

**`btnRefreshOverview` is the one control that can't be finished from inside the free
tier.** Generating the narrative needs a model, and every route to one — AI Builder,
Copilot Studio, the HTTP connector, Azure OpenAI — is premium, admin-gated, or both.
Options are laid out in `docs/07-gaps-and-decisions.md`. The button is wired to the
version-management half of the job, which is the part that has to be right regardless of
where the text comes from:

```powerfx
// Replace the OverviewText value with a call to whatever generates it. Everything
// else here — version numbering, the IsCurrent flip, re-reading history — stands.
With(
    { nextVersion: Coalesce(Max(colHistory, VersionNumber), 0) + 1 },

    // Demote the current version first. If this fails, the Collect below never runs
    // and you're left with one current version rather than two.
    If(
        !IsBlank(gblOverview),
        Patch(
            'pursuit-tracker-AIOverviews',
            LookUp('pursuit-tracker-AIOverviews', ID = gblOverview.ID),
            { IsCurrent: false }
        )
    );

    Collect(
        'pursuit-tracker-AIOverviews',
        {
            Title:          "Version " & nextVersion,
            Pursuit:        { Id: gblPursuitId, Value: gblPursuit.Title },
            PursuitKey:     gblPursuitId,
            VersionNumber:  nextVersion,
            OverviewText:   "TODO: generated narrative",
            IsCurrent:      true,
            GeneratedDate:  Now(),
            SourceSummary:  "Salesforce + " & CountRows(colDocs) & " materials",
            MaterialsCount: CountRows(colDocs)
        }
    )
);
ClearCollect(
    colHistory,
    SortByColumns(Filter('pursuit-tracker-AIOverviews', PursuitKey = gblPursuitId), "VersionNumber", SortOrder.Descending)
);
Set(gblOverview, LookUp(colHistory, IsCurrent = true))
```

The demote-then-insert ordering matters. Reversed, a failure between the two writes
leaves two rows with `IsCurrent = true` and the overview card silently shows whichever
sorts first. Canvas apps have no transactions, so the best available guarantee is to
sequence the writes so the failure mode is recoverable.

## `cardActions` — `galTasks`

| Property | Formula |
|---|---|
| `Items` | `=colTasks` |
| `TemplateSize` | `=56` |

| Control | Property | Formula |
|---|---|---|
| `lblTaskTitle` | `Text` | `=ThisItem.Title` — `FontWeight = Semibold`, `Color = ClrText`, `Wrap = true` |
| `lblTaskPhase` | `Text` | `=ThisItem.Phase.Value` — `Color = ClrTextMuted` |
| `lblTaskEffort` | `Text` | `=ThisItem.Effort.Value` — `Color = ClrText` |
| `recTaskPill` | `Visible` | `=ThisItem.Status.Value in ["At risk", "Blocked"]` |
| | `Fill` / all `Radius*` | `=ClrRiskFill` / `=RadiusChip` |
| `lblTaskPill` | `Text` | `=ThisItem.Status.Value` |
| | `Visible` / `Color` / `Align` | `=recTaskPill.Visible` / `=ClrRiskText` / `=Align.Center` |
| `lblTaskDue` | `Text` | `=DueLabel(ThisItem.DueDate, ThisItem.DueDescription)` |
| | `Visible` / `Color` | `=Not(recTaskPill.Visible)` / `=ClrTextMuted` |
| `recTaskDivider` | `Y` / `Height` / `Fill` | `=Parent.TemplateHeight - 1` / `=1` / `=ClrDivider` |

The pill and the due date occupy the same slot — that's what the mockup shows, with
"Draft executive proposal" displaying its At risk pill where "Confirm buying committee"
shows Aug 12. A task that is both at risk and dated shows the risk, which is the more
urgent of the two facts.

## `cardAlignment`

| Control | Property | Formula |
|---|---|---|
| `lblSICap` | `Text` | `="SYSTEMS INTEGRATORS"` — `Size = SizeMeta`, `Color = ClrTextMuted` |
| `galAlignSIs` | `Items` | `=gblPursuit.AlignedSIs` |
| `lblHypeCap` | `Text` | `="HYPERSCALERS"` |
| `galAlignHype` | `Items` | `=gblPursuit.Hyperscalers` |
| `btnOtherSI` / `btnOtherHype` | `Text` | `="+ Other"` |
| | `Fill` / `Color` / `BorderColor` / `BorderThickness` | `=ClrCard` / `=ClrChipText` / `=ClrBorder` / `=1` |
| | `OnSelect` | `=Set(gblPanel, "alignment")` |

Both galleries: `Layout` Horizontal, `TemplateSize = 76`, `Height = 26`, chip template
as on the board.

## `cardDocuments` — `galDocs`

| Property | Formula |
|---|---|
| `Items` | `=colDocs` |
| `TemplateSize` | `=28` |

`lblDocLink`: `Text = ThisItem.Title`, `Color = ClrLink`, `Underline = true`,
`OnSelect = Launch(ThisItem.Url)`.

In the mockup the three document links run together as one wrapped block
("Working proposal deckDiscovery notesNTT solution outline"). A gallery with one row per
document gives each its own hit target, which is what that layout is reaching for.

## `cardUpdates` — `galUpdates`

| Property | Formula |
|---|---|
| `Items` | `=colUpdates` |
| `TemplateSize` | `=88` |

| Control | Property | Formula |
|---|---|---|
| `lblUpdateBody` | `Text` | `=ThisItem.UpdateText` — `Color = ClrText`, `Wrap = true`, `Height = 44` |
| `lblUpdateMeta` | `Text` | `=RelativeDay(ThisItem.UpdateDate) & If(ThisItem.Source.Value = "Manual", "", " · " & Lower(ThisItem.Source.Value) & " update") & " · " & ThisItem.AuthorName` |
| | `Size` / `Color` | `=SizeMeta` / `=ClrTextFaint` |

That byline reproduces both mockup forms: "Today · voice update · Don Mishory" for a
voice-sourced item, and "Yesterday · Don Mishory" for a typed one, because `Manual`
contributes no middle segment.

## `cardHistory` — `galHistory`

| Property | Formula |
|---|---|
| `Items` | `=colHistory` |
| `TemplateSize` | `=64` |

| Control | Property | Formula |
|---|---|---|
| `lblVersion` | `Text` | `="Version " & ThisItem.VersionNumber & If(ThisItem.IsCurrent, " · current", "")` |
| | `FontWeight` / `Color` | `=FontWeight.Semibold` / `=If(ThisItem.IsCurrent, ClrText, ClrTextMuted)` |
| `lblVersionMeta` | `Text` | `=RelativeDay(ThisItem.GeneratedDate) & " · " & ThisItem.SourceSummary` |
| | `Size` / `Color` | `=SizeMeta` / `=ClrTextFaint` |
| `recVersionDivider` | `Y` / `Height` / `Fill` | `=Parent.TemplateHeight - 1` / `=1` / `=ClrDivider` |
| (template) | `OnSelect` | `=Set(gblOverview, ThisItem)` |

Selecting a version shows it in the overview card. It doesn't make it current — reading
an old version shouldn't rewrite the record. Screen `OnVisible` resets to the current
one.

---

## The Add task / Add update panels

The mockups don't show these open, so this is a judgement call: a right-hand slide-over
rather than a full-screen form, so the pursuit stays visible behind it.

Build both as a Rectangle (`Fill = ClrCard`, `X = Parent.Width - 420`, full height)
with `Visible = gblPanel = "task"` / `= "update"`, over a dimming Rectangle
(`Fill = ColorFade(ClrPage, -0.4)`, `Visible = gblPanel <> ""`,
`OnSelect = Set(gblPanel, "")`).

**Add task** — `txtTaskTitle`, `drpTaskPhase` (`Items = Choices('pursuit-tracker-Tasks'.Phase)`),
`drpTaskEffort`, `dteTaskDue`, `pplTaskOwner` (Combo box,
`Items = Office365Users.SearchUser({searchTerm: Self.SearchText})`).

```powerfx
// btnSaveTask.OnSelect
Collect(
    'pursuit-tracker-Tasks',
    {
        Title:      txtTaskTitle.Text,
        Pursuit:    { Id: gblPursuitId, Value: gblPursuit.Title },
        PursuitKey: gblPursuitId,
        Phase:      { Value: drpTaskPhase.Selected.Value },
        Effort:     { Value: drpTaskEffort.Selected.Value },
        Status:     { Value: "Not started" },
        DueDate:    dteTaskDue.SelectedDate,
        AssignedTo: {
            '@odata.type': "#Microsoft.Azure.Connectors.SharePoint.SPListExpandedUser",
            Claims:      "i:0#.f|membership|" & Lower(pplTaskOwner.Selected.Mail),
            DisplayName: pplTaskOwner.Selected.DisplayName,
            Email:       pplTaskOwner.Selected.Mail,
            Department:  "",
            JobTitle:    "",
            Picture:     ""
        }
    }
);
ClearCollect(colTasks, SortByColumns(Filter('pursuit-tracker-Tasks', PursuitKey = gblPursuitId), "DueDate", SortOrder.Ascending));
Set(gblPanel, "")
```

That `AssignedTo` record shape is not optional decoration. Patching a SharePoint Person
column requires all seven fields including the `@odata.type` tag and the
`i:0#.f|membership|` claims prefix; omit any of them and the write fails with an error
that names neither the column nor the missing field.

**Add update** — `txtUpdateBody` (multiline), `drpUpdateSource`
(`Items = Choices('pursuit-tracker-Updates'.Source)`).

```powerfx
// btnSaveUpdate.OnSelect
Collect(
    'pursuit-tracker-Updates',
    {
        // SharePoint requires Title, so derive one rather than making someone write it.
        Title:      Left(txtUpdateBody.Text, 60) & If(Len(txtUpdateBody.Text) > 60, "…", ""),
        Pursuit:    { Id: gblPursuitId, Value: gblPursuit.Title },
        PursuitKey: gblPursuitId,
        UpdateText: txtUpdateBody.Text,
        Source:     { Value: drpUpdateSource.Selected.Value },
        AuthorName: gblUser.FullName,
        UpdateDate: Now()
    }
);
ClearCollect(colUpdates, SortByColumns(Filter('pursuit-tracker-Updates', PursuitKey = gblPursuitId), "UpdateDate", SortOrder.Descending));
Reset(txtUpdateBody);
Set(gblPanel, "")
```

## New pursuit

`btnNewPursuit` on the board sets `gblNewPursuit` and navigates here with a blank
`gblPursuitId`. Guard the screen so it doesn't try to render a record that doesn't
exist: set `Visible = Not(gblNewPursuit)` on both rails, and show a create panel
(`Visible = gblNewPursuit`) with Title, Account, Stage, Owner, Target close. On save,
`Collect` into `'pursuit-tracker-Pursuits'`, capture the new ID, set `gblPursuitId`, and
set `gblNewPursuit` to false — the rails then populate normally.
