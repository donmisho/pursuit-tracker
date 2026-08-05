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

## 6. Paste the nav bar onto each screen

`src/yaml/TopNav.pa.yaml` is the shared header, as Power Apps code-view YAML.

1. Open `scrPortfolioBoard`, right-click the screen in the tree view → **Paste** (or
   Ctrl+V with the YAML on your clipboard). Studio validates the YAML and builds the
   controls.
2. Repeat on the other two screens.
3. On each screen, set the `Fill` of the tab that represents *that* screen to
   `=ClrAccent` — that's the selected-tab state in the mockups. The YAML ships with
   `scrPortfolioBoard` selected.

If a paste is rejected, build the nav manually from the property table at the bottom of
that file and move on — the YAML is an accelerator, not a dependency. Studio only
accepts YAML in the exact shape it generates itself, and control versions shift between
releases.

## 7. Then build the screens

In order, because each depends on state the previous one sets:

1. `docs/03-screen-portfolio-board.md`
2. `docs/04-screen-portfolio-list.md`
3. `docs/05-screen-pursuit-workspace.md`
4. `docs/06-flows.md` — the Excel export, once the list screen exists

## A note on how the screen docs are written

Each gives you a control tree and a table of **every non-default property**, keyed to
control name. Properties not listed keep their Power Apps defaults.

I've written them as formula references rather than as more pasteable YAML on purpose.
Chrome — bars, headers, card frames — pastes reliably. Galleries don't: their YAML
carries template metadata and a `Variant` string that changes between Studio releases,
and a rejected paste on a nested gallery costs more time to unpick than building the
two galleries by hand. The formulas are the part that's hard to get right, and they
paste into a property box perfectly.
