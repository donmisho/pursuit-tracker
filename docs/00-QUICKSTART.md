# Quickstart — build it, step by step

No explanations. Reasoning lives in `docs/01`–`08`.

**Twelve files get pasted, each into exactly one place. Nothing is pasted twice, and no file
is a fragment of another** — that last part matters, because the `OnVisible` blocks used to
be described as "the part of `App.OnStart` below the banner comment" and that stopped being
unambiguous once `OnStart` grew a section after it.

| # | File | Goes into |
|---|---|---|
| 1 | `src/App.Formulas.powerfx` | App → **Formulas** |
| 2 | `src/App.OnStart.powerfx` | App → **OnStart** |
| 3 | `src/yaml/01-PortfolioBoard.pa.yaml` | right-click `scrPortfolioBoard` → **Paste** |
| 4 | `src/yaml/02-PortfolioList.pa.yaml` | right-click `scrPortfolioList` → **Paste** |
| 5 | `src/yaml/03-PursuitWorkspace.pa.yaml` | right-click `scrPursuitWorkspace` → **Paste** |
| 6 | `src/yaml/04-PursuitDocsAI.pa.yaml` | right-click `scrPursuitDocsAI` → **Paste** |
| 7 | `src/yaml/05-MyActions.pa.yaml` | right-click `scrMyActions` → **Paste** |
| 8 | `src/screens/scrPortfolioBoard.OnVisible.powerfx` | `scrPortfolioBoard` → **OnVisible** |
| 9 | `src/screens/scrPortfolioList.OnVisible.powerfx` | `scrPortfolioList` → **OnVisible** |
| 10 | `src/screens/scrPursuitWorkspace.OnVisible.powerfx` | `scrPursuitWorkspace` → **OnVisible** |
| 11 | `src/screens/scrPursuitDocsAI.OnVisible.powerfx` | `scrPursuitDocsAI` → **OnVisible** |
| 12 | `src/screens/scrMyActions.OnVisible.powerfx` | `scrMyActions` → **OnVisible** |

Files 8 and 9 are the same `LoadPortfolio` block that's inside `App.OnStart`, differing
only in their last line. That duplication is deliberate: canvas apps have no user-defined
behaviour functions, so a block that has to run both at startup and on every visit has to
exist in both places.

## A. Create the app

1. <https://make.powerapps.com>. Confirm the environment picker (top right) says your
   default environment.
2. **+ Create** → **Blank app** → **Blank canvas app** → **Create**.
3. Name: `Pursuit Tracker`. If the dialog offers a **Format** choice, pick **Tablet**.
   Newer makers create a responsive app instead — that's fine, skip it. → **Create**.

## B. Settings

4. Gear icon (top right) → **Settings**.
5. **Display** → turn **Scale to fit** OFF. **No such toggle and the layout says
   Responsive? Skip it** — the two are mutually exclusive, so it's already off. Set
   **Orientation** to **Landscape** if shown.
6. **General** → **Data row limit** → `2000`.
7. **Updates** → turn ON **Named formulas** and **User-defined functions**. **Not listed?
   They've gone GA and are already on — skip.**
8. Close Settings. **File → Save**. Reload the browser tab.

## C. Connect data

9. Left rail → **Data** → **Add data** → search `SharePoint` → your connection.
10. Paste site URL: `https://westmonroepartners1.sharepoint.com/sites/PursuitTracking` →
    **Connect**.
11. Tick all **six**:
    - `pursuit-tracker-pursuits`
    - `pursuit-tracker-actions`
    - `pursuit-tracker-status-updates`
    - `pursuit-tracker-documents`
    - `pursuit-tracker-ai-history`
    - `pursuit-tracker-lookups`

    → **Connect**.
12. **Add data** again → search `Office 365 Users` → **Connect**.

The lookup list is the sixth and it's easy to miss. Without it every edit dropdown is
empty, and saving a pursuit writes a blank stage that SharePoint rejects.

## D. Theme and startup

13. Left rail → **Tree view** → click **App** (top of the tree).
14. Property dropdown (left of the formula bar) → **Formulas**. Paste **all** of
    `src/App.Formulas.powerfx`.
15. Property dropdown → **OnStart**. Paste **all** of `src/App.OnStart.powerfx`.
16. Right-click **App** in the tree → **Run OnStart**.

## E. Create the screens

17. **+ New screen** → **Blank**, five times.
18. Rename each (double-click in the tree) to exactly:
    - `scrPortfolioBoard`
    - `scrPortfolioList`
    - `scrPursuitWorkspace`
    - `scrPursuitDocsAI`
    - `scrMyActions`
19. Delete `Screen1` if one exists.
20. Click **App** → property **StartScreen** → `=scrPortfolioBoard`.

**All five have to exist before any paste.** Every screen's nav bar navigates to the other
four by name, and `Navigate()` to a screen that doesn't exist is an error Studio can't
resolve on its own.

## F. Paste the screens

For each of the five, in order:

21. Click the screen in the tree → property **Fill** → `=ClrPage`.
22. Open the YAML file, select all, copy.
23. Right-click the screen name in the tree → **Paste**. Approve the browser clipboard
    prompt the first time.

| Screen | File | Controls |
|---|---|---|
| `scrPortfolioBoard` | `src/yaml/01-PortfolioBoard.pa.yaml` | 44 |
| `scrPortfolioList` | `src/yaml/02-PortfolioList.pa.yaml` | 48 |
| `scrPursuitWorkspace` | `src/yaml/03-PursuitWorkspace.pa.yaml` | 137 |
| `scrPursuitDocsAI` | `src/yaml/04-PursuitDocsAI.pa.yaml` | 59 |
| `scrMyActions` | `src/yaml/05-MyActions.pa.yaml` | 40 |

Counts are what `python3 tools/validate-screens.py` prints — every control including
gallery children.

**A screen file is a bare control list — it must not start with `Screens:`.** A document
that opens with `Screens:` / `<name>:` / `Children:` declares a screen, so Studio creates a
second one (`scrPortfolioBoard_1`) instead of pasting into the one you selected. The files in
`src/yaml/` start with `- navBg:`; that is the form that pastes controls into a screen.

**Check what's actually on the clipboard before re-reporting a rejection.** The line and
column in a `PA1001` refer to the pasted text: if the error repeats unchanged after a fix,
the old copy is still in the clipboard.

On a fresh build the screens are empty, so there's nothing to delete first. **On a rebuild
there is**: pasting over existing controls adds a second copy of everything rather than
replacing it, and you get doubled headers with the transparent click layers fighting each
other. Click a blank part of the screen background, **Ctrl+A**, **Delete**, then paste.

## G. Screen OnVisible

Five files, five screens, no editing.

24. `scrPortfolioBoard` → **OnVisible** → all of
    `src/screens/scrPortfolioBoard.OnVisible.powerfx`
25. `scrPortfolioList` → **OnVisible** → all of
    `src/screens/scrPortfolioList.OnVisible.powerfx`
26. `scrPursuitWorkspace` → **OnVisible** → all of
    `src/screens/scrPursuitWorkspace.OnVisible.powerfx`
27. `scrPursuitDocsAI` → **OnVisible** → all of
    `src/screens/scrPursuitDocsAI.OnVisible.powerfx`
28. `scrMyActions` → **OnVisible** → all of
    `src/screens/scrMyActions.OnVisible.powerfx`

Skipping 24 is why a published board comes up blank while Studio looks fine: Studio keeps
collections alive from your last **Run OnStart**, so preview shows data the published app
never loads.

## H. Run it

29. **File → Save**.
30. **F5**. On a responsive app, run maximised at 1366×768 or larger.
31. Check against `docs/08-deploy-and-test.md` §2.

**Preview writes to your real SharePoint lists.** Before testing the move handle or Add
pursuit, add a throwaway `PUR-999` row and test on that.

## I. Excel download (optional, later)

32. Build the flow: `docs/06-flows.md`.
33. **Data → Add data** → search `PursuitTracker-ExportPortfolio`.
34. Select `btnDownloadExcel` → **OnSelect** → replace the placeholder with the formula in
    `docs/04-screen-portfolio-list.md` (under "The download").

## J. Publish

35. **File → Save**, then **Publish** → **Publish this version**.
36. App detail page in make.powerapps.com → copy the **Web link**.

Saving is not publishing. The played app keeps serving the last published version, and the
player caches hard — close the tab and reopen rather than refreshing.

---

## If something looks wrong

| Symptom | Fix |
|---|---|
| Everything red after step 14 | Step 7 toggles are off, or you didn't reload after step 8 |
| Only the last five theme entries error | User-defined functions unavailable — inline them, see `docs/02-app-setup.md` |
| "No type found for variable 'x'" | Older `App.OnStart.powerfx` — re-copy; the current one seeds every global with a typed value |
| "The function 'AddColumns' has some invalid arguments" | Same — re-copy. Column names are identifiers (`OwnerName`), not strings |
| "'ShowColumns' has some invalid arguments" | Older `App.OnStart.powerfx` — re-copy. The lookup projection is `ForAll` now |
| "Name isn't valid. 'Active' isn't recognized" | Same — re-copy. `Active` is a Choice column with no defined choices, so it never reaches the Power Apps schema and the filter is gone |
| Board has no columns, published only | Step 24 was skipped |
| Board has no columns, everywhere | Right-click App → Run OnStart |
| All cards say "No open actions" | Right-click App → Run OnStart |
| Cards show email addresses | Step 12 was skipped |
| Edit dropdowns empty | The lookup list wasn't connected (step 11) or OnStart hasn't been run |
| Save does nothing on a pursuit | Empty dropdowns write a blank stage and SharePoint rejects it — fix the dropdowns first |
| Save raises "Save failed: …" | Real SharePoint error. Most likely the lookup values don't match the column's choices — see `docs/05-screen-pursuit-workspace.md` |
| Workspace or Docs & AI tab greyed out | Correct — both need a pursuit selected. Click a card |
| My Actions is empty and says so | The owner email on the actions matches neither your address nor the part before its `@`. The screen prints the address it matched — fix `Action Owner Entra ID` in the list |
| My Actions is blank with no message | Step 28 was skipped, or the screen was pasted before `scrMyActions` existed |
| Workspace opens blank after clicking a card | Step 26. Check `gblPursuitKey` in View → Variables: if it holds `PUR-nnn`, navigation worked and OnVisible is the problem |
| Docs & AI screen empty | Step 27 |
| Blue squiggle under `Status.Value <> "Completed"` | Delegation warning — correct, ignore it |
| "Unknown property 'Fill' for control type 'Button'" | Older YAML — re-copy. Buttons and inputs need the `Classic/` prefix |
| "Name isn't valid" on `Transparent` | Older YAML — re-copy. It's `Color.Transparent` |
| "Duplicate name 'Color'" (PA1001) | Older YAML — re-copy |
| Headers doubled / text overlapping itself | You pasted over existing controls. Ctrl+A, Delete, paste again |
| A paste in step 23 is rejected | See the FALLBACKS block at the bottom of that YAML file |

Full triage: `docs/08-deploy-and-test.md`.

---

## Notes for someone coming from forms programming

- **Properties are formulas, not values.** Every property box takes an expression that
  recalculates on its own, like a spreadsheet cell. There is no `lblTitle.Text = "x"`
  assignment anywhere.
- **`OnSelect` and `OnVisible` are the only imperative places.** Statements separate with
  `;` — a separator, not a terminator, so a trailing `;` is a syntax error.
- **`Set()` makes a global variable; `ClearCollect()` makes an in-memory table.** Both are
  app-wide.
- **Galleries are your repeater.** `Items` is the data, the controls inside are the row
  template, `ThisItem` is the current row.
- **There is no compile step**, and **write failures are silent** — a `Patch` a column
  rejects returns blank and carries on. Every save in this app checks `Errors()` and
  notifies, which is why a failed save shows a red toast instead of appearing to do nothing.
