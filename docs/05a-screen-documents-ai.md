# Screen — `scrPursuitDocsAI`

Documents and the AI overview, split off the workspace so neither has to fight for
vertical space.

```
scrPursuitDocsAI
├── nav bar (four tabs)
├── lblBreadcrumb / lblAccount / lblPursuitName
├── LEFT  — cardDocs        btnAddDoc + galDocs, newest change first
└── RIGHT — cardAiCurrent   current overview      (top half)
          — cardAiHistory   previous versions     (bottom half)
   EDIT PANEL               document fields + Delete / Cancel / Save
```

Create a blank screen named exactly `scrPursuitDocsAI`, set `Fill` to `=ClrPage`, paste
`src/yaml/04-PursuitDocsAI.pa.yaml`, then set `OnVisible`:

```powerfx
Set(gblPursuit, LookUp('pursuit-tracker-pursuits', Title = gblPursuitKey));

// Newest change first. Modified, not Added Date -- editing a link's type or URL should
// float it back to the top, which is what "last update" means to whoever asked.
ClearCollect(
    colDocs,
    Sort(Filter('pursuit-tracker-documents', 'Pursuit ID' = gblPursuitKey), Modified, SortOrder.Descending)
);

ClearCollect(
    colHistory,
    Sort(Filter('pursuit-tracker-ai-history', 'Pursuit ID' = gblPursuitKey), 'Version Number', SortOrder.Descending)
);

// Nothing in the app writes this list, so nothing guarantees exactly one current
// version. Prefer the flag, fall back to the highest version number, then to an empty
// record of the right shape so the card renders rather than erroring.
Set(gblOverview, LookUp(colHistory, 'Is Current'.Value = "Yes"));
If(IsBlank(gblOverview), Set(gblOverview, First(colHistory)));
If(IsBlank(gblOverview), Set(gblOverview, LookUp('pursuit-tracker-ai-history', ID < 0)));

Set(gblPanel, "");
Set(gblEditKey, "")
```

## Documents

`galDocs` sorts on `Modified` descending, not `Added Date` — editing a link's type or URL
floats it back to the top, which is what "last updated" means to the person asking.

Each row is title, then `Document Type · updated <date, time>`, then an "Included in AI
overview" line when that flag is set. `Edit` opens the panel; Delete lives inside it.

### On dropping a file

**Canvas apps have no file-drop control, and no way to upload an arbitrary file to a
document library on standard connectors.** The nearest thing is the **Attachments**
control, and it only functions inside an Edit Form's data card bound to a SharePoint list
that has attachments enabled. It does give you a real drag-and-drop target and a file
picker.

The reason this screen doesn't use it is a storage decision, not a technical block:
`pursuit-tracker-documents` holds *links*, and DOC-001 points at a file in your OneDrive.
An Attachments control would store uploads **as attachments on the list item**, so the
library would end up split — some documents linked, some embedded in a list row, none of
them in one place, and none of the embedded ones reachable from Teams or search the way a
library file is.

Three ways to get file upload, worst to best:

- **Attachments control on a Form.** Free, real drop target, but splits your storage as
  above and needs a hand-authored Form data card, which is the one construct in this app
  I've deliberately avoided pasting as YAML.
- **Upload to the SharePoint library from the app.** Needs the file bytes, which means a
  premium connector or a Power Automate flow with the OneDrive/SharePoint connector
  triggered from the app. The connectors are standard; the plumbing isn't trivial.
- **Keep linking.** Put files in the site's document library the normal way — where
  versioning, co-authoring and search already work — and paste the link. It's one extra
  step for the person adding a document and it keeps every file in one findable place.

I'd stay with linking. If you want the drop target anyway, say so and I'll build the Form
and Attachments card, with the storage split documented.

## AI overview

The top card is whatever `gblOverview` points at — normally the version flagged
`Is Current`, falling back to the highest `Version Number`. The stamp line above it reads
`Version 3 · Aug 6, 2026 · 2:14 PM`.

The bottom card lists **every other** version:

```powerfx
Sort(
    Filter(colHistory, IsBlank(gblOverview) || Title <> gblOverview.Title),
    'Version Number',
    SortOrder.Descending
)
```

Each row is the version and timestamp, plus a two-line abstract — `Clip(..., 150)` of the
overview text, which at this width and `SizeBody` fills two lines and ellipses. Selecting
a row swaps it into the card above; it doesn't change which version is current, because
reading an old version shouldn't rewrite the record. Leaving the screen resets to current.

Both cards are read-only. SharePoint's native AI writes this list — see
`docs/07-gaps-and-decisions.md`.
