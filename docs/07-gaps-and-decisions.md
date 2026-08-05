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

## 3. The AI overview can't be generated inside the free tier

**Mockup:** a "Refresh overview" button that regenerates the narrative from Salesforce
plus attached materials.

**Platform:** every route from a canvas app to a language model is premium, admin-gated,
or both. AI Builder needs credits. Copilot Studio needs licences. The HTTP connector and
any custom connector are premium and make every user of the app premium. Azure OpenAI
needs a subscription and a key you'd have to get from someone.

**This build:** the button owns the version lifecycle — number the new version, demote
the old one, write the provenance line, refresh history — with the generated text as a
single `TODO` string. Everything around the model call is finished and correct.

**Three ways to finish it, cheapest first:**

- **Write from outside.** Your Copilot - Pursuit Strategy Agent already produces this
  kind of narrative. Have it write into `pursuit-tracker-ai-history` following the same
  `Is Current` rule, and the app displays it with no premium anything. The Refresh button
  becomes a re-read. The schema is already built for this — `Include in AI Overview` on
  documents is an input filter that nothing in the app populates, and `Source Summary`
  reads like something a generator wrote. I'd guess this is what you already intended.
- **A scheduled flow** that regenerates overviews nightly for pursuits whose Salesforce
  data changed. Still needs a model connector, but only *you* run the flow — app users
  stay free.
- **AI Builder "Create text with GPT"** inside the flow. Cleanest experience, costs
  credits, and credits are a procurement conversation.

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

## 4b. Four schema facts that shape the app

Detail and fixes in `docs/01-data-model.md`; the short version of what each one cost:

**`Overview Text` is a 255-character Text column.** Your mockup's overview is about 430.
SharePoint truncates rather than erroring, so this destroys content silently. Convert it
before wiring up any generator.

**`Aligned SIs` and `Hyperscalers` are single-select.** The mockups need multi — NiSource
with Fujitsu *and* NTT Data. Every chip gallery in `docs/03`–`05` is written for
multi-select and needs the column converted, or replacing with a single label.

**Every Choice column has an empty choice list.** `Choices()` returns nothing, so the
board can't read its columns from SharePoint and every dropdown in the add panels binds
to a literal table instead. The stage order lives in `App.OnStart`, which means adding a
stage is now an app edit rather than a list edit — a real regression against the original
design, and it goes away once the choice values are defined.

**`Active` is a Number and every row is `0`.** The app doesn't filter on it, so the board
shows all fourteen pursuits including the three `Unassigned` ones. Decide what the column
means, then switch the filter on — the line is in `App.OnStart`, commented.

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

Canvas apps can't write atomically across two lists. The place this matters is the
`Is Current` flip on AI overviews, which is why that code demotes before it inserts:
fail halfway and you get zero current versions rather than two, which is both easier to
spot and easier to repair.

Anywhere else you add a multi-list write, sequence it so a partial failure leaves
something visibly wrong rather than subtly wrong.

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
| Pursuit workspace | 3–4 hrs |
| Export flow | ~45 min |
| The four SharePoint column changes | ~15 min |

Call it a solid day. The formulas are now written against your real schema rather than
an inferred one, so the reconciliation pass that would have eaten the second day is
already done — what's left is confirming the five list titles.

The workspace screen is the long pole — it's seven cards, five galleries, and two
slide-over panels. If you want something usable fast, build the board and the list
first: those two alone replace a spreadsheet.
