# Pursuit Tracker

A Power Apps canvas app over the five `pursuit-tracker` SharePoint lists on
[PursuitTracking](https://westmonroepartners1.sharepoint.com/sites/PursuitTracking),
built to the three screen mockups: portfolio board, portfolio list, pursuit workspace.

Everything here stays on standard connectors — SharePoint, Office 365 Users, OneDrive
for Business — so it needs no app registration, no admin consent, no premium licence,
and no IT involvement.

This repo is the build specification, not the app. Canvas apps live in Power Platform;
what's version-controlled here is the data contract, the full Power Fx for every screen,
the theme, and the flow definition. The app gets assembled in Power Apps Studio from
these.

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
| `src/yaml/TopNav.pa.yaml` | The nav bar as code-view YAML. Paste onto each screen |
| `tools/dump-list-schema.js` | Browser-console script that dumps your real list schemas |

## Read this before you start

**Four SharePoint column changes come first**, listed at the bottom of
`docs/01-data-model.md`. The blocking one: `Overview Text` is a 255-character Text
column and your mockup's overview is about 430 — SharePoint truncates rather than
erroring, so it destroys content silently. The other three (multi-select SIs and
hyperscalers, defined choice values, deciding what `Active` means) are the difference
between matching the mockups and approximating them.

**The five list titles are inferred from your export filenames**, not confirmed against
the site. Check them and find-and-replace across `docs/` and `src/` if they differ. The
column names are read from the real schema and are correct.

**Three things in the mockups can't be built this way.** Drag-and-drop doesn't exist in
canvas apps, galleries can't scroll horizontally, and generating the AI overview needs a
model connector that is premium in every form. Each has a worked-around alternative in
`docs/07-gaps-and-decisions.md`. The workarounds are in the build; nothing is left
half-specified.

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
