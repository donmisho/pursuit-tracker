# Gaps and decisions

Where the mockups and the canvas-app platform disagree, and what this build does about
it. Read this before you demo the app to anyone, so nothing here arrives as a surprise
in the room.

---

## 1. There is no drag-and-drop

**Mockup:** "Drag pursuits into the current workflow stage."

**Platform:** Canvas apps have no drag-and-drop. Not a hard one, not an awkward one —
the gesture doesn't exist. Galleries don't expose drag events, and there's no drop
target primitive.

**This build:** a move handle on each card. Press it to pick the card up (the card
outlines in accent, the page subtitle names what's moving), then press "Move here" on
any other column. Pressing the handle again cancels. Two taps instead of one gesture,
and it works identically on a phone, where dragging inside a scrolling column is
unpleasant anyway.

**If drag matters more than the licence:** a PCF code component — the community
"drag-and-drop gallery" components do exactly this — gives you real dragging. Code
components require the environment's **Power Apps component framework for canvas apps**
setting, which is an admin toggle, and using one makes the app premium. That's both
gates you were trying to avoid, for one gesture.

## 2. The list can't scroll horizontally

**Mockup:** a horizontal scrollbar under the portfolio list, implying columns past
"Next task".

**Platform:** galleries scroll vertically only. There's no horizontal scroll container.

**This build:** six columns sized to fit a 1366-wide tablet layout. Everything the
scrollbar implied lives in the Excel export instead, which already carries pursuit ID,
account, health, target decision date, Salesforce URL, and estimated fees — six fields
the screen doesn't show.

**If you need more on screen:** widen the app to 1920 in Settings and add columns (you'd
be designing for a monitor, not a laptop), or add a column-picker that swaps which six
render. Both are real work, and the export is usually what people actually wanted.

## 3. The AI overview is display-only

**Mockup:** a "Refresh overview" button that regenerates the narrative from Salesforce
plus attached materials.

**Platform:** every route from a canvas app to a language model is premium, admin-gated,
or both. AI Builder needs credits, Copilot Studio needs licences, and the HTTP and custom
connectors are premium — using any of them makes every user of the app premium.

**This build:** no Refresh button. SharePoint's native AI populates `Overview Text`,
`Version Number`, `Refreshed Date`, and `Is Current`; the workspace reads them and writes
nothing back. That's the right split — the generation problem moves to the tool that
already solves it, and the app stops needing a connector it can't have.

What went out with the button: version numbering, the `Is Current` flip, the pointer
update on the pursuit, and the transaction-ordering care all of that needed. The workspace
is meaningfully simpler for it.

**One thing to watch.** Nothing now enforces exactly one `Is Current = "Yes"` per pursuit
— the app used to guarantee it. Whatever populates the list owns that invariant. The
workspace falls back to the highest `Version Number` when the flag is missing or
ambiguous, so a card degrades to "probably the right version" rather than to blank, but
that's tolerance, not correctness.

## 4. Delegation, and why the text keys help

SharePoint returns at most 500 rows to a canvas app by default, 2000 at the ceiling, and
anything the connector can't translate into a server-side query is evaluated locally
against only those rows. No error — just quietly incomplete data.

The schema's text keys are a real advantage here. Every child-list filter is
`'Pursuit ID' = "PUR-001"` — text equality, which SharePoint delegates. Had the lists
been keyed on Lookup columns, `Filter(list, Lookup.Id = x)` wouldn't delegate and you'd
need helper columns. Nothing to add.

What this build does:

- Data row limit set to 2000 (`docs/02-app-setup.md`).
- `LoadPortfolio` pulls `'pursuit-tracker-actions'` **whole** and joins in memory. It
  looks wasteful, but `Filter(actions, Status.Value <> "Completed")` is *not* delegable
  — SharePoint delegates `=` on a choice column, never `<>` — so filtering server-side
  would silently return a truncated set. Fetching unfiltered is both correct and faster
  than a per-card lookup.
- Workspace filters go to the server, because they're text equality.

Where it bites eventually: once the actions list passes 2000 rows in total,
`ClearCollect(colActions, 'pursuit-tracker-actions')` starts truncating, and "next task
due" goes blank on cards for no visible reason. At three actions you have room.

Fix when you get there: add an `Is Open` Yes/No column to actions, maintained by the app
on every status write, and filter on it server-side. Yes/No delegates.

## 4b. Schema constraints, resolved

Four gaps between the exported schema and what the mockups need have been closed in
SharePoint: `Overview Text` is multi-line, `Aligned SIs` and `Hyperscalers` are
multi-select, the Choice columns have real values, and `Source Summary` is gone. Detail
in `docs/01-data-model.md`.

Two of those are load-bearing in ways that aren't obvious from the app:

**Defined choice values gave the board back its wiring.** With empty choice lists,
`Choices()` returned nothing and the stage order had to live in `App.OnStart` — adding a
workflow stage would have meant editing the app. It now reads from the column, so stage
order is a list setting. `App.OnStart` keeps a fallback for an empty choice list, because
fill-in is still enabled and the failure mode is a blank board with no error.

**Multi-select is what the chip galleries bind to.** Reverting either column to
single-select turns `ThisItem.'Aligned SIs'` from a table into a record, and every chip
gallery that binds to them renders empty rather than erroring.

**Still open: `Active`.** A Number column reading `0` on all fourteen rows, so the app
doesn't filter on it and the board shows everything, `Unassigned` included. Both filter
variants are in `App.OnStart`, commented — `Active = 1` if it stays a Number, `Active` if
it becomes Yes/No. Until one is uncommented, "active pursuit" isn't a concept the app has.

## 5. Excel export is CSV

See `docs/06-flows.md`. CSV, one action, instant. A real `.xlsx` is available through
Excel Online (Business) at the cost of one API call per row.

## 6. This doesn't run locally

Worth naming, since running locally is where you started. A canvas app runs in the Power
Apps player — browser, mobile app, or embedded in Teams or the SharePoint site. There's
no localhost.

The thing that would have given you both — Power Apps **code apps**, which run a real
React app at localhost via `pac code run` against Power Platform connectors — requires a
**Power Apps Premium** licence for every end user. That's a procurement conversation,
which is the thing you were avoiding. If your team ends up licensed for Premium anyway,
that path becomes strictly better than this one and the data model here carries over
unchanged.

## 7. There are no transactions

Canvas apps can't write atomically across two lists. As built this doesn't bite: every
write the app makes — a stage change, a new action, a new update — touches exactly one
list. The one place it would have mattered was the `Is Current` flip on AI overviews, and
that moved to SharePoint's AI along with the rest of the generation work.

Worth remembering if you add a multi-list write later: sequence it so a partial failure
leaves something visibly wrong rather than subtly wrong.

## 8. The dark theme is hand-built

Canvas apps have no dark mode. The palette in `src/App.Formulas.powerfx` is read off
your mockups and applied through named formulas, so it's centralised — but every new
control lands in Power Apps' default light styling and needs its `Fill` and `Color`
pointed at a token. Nothing enforces this. A control that looks wrong is almost always a
missed token.

---

## Estimate

| | |
|---|---|
| Setup, data sources, theme | ~30 min |
| Portfolio board | 2–3 hrs |
| Portfolio list | 1–2 hrs |
| Pursuit workspace | 2–3 hrs |
| Export flow | ~45 min |

Under a day. The formulas are written against your real schema, the list titles are
confirmed, and the schema changes are applied — the reconciliation pass that would have
eaten a second day is done. The workspace also lost its Refresh button and the version
lifecycle behind it, which is the largest single piece of logic that was in the original
estimate.

The workspace screen is the long pole — it's seven cards, five galleries, and two
slide-over panels. If you want something usable fast, build the board and the list
first: those two alone replace a spreadsheet.
