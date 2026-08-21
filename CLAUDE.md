# Pursuit Tracker — working agreement

A Power Apps **canvas app** over SharePoint lists on
`https://westmonroepartners1.sharepoint.com/sites/PursuitTracking`, maintained as source in
this repo. Read this before touching anything; most of it is knowledge that cost a broken
paste to learn.

---

## 1. What this repo actually is

This repo is **not** an app you can run. It is the source of an app that lives in Power Apps
Studio. A `.msapp` cannot be produced from this environment — packing one needs the Power
Platform CLI, and hand-forging the archive fails Studio's internal checksums. So the
deliverable is always **text the user pastes into Studio**:

| File | Pastes into |
|---|---|
| `src/App.Formulas.powerfx` | App → **Formulas** (named formulas + UDFs; the whole theme) |
| `src/App.OnStart.powerfx` | App → **OnStart** |
| `src/screens/scr*.OnVisible.powerfx` | that screen's **OnVisible** |
| `src/yaml/0*-*.pa.yaml` | right-click the screen → **Paste** (code-view YAML) |

Five screens: `scrPortfolioBoard`, `scrPortfolioList`, `scrPursuitWorkspace`,
`scrPursuitDocsAI`, `scrMyActions`. `docs/00-QUICKSTART.md` is the twelve-file paste map;
`docs/01`–`09` carry the reasoning. `tools/validate-screens.py` is the only automated check
that exists.

The nav bar is duplicated on every screen, so **adding a screen means repasting all of
them** — or pasting the one new nav button onto each by hand.

**Every change ends with: what to repaste, and where.** A commit the user can't act on is
not a delivered change.

---

## 2. Settled decisions

Decided as of August 2026, with the workarounds already built. Don't reopen any of these
casually. If you have specific evidence the platform has changed, say so once and move on.

- **No IT involvement.** No Entra app registration, no admin consent, no premium licence.
  Standard connectors only: SharePoint, Office 365 Users, OneDrive for Business. This is why
  it's a canvas app and not a local SPA — the SharePoint scopes a SPA needs stopped being
  user-consentable in July 2025.
- **The AI overview is display-only.** SharePoint's native AI writes `Overview Text`; the app
  renders it. No Refresh button, no generation call.
- **Drag-and-drop and horizontally scrolling galleries don't exist in canvas apps.** Both
  mockup features have shipped alternatives — see `docs/07-gaps-and-decisions.md`.

---

## 3. Workflow

1. **Pull current code from GitHub, not from memory.** The user edits screens directly in
   Studio and pushes the result. Assume every file has moved since you last saw it. Read the
   file before editing it, every time.
2. If the user pastes a screen back at you, **that version is the source of truth** — merge
   your change into theirs, don't overwrite with yours.
3. `python3 tools/validate-screens.py` **must** print 0 errors and 0 warnings before every
   commit. It catches four classes of failure that otherwise only surface as a rejected paste
   in Studio. Any new named formula or UDF goes in its `KNOWN_GLOBALS`.
4. Update `docs/` in the same commit when behaviour changes. The docs are the fallback when a
   paste is rejected, so they can't drift.
5. Branch `claude/pursuit-tracker-local-app-bof6aq` unless told otherwise. Never open a PR
   unless asked outright.

### When the user pastes YAML back

Studio's clipboard sometimes emits a `Screens: / <name>: / Children:` wrapper. The repo
stores the **flat control-list** form (a top-level YAML sequence of `- controlName:` maps).
Normalise before committing, or the validator reads 0 controls and passes vacuously.

### Tone

Terse. The user has said, verbatim: *"I don't need the verbose explanations. Just the bug
fixes."* Lead with the fix and the paste target. Explain a decision only when it changes what
they'd do. No preamble, no recap.

---

## 4. Power Apps `.pa.yaml` — the rules that break pastes

- **No comments in a `.pa.yaml` file. None.** PyYAML skips them, Studio does not: a `#`
  line containing `": "` comes back as `PA1001 YamlInvalidSyntax: While scanning a
  multiline plain scalar, found invalid mapping` and the whole paste is rejected. Every
  screen file is now a bare control list; the commentary that used to live in the headers
  is in `docs/`. The validator errors on the first comment line it finds.
- **Document order is z-order.** The last control declared renders on top and captures the
  pointer. **Anything clickable must be declared after everything it overlaps.** Half the
  "the button doesn't work" bugs in this project were this.
- **`Classic/` prefix is mandatory** for `Button`, `TextInput`, `DropDown`, `ComboBox`,
  `DatePicker`. Unprefixed names resolve to modern Fluent controls with entirely different
  property sets, and the paste fails on the first property they don't have.
- **`Classic/Button` with `Text: =""` is the rounded-rectangle primitive.** It is the only
  classic control with `Radius*` properties, so every card, panel and chip in this app is one.
- **One version per control type.** `Classic/DropDown@2.2.0` on the filter row and
  `Classic/DropDown@2.3.1` in a panel copied from another screen is `PA2107 Another
  instance of control type 'X' has already been referenced using a different version`, and
  the paste dies. Every dropdown in this app is `@2.3.1` with `Items.Value: =Value`; the
  validator errors on a second version of any type in a file.
- **A bound `Classic/ComboBox` needs `DisplayFields` and `SearchFields`**, both `=["Value"]`.
  Without them the paste succeeds, `Items` is ignored, and the control renders the built-in
  sample list — `Item 1`, `Item 2`, … — in the published app. `Classic/DropDown` wants the
  same thing spelled differently: `Items.Value: =Value`.
- **A property may appear once.** A duplicate key is `PA1001 YamlInvalidSyntax: Duplicate
  name 'Color'` and kills the whole screen. PyYAML silently keeps the last one, which is why
  the validator installs a `StrictLoader`.
- **Every property value is a formula string starting with `=`** (except `Control`, `Variant`,
  `Layout`, `MetadataKey`, `IsLocked`, `Group`, `ComponentName`).
- **`PA2108 Unknown property 'X' for control type 'Y'`** kills the whole screen too. Known
  traps, tracked in the validator's `FORBIDDEN` map:
  - `HtmlViewer` has **no** `VerticalAlign`, `Wrap`, `Align`, `FontWeight`, `Underline`, `Text`.
  - `RichTextEditor` has **no** `VerticalAlign`, `Wrap`, `Align`, `Text`, `Mode`, `Size`,
    `Color`, `Font`, `Fill`, `BorderColor`.
- **Labels do not clip.** A Label whose text needs more room than its `Height` allows keeps
  rendering — and with the default `VerticalAlign.Middle` it spills out of *both* ends onto
  the controls above and below. The designer draws bounds; the player draws text, so this is
  invisible in edit mode and obvious in run mode. Two separate bugs here were this. Use
  `Clip(text, n)`, top-align, and size the label off its neighbours rather than guessing.
- **`TabIndex` defaults to 0, meaning z-order.** Any positive value sorts ahead of every zero,
  so setting it on some controls and not others scrambles the tab order. `-1` removes a
  control from the tab order entirely.
- **Deleting a control in Studio leaves every reference to it behind**, and the formula that
  read it silently stops working. `drpUpdType`/`drpUpdRisk` were deleted from the canvas while
  `btnPanelSave` still wrote them, which broke saving updates with no error. The validator now
  treats dangling `btn|lbl|drp|txt|dte|cmb|rte|gal|rec|card|htm|nav` references and orphaned
  `lblCap<control>` captions as errors.

---

## 5. Power Fx notes specific to this app

- **No regex replace exists.** String surgery is `Split` + `ForAll(Sequence(...))` + `Concat`
  (see `DropDecl` in `App.Formulas.powerfx`).
- **`ShowColumns` on a SharePoint list rejects most column sets.** Use
  `ForAll(source As X, { Col: X.Field })` instead.
- **One type error kills the entire behaviour formula.** `btnPanelSave.OnSelect` has three
  branches; a bad Choice write in the pursuit branch made all three do nothing, silently.
  After every write, check `Errors(list)` and `Notify` the first message.
- **Choice columns patch as `{ Value: "x" }`**; MultiChoice as tables of those.
- **A Choice column with an empty `<CHOICES/>` set never reaches the Power Apps schema** and
  every reference to it errors with `Name isn't valid`.
- **`colStages` is a literal 6-row table**, not `Choices(...)`. Three writes disagreeing on the
  inferred type produced "Incompatible type"; the literal ends the argument. The `Choices()`
  version is kept commented in `App.OnStart.powerfx`.
- **`colLookups` loads last in `OnStart`, wrapped in `IfError`** — a failure there used to take
  the whole startup down and publish a blank board.
- **A gallery cannot bind to a SharePoint view.** There is no `Views()` in Power Fx. Filter in
  the app.
- **Collections can be stale-but-present in Studio and empty at runtime.** If something renders
  in Run mode but is blank when published, the screen is missing its `OnVisible` load.

### SharePoint document library quirks

- `Name` has **no** extension; `'{FilenameWithExtension}'` does. Type detection uses
  `EndsWith('{FilenameWithExtension}', ".docx")`, not `Split(name, ".")` — `Split` doesn't name
  its column `Result`, and that error surfaces as a silently blank label.
- Documents live in a per-pursuit folder named for the Pursuit ID (`PUR-014`), created by a
  Power Automate flow. Gallery filter: `"/" & gblPursuitKey & "/" in 'Folder path'`.
- `Forms/AllItems.aspx?FilterField1=...` takes the **internal** column name; an unrecognised one
  fails the whole view render ("Unknown render failure"). Link to the folder instead.
- Columns with spaces need quotes: `'Pursuit ID'`, not `PursuitID`.

---

## 6. Design system

Every colour, size and spacing value is a named formula in `src/App.Formulas.powerfx`. Read
them there — they are the source of truth and this file would only drift from them. **Never
hardcode a colour or a font size in a screen.** The theme is dark.

Standing UI conventions the user has asked for explicitly:

- Every label and button is **Title Case**, unless it is already ALL CAPS (field captions).
- Add buttons are a **`+`**; delete buttons are a **trash can icon**. No text buttons for either.
- Galleries that can change get a **refresh icon** next to the `+`.
- Multi-line inputs are sized off `Parent.Height`, not pinned, so they fill the panel.
- Pursuit identity always renders as `PUR-014 - Dynamics F&O` via `PursuitLabel(id, name)`.
- Workspace right column is **2/3 latest update, 1/3 previous updates**; left column is
  details over actions.
- Pasted rich text is normalised **at display time** by `StatusHtml()` — white body at
  `SizeBody`, headings bold at `SizeBody + 2`. Stored HTML is never rewritten.

---

## 7. Data model

Six SharePoint lists/libraries: `pursuit-tracker-pursuits`, `-actions`, `-status-updates`,
`-documents` (links only), `-ai-history`, `-lookups`, plus the **`Pursuit Documents`** library.
Column-by-column detail is in `docs/01-data-model.md` — trust that file and the user's CSV
exports over anything remembered.

`pursuit-tracker-lookups` drives every edit dropdown: rows are `Title` (the lookup type),
`Value`, `Sort Order`. `colLookups` reshapes it to `{ LookupType, Value }`.

Known data problems live in **`docs/OPEN-ITEMS.md`**. They are the user's to fix in
SharePoint — don't work around them in code.
