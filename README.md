# Pursuit Tracker

A Power Apps canvas app over the five `pursuit-tracker` SharePoint lists on
[PursuitTracking](https://westmonroepartners1.sharepoint.com/sites/PursuitTracking),
built to the three screen mockups: portfolio board, portfolio list, pursuit workspace.

Everything here stays on standard connectors — SharePoint, Office 365 Users, OneDrive
for Business — so it needs no app registration, no admin consent, no premium licence,
and no IT involvement.

The app is built, as far as anything outside Power Platform can build a canvas app.
`src/yaml/` holds all three screens as Power Apps code-view YAML — 153 controls,
positioned, with every formula — which you paste into Studio one screen at a time. The
theme and startup logic paste into two App properties. `docs/` carries the same thing as
property tables, both as a fallback and as the record of why each formula is what it is.

What can't be produced from here is a `.msapp`: packing one needs the Power Platform CLI,
and this environment has neither the .NET SDK nor network access to install it. Hand-
forging the archive isn't an option either — Studio validates internal checksums, and a
corrupt file is worse than no file.

## Order of work

| | |
|---|---|
| [`docs/01-data-model.md`](docs/01-data-model.md) | The five lists, column by column. **Start here** — reconcile it against your real schema |
| [`docs/02-app-setup.md`](docs/02-app-setup.md) | Create the app, connect the lists, paste the theme, paste the nav bar |
| [`docs/03-screen-portfolio-board.md`](docs/03-screen-portfolio-board.md) | The kanban |
| [`docs/04-screen-portfolio-list.md`](docs/04-screen-portfolio-list.md) | The reportable table and the Excel download |
| [`docs/05-screen-pursuit-workspace.md`](docs/05-screen-pursuit-workspace.md) | The detail page |
| [`docs/06-flows.md`](docs/06-flows.md) | The one Power Automate flow |
| [`docs/07-gaps-and-decisions.md`](docs/07-gaps-and-decisions.md) | Where the mockups and the platform disagree |

## Source

| | |
|---|---|
| `src/App.Formulas.powerfx` | Dark theme as named formulas. Paste into App → Formulas |
| `src/App.OnStart.powerfx` | Startup state and the shared portfolio load |
| `src/yaml/01-PortfolioBoard.pa.yaml` | The kanban as code-view YAML — 30 controls. Paste onto `scrPortfolioBoard` |
| `src/yaml/02-PortfolioList.pa.yaml` | The table and export button — 33 controls |
| `src/yaml/03-PursuitWorkspace.pa.yaml` | The detail page, seven cards and both slide-over panels — 90 controls |
| `tools/validate-screens.py` | Structural check over the screen YAML |
| `tools/dump-list-schema.js` | Browser-console script that dumps your real list schemas |

## Read this before you start

**The schema is confirmed and current.** Column names come from the real list exports,
the five list titles are confirmed, and the four schema changes the mockups needed are
applied. One item is open: `Active` is a Number reading `0` on every row, so the app
doesn't filter on it and the board shows all fourteen pursuits. Both filter variants sit
commented in `src/App.OnStart.powerfx`.

**The AI overview is display-only.** SharePoint's native AI populates the overview text
and its version history; the app reads and renders it, and there's no Refresh button.
That takes the one thing that couldn't be done on standard connectors off the table
entirely.

**Two things in the mockups can't be built this way.** Drag-and-drop doesn't exist in
canvas apps, and galleries can't scroll horizontally. Both have worked-around
alternatives in `docs/07-gaps-and-decisions.md` — the workarounds are in the build,
nothing is left half-specified.

## Why canvas rather than something local

An app registration in Entra was the fork in the road. Even where self-service
registration is permitted, the SharePoint scopes this app needs stopped being
user-consentable when Microsoft reclassified them as high-impact in July 2025 — so a
local SPA would very likely have hit an admin-consent wall after being built. A canvas
app on standard connectors sidesteps that question entirely, and gets shareable with the
rest of the team as a side effect.

The trade is that it doesn't run locally and the UI lands close to the mockups rather
than exactly on them. `docs/07-gaps-and-decisions.md` covers what that costs and what
would change the calculus.
