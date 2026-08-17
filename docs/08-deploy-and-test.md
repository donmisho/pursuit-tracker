# Deploy and test

There is no build step and no deployment pipeline. A canvas app lives in Power Platform;
"deploying" is pressing Publish, and "testing" is pressing Play. What follows is the
order that surfaces problems early, and what the results should look like against your
fourteen pursuits.

---

## 1. First run, before anything is published

In Studio, press **F5** (or the ▶ button) to open Preview.

> **Preview writes to production.** There is no sandbox copy of your lists. Moving a card
> on the board patches the real SharePoint item the instant you press "Move here", and
> Save on the Add task panel creates a real `ACT-nnn` row. There is no undo.
>
> Before testing writes, add one throwaway pursuit — `PUR-999`, account "Test" — and do
> your stage-move and add-task testing on that. Your three `Unassigned` rows (PUR-007,
> PUR-008, PUR-011) look like safe targets and aren't: they're real pursuits, and a stage
> change on one is a real change.

## 2. What "working" looks like on your data

Your lists are thin — three actions, one update, one document, one AI overview, all
attached to two pursuits. Most of the app will look empty on first run, and almost all of
that emptiness is correct. Knowing which is which saves an hour of chasing non-bugs.

### Portfolio board

Fourteen cards across five columns:

| Column | Count | Pursuits |
|---|---|---|
| Unassigned | 3 | PUR-007, PUR-008, PUR-011 |
| WM Account Team Assimilation | 3 | PUR-003, PUR-010, PUR-013 |
| Partner Introduction | 3 | PUR-002, PUR-006, PUR-012 |
| Preliminary Scoping | 4 | PUR-001, PUR-004, PUR-009, PUR-014 |
| Proposal/Quote | 1 | PUR-005 |

Only **two cards show a next task**: Frazier/MatixCare (PUR-001) reads "Confirm buying
committee · August 12", and Evergreen (PUR-009) reads "Draft executive proposal ·
August 20". The other twelve read "No open actions". That's right — there are only three
action rows in the whole system.

Evergreen showing ACT-002 rather than ACT-003 is the test that matters. ACT-003 is due
July 31, earlier, but its status is `Completed`, so it's correctly excluded. If Evergreen
shows "Get Fujitsu to respond to RFP Questions", the open-action filter is broken.

**No card will show a red health bar.** Every row is `On track`. To confirm `recHealth`
works at all, set one pursuit's Health to `At risk` in SharePoint and reload.

Three cards have no target decision date (PUR-007, PUR-008, PUR-012) and should sort to
the *bottom* of their columns, not the top. That's the `Date(2099,12,31)` substitution
doing its job.

### Portfolio list

Same fourteen rows, sorted by pursuit name — the two Elevance Health rows land together.

Eight rows read "No Salesforce opportunity"; six read "Salesforce opportunity linked".
Most SI and hyperscaler cells are empty, because most rows carry neither.

### Pursuit workspace

Only two pursuits have anything to show, and they show *different* things — which between
them exercises every card:

| | PUR-001 (Frazier) | PUR-009 (Evergreen) |
|---|---|---|
| Actions | 1 | 2, one completed and greyed |
| Status updates | 1, tagged Risk | none |
| Documents | none | 1 |
| AI overview + history | Version 3 | none |

Open both. Between them every card populates at least once. Any *third* pursuit will show
a title, an owner, and four empty cards — correct, not broken.

Two things you cannot test with current data:

**The at-risk pill.** ACT-002 is `Health = At risk`, so it should show the red pill in
place of its due date on Evergreen's workspace. This one you *can* test — it's the one
risk indicator your data does exercise.

**The dependency wording.** "After proposal / quote" only renders when an action has a
predecessor *and no due date*. ACT-003 has both a predecessor and a due date, so the date
wins and the wording never appears. To see it, clear ACT-003's due date temporarily.

### My Actions

Only what `Action Owner Entra ID` says is yours, and only what isn't `Completed`. On
current data that is at most two rows — ACT-002 and ACT-003 — and none at all if the owner
addresses in the list aren't your sign-in address.

An empty screen here is the expected result of an address mismatch rather than a bug, so
the screen prints the address it matched. If that address looks right and the rows still
don't appear, check the actions' owner column for a different spelling, and check that the
two you expect aren't `Completed`.

Switch `SORT BY` between **Due Date** and **Opportunity**: the first puts the nearest date
at the top with undated actions last, the second groups by account and pursuit with dates
still ascending inside each group. Overdue dates render in the risk colour.

## 3. Wire the export, then re-test

`btnDownloadExcel` ships with a placeholder that just notifies. Once the flow from
`docs/06-flows.md` exists and is added under **Data → Add data**, replace its `OnSelect`
with the formula in `docs/04-screen-portfolio-list.md`.

Then check the file itself, not just that a download happened: open it and confirm the
Target decision column parses as a date rather than left-aligning as text, and that the
Aligned SIs cell for a multi-partner pursuit shows both names comma-separated.

## 4. Publish

**File → Save**, then **Publish**. Save alone updates the editor copy; until you publish,
anyone playing the app still gets the previous version.

**Settings → Versions** keeps every published version and lets you restore one. That is
your rollback, and it's the reason to publish deliberately rather than continuously —
a version you can name in your head is worth more than fifty you can't.

## 5. Where it runs

Publishing gives you a **Web link** from the app's detail page in
<https://make.powerapps.com> — bookmark it and it behaves like any web app.

Three other surfaces, no extra work:

- **Power Apps mobile app** — the app appears automatically. Expect it to be cramped: the
  layout is fixed at 1366×768 with "Scale to fit" off, so a phone letterboxes it. Usable
  on a tablet, awkward on a phone.
- **Teams** — the app's **⋯ → Add to Teams** produces an app you can pin to a channel.
- **The PursuitTracking SharePoint site** — edit a page, add the **Power Apps** web part,
  paste the app's URL. Worth doing: it puts the app next to the lists it reads, so people
  who find the lists find the app.

## 6. Sharing it with anyone else

Two permissions, and they are separate:

**The app.** Share from make.powerapps.com. Co-owner lets someone edit; User only runs it.

**The data.** Sharing the app grants nothing at the SharePoint layer. Every user needs
their own permission on the PursuitTracking site, and they see exactly what their own
access allows — the app runs as the signed-in user, not as you. Someone with the app but
no site access gets a screen of permission errors, which reads like a broken app rather
than a missing grant. Grant site access first, then share the app.

No premium licences are involved: SharePoint, Office 365 Users, and OneDrive for Business
are all standard connectors.

## 7. Moving it elsewhere later

For one person in the default environment, nothing further is needed. If it ever moves —
to a shared environment, or to a colleague — use **Export package** (`.zip`) and Import
on the other side. Connections don't travel: whoever imports it re-authorises SharePoint
and Office 365 Users on first open, and the app points at whatever site the connection
resolves to. Check the data sources after any import rather than assuming they came across.

---

## First-run triage

Every failure below is one I'd expect at least once. In rough order of likelihood:

**Every property on every screen is red right after pasting.** The theme isn't loaded.
Named formulas and User-defined functions both need switching on
(`docs/02-app-setup.md` step 2), and `App.Formulas` needs pasting before any screen.

**Board renders but has no columns.** `colStages` is empty. Run OnStart (right-click App
→ Run OnStart) — Studio doesn't run it automatically while you're editing.

**Cards show email addresses instead of names.** Office 365 Users isn't added as a data
source, or `UserProfileV2` couldn't resolve the address. The raw email is the designed
fallback, not a crash — but check the connector is present before assuming the address is
wrong.

**Every card reads "No open actions", including PUR-001 and PUR-009.** `colActions` is
empty. Same fix: run OnStart.

**A blue-underlined delegation warning on `Status.Value <> "Completed"`.** Expected and
documented (`docs/07`, section 4). SharePoint doesn't delegate `<>` on a choice column,
which is exactly why that filter runs in memory over a full pull. Ignore it until the
actions list passes 2000 rows.

**Chip galleries are empty everywhere.** `Aligned SIs` or `Hyperscalers` reverted to
single-select. The galleries bind to those as tables; as records they render nothing and
don't error.

**The workspace tab is greyed out.** By design — it stays disabled until `gblPursuitKey`
is set, which happens when you open a card or a list row. Without that guard the tab
opens an empty record and every gallery on it errors.

**An AI overview ends mid-sentence.** `Overview Text` is back to a 255-character Text
column, or was written while it still was one. SharePoint truncates silently.
