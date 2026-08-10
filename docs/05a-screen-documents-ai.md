# Screen — `scrPursuitDocsAI`

Documents and the AI overview, split off the workspace so neither has to fight for
vertical space.

```
scrPursuitDocsAI
├── nav bar (four tabs)
├── lblBreadcrumb / lblAccount / lblPursuitName
├── LEFT  — cardDocs        the Pursuit Documents library, filtered by pursuit (top half)
│         — cardLinks       pursuit-tracker-documents, the link list      (bottom half)
└── RIGHT — cardAiCurrent   current overview, rich text   (top two-thirds)
          — cardAiHistory   previous versions             (bottom third)
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

## Documents and Links are two different stores

**Documents** is the `Pursuit Documents` **library**, read directly. Files live in a folder
named for the pursuit — `PUR-014` — created by a flow, so the filter is on where the file
sits rather than on a column of the item:

```powerfx
Sort(
    Filter('Pursuit Documents', "/" & gblPursuitKey & "/" in 'Folder path'),
    Modified,
    SortOrder.Descending
)
```

`in` is a substring test, so it doesn't delegate — SharePoint returns the library and the
match happens in memory. Fine at this size, and it dodges having to reconstruct the exact
server-relative path, which differs between the display name and the URL.

The folder rows themselves don't appear: a folder sits in the library root, so its own
`Folder path` doesn't contain `/PUR-014/`. No `IsFolder` filter needed.

### There is no way to bind a SharePoint view

The connector exposes the library and its columns. Views are a SharePoint page construct —
there's no `Views(...)` in Power Fx and no gallery property that takes one. A view's column
choice, sort and filter have to be rebuilt in the gallery, which is what the row below is.

### The row

Type badge, file name, and who touched it:

| | |
|---|---|
| `recDocType` + `lblDocType` | file-type chip: coloured outline, white letters |
| `lblDocName` | `Name`, link-coloured |
| `lblDocModified` | `Modified`, right-aligned |
| `lblDocWho` | `Created by … · Modified by …` from the two Person columns |

### The file-type chip

An outlined chip, white text, coloured border by extension:

| | | |
|---|---|---|
| `.doc` `.docx` | `W` | blue |
| `.ppt` `.pptx` | `PPT` | orange |
| `.xls` `.xlsx` `.csv` | `XL` | green |
| `.msg` `.eml` | `E` | yellow |
| `.pdf` | `PDF` | red |
| anything else | `O` | white |

Both the letter and the border are an `If` chain of `EndsWith()` against
`ThisItem.'{FilenameWithExtension}'`, written inline on the two controls.

Two things had to be got right, and I got both wrong first:

**`Name` doesn't carry the extension.** The connector exposes the leaf name without it, so
anything parsing `Name` classifies every file as "other". `{FilenameWithExtension}` is the
column that has the suffix. `Name` is still what the row *displays* — the extension is
already in the chip.

**`EndsWith`, not `Split`.** `Lower(Last(Split(name, ".")).Result)` assumes `Split` names its
output column `Result`. Get that wrong and the whole expression is an error: the label
renders **blank** and the border quietly falls back to a default, which reads as "the chip
half works" rather than as a broken formula. `EndsWith` is case-insensitive and has no
intermediate table to name.

Text rather than a real file-type icon: canvas apps have no icon set for document types,
and the alternatives — an image per extension, or the library's `{Thumbnail}` — mean either
bundling assets or a per-row image fetch.

No collection behind it — it holds files, nothing in the app writes to it, and there's no
join to build, so there's nothing to refresh after a save. Clicking a row opens the file
through `ThisItem.'Link to item'`.

**Add document** leaves the app: `Launch(SiteUrl & "/Pursuit Documents")`.

It opens the library plainly, with no view filter. `Forms/AllItems.aspx?FilterField1=…` is
the documented way to filter a view by URL and it takes the column's **internal** name, not
its display name — a name SharePoint doesn't recognise doesn't filter to nothing, it fails
the whole view render: *"Unknown render failure. The specified view might have been
deleted."* A plain library link can't break that way.

That is as close to "a new record with the pursuit id prepopulated" as a document library
gets. **A library row can't exist before its file does**, so there is no new-item form to
prefill — the upload creates the row. Two ways to get the `PursuitID` filled without typing
it, both configured in SharePoint rather than here:

The column is `Pursuit ID`, with a space, so it needs the single quotes — the same
convention every other list in this app uses for its key column.

- **Column default value** on a per-folder basis (Library settings → Column default value
  settings). One folder per pursuit, each defaulting `Pursuit ID` to that pursuit. The upload
  then carries the right value with no user action. Change the `Launch` URL to point at the
  folder rather than the filtered view.
- **A Power Automate flow** on "when a file is created", reading the pursuit from the folder
  path or from a prompt.

Without one of those, whoever uploads has to set `Pursuit ID` on the item afterwards or the
document won't appear in the app.

### Refresh

Each card has a `↻` beside its `+`.

**Documents needs it.** Adding a document leaves the app for SharePoint, and coming back to
a browser tab that never lost focus doesn't re-run `OnVisible` — the gallery keeps showing
what the connector cached. `Refresh('Pursuit Documents')` drops that cache and re-queries.

**Links doesn't, strictly.** Saving or deleting a link already rebuilds `colLinks` in
`btnPanelSave` and `btnPanelDelete`, so the list is current after anything done in the app.
Its `↻` is there for changes someone else made to the list while the screen was open.

**Links** is the `pursuit-tracker-documents` list, unchanged — title, type, URL, and the
"included in AI overview" flag, with the same add/edit/delete panel it always had. The two
are separate on purpose: a link to a file in someone's OneDrive and a file in the site
library are different things, and merging them would mean one of them lying about where it
lives.

## Links

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
