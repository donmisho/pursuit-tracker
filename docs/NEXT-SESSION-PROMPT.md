# Prompt to start the next session

Copy everything below the line into a new chat.

---

I'm continuing work on the Pursuit Tracker — a Power Apps canvas app over SharePoint lists on
`https://westmonroepartners1.sharepoint.com/sites/PursuitTracking`. The source lives in
`donmisho/pursuit-tracker` on branch `claude/pursuit-tracker-local-app-bof6aq`.

**Read `CLAUDE.md` at the repo root first.** It has the constraints, the platform rules that
break pastes, the design conventions, and the open data issues. Don't re-derive any of it.

Three things that matter most:

1. **Pull the current code from GitHub, not from memory.** I edit screens directly in Power
   Apps Studio and push the result, so assume every file has moved. Read a file before you
   edit it, every time. If I paste a screen at you, that version is the source of truth —
   merge into mine rather than overwriting with yours.
2. **`python3 tools/validate-screens.py` must be clean before every commit.** It catches
   duplicate property keys, `PA2108` properties a control type doesn't have, dangling control
   references, and orphaned captions — all of which otherwise show up as a rejected paste in
   Studio.
3. **End every change with what to repaste and where.** The deliverable is text I paste into
   Studio — a screen YAML, an `OnVisible`, or `App.Formulas` — not a commit.

Keep it terse. Lead with the fix; skip the explanation unless it changes what I do.

## Where things stand

All five screens are built and pasting cleanly: `01-PortfolioBoard` (44 controls),
`02-PortfolioList` (48), `03-PursuitWorkspace` (137), `04-PursuitDocsAI` (59),
`05-MyActions` (33).

Most recent change: added `scrMyActions` — my open actions across every pursuit, sortable by
due date or by opportunity, with a row click into the pursuit workspace. It's documented in
`docs/09-screen-my-actions.md`. The other four screens each gained a `btnNavActions` nav
button, so all five needed repasting.

Still open on my side, in SharePoint rather than in code — the list is in
`docs/OPEN-ITEMS.md`: the lookup values don't match the Choice sets exactly, and three
pursuits still hold `0` in `Active`, so the Active filter stays commented out in
`App.OnStart.powerfx`.

## What I want to do next

<!-- Replace this line with the actual request. Examples of the shape it usually takes:
     - "Fix X on screen N — here's the current YAML I pulled from Studio: …"
     - "Add a <thing> to the workspace right column, keeping the 2/3–1/3 split"
     - "Here's the schema CSV for a list I changed — reconcile the app against it" -->
