# Setup — from empty app to wired shell

Roughly 30 minutes. Nothing here needs an admin.

## 1. Confirm you're on the free path

Build the app from <https://make.powerapps.com> in your **default environment**. The
SharePoint connector is a standard connector, so a canvas app that touches only
SharePoint (plus Office 365 Users, also standard) is covered by your existing M365
licence with no per-user Power Apps cost.

The moment you add a premium connector — SQL, Dataverse, HTTP, Azure OpenAI, any custom
connector — every user of the app needs a paid Power Apps licence. That constraint
shapes two decisions later: the Excel export (`docs/06-flows.md`) and the AI overview
refresh (`docs/07-gaps-and-decisions.md`). Both are built to stay on the free side of
that line.

## 2. Create the app

**Create → Blank app → Blank canvas app**, name it `Pursuit Tracker`, format **Tablet**.

Then, before anything else, **Settings → Display → turn off "Scale to fit"**. The
mockups are a dense information layout; with scaling on, Power Apps letterboxes the app
and the board columns end up floating in grey bars on a wide monitor.

While you're in Settings:

- **General → Data row limit: 2000** (the maximum). Default is 500, and it silently
  truncates. See the delegation note in `docs/07-gaps-and-decisions.md`.
- **Upcoming features → Named formulas: on.** Required — the theme in
  `src/App.Formulas.powerfx` is built on them.
- **Upcoming features → User-defined functions: on.** Also required. The three helpers
  at the bottom of the theme file (`StageAccent`, `DueLabel`, `RelativeDay`) take
  parameters, which makes them user-defined functions rather than plain named formulas.
  With the toggle off, Studio rejects the whole `Formulas` property — including the
  colours — and it isn't obvious that three lines at the bottom are the cause.

## 3. Add the five data sources

**Data → Add data → SharePoint → your connection →**
`https://westmonroepartners1.sharepoint.com/sites/PursuitTracking`, then select all
five `pursuit-tracker-*` lists at once.

**Office 365 Users is required, not optional.** The owner columns hold email strings
rather than Person values, so there is no display name in the data — every "Don Mishory"
in the UI comes from resolving `dmishory@westmonroe.com` through this connector at load.
It's a standard connector, so it costs nothing.

Every formula in `docs/03`–`05` refers to the lists as `'pursuit-tracker-pursuits'`,
`'pursuit-tracker-actions'`, `'pursuit-tracker-status-updates'`,
`'pursuit-tracker-documents'`, and `'pursuit-tracker-ai-history'` — confirmed titles, so
they should bind on the first try.

The schema changes the app depends on are already applied (`docs/01-data-model.md`). The
one that will still surprise you: `Active` is a Number reading `0` on every row, so the
board shows all fourteen pursuits including the three `Unassigned` ones. That's
deliberate, not a bug.

## 4. Paste the theme

Tree view → **App** → `Formulas` property → paste all of
`src/App.Formulas.powerfx`.

Then **App** → `OnStart` → paste all of `src/App.OnStart.powerfx`.

Right-click App → **Run OnStart** so the collections exist while you build. You'll want
to re-run it after any change to the SharePoint schema.

## 5. Create the three screens

Add three blank screens and rename them exactly:

| Screen | Mockup |
|---|---|
| `scrPortfolioBoard` | Portfolio board — the kanban |
| `scrPortfolioList` | Portfolio list — the reportable table |
| `scrPursuitWorkspace` | Pursuit workspace — the detail page |

Set **App → StartScreen** to `=scrPortfolioBoard`.

On each screen set `Fill` to `=ClrPage`. If the screen stays white, named formulas
aren't switched on yet — go back to step 2.

## 6. Paste the three screens

`src/yaml/` holds each screen as complete Power Apps code-view YAML — every control,
positioned, with every formula. 153 controls across the three files.

For each screen in turn:

1. Open the file, select all, copy.
2. In Studio, right-click the matching screen in the tree view → **Paste**. The first
   paste triggers a browser clipboard-permission prompt; approve it.
3. Set the screen's `Fill` to `=ClrPage`.
4. Set the screen's `OnVisible` — the comment block at the foot of each YAML file says
   which one, and `docs/03`–`05` carry the formulas.

| File | Screen | Controls |
|---|---|---|
| `01-PortfolioBoard.pa.yaml` | `scrPortfolioBoard` | 30 |
| `02-PortfolioList.pa.yaml` | `scrPortfolioList` | 33 |
| `03-PursuitWorkspace.pa.yaml` | `scrPursuitWorkspace` | 90 |

The nav bar is included in all three files rather than pasted separately, so each screen
is one paste. The selected-tab styling is already set per screen.

### If a paste is rejected

Studio only accepts the exact YAML shape its own code view emits, and that shape moves
between releases — I can't verify a paste from outside Power Apps, so treat this as an
accelerator with a known fallback rather than a guarantee. Each file ends with a
FALLBACKS note naming the two controls most likely to be the cause. Beyond those,
`docs/03`–`05` carry every control and formula as property tables, which always work:
insert the control by hand and paste the formulas into the property box.

Two things worth knowing before you paste:

**Set App.Formulas and App.OnStart first** (step 4). Nearly every property here resolves
through a theme token — a screen pasted before the theme exists shows a wall of red
errors that all disappear once the tokens are defined.

**Create all three screens first** (step 5). The nav buttons navigate by screen name, and
a `Navigate()` to a screen that doesn't exist is an error Studio can't resolve.

## A note on how the screen docs are written

`docs/03`–`05` give each screen as a control tree plus a table of **every non-default
property**, keyed to control name. Properties not listed keep their Power Apps defaults.

They exist alongside the YAML rather than being replaced by it. The YAML is faster when
it works; the tables always work, and they carry the reasoning — why the board sorts on a
substituted date, why `ShowColumns` wraps `AddColumns` in the export, why the at-risk pill
reads `Health` and not `Status`. Read the tables when something looks wrong; paste the
YAML when you just want the screen on the canvas.
