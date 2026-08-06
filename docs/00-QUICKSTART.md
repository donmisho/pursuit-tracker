# Quickstart — build it, step by step

No explanations. Reasoning lives in `docs/01`–`08`.

## A. Create the app

1. Go to <https://make.powerapps.com>. Confirm the environment picker (top right) says
   your default environment.
2. **+ Create** → **Blank app** → **Blank canvas app** → **Create**.
3. Name: `Pursuit Tracker`. If the dialog offers a **Format** choice, pick **Tablet**.
   Newer makers don't offer one and create a responsive app instead — that's fine, skip
   it. → **Create**.

## B. Settings

4. Gear icon (top right) → **Settings**.
5. **Display** → turn **Scale to fit** OFF. **No such toggle and the layout says
   Responsive? Skip it** — the two are mutually exclusive, so it's already off. While
   you're here, set **Orientation** to **Landscape** if that option is shown.
6. **General** → **Data row limit** → `2000`.
7. **Updates** → turn ON **Named formulas** and **User-defined functions**. **Not listed?
   They've gone GA and are already on — skip.**
8. Close Settings. **File → Save**. Reload the browser tab.

## C. Connect data

9. Left rail → **Data** (cylinder icon) → **Add data** → search `SharePoint` → your
   connection.
10. Paste site URL: `https://westmonroepartners1.sharepoint.com/sites/PursuitTracking` →
    **Connect**.
11. Tick all five: `pursuit-tracker-pursuits`, `pursuit-tracker-actions`,
    `pursuit-tracker-status-updates`, `pursuit-tracker-documents`,
    `pursuit-tracker-ai-history` → **Connect**.
12. **Add data** again → search `Office 365 Users` → **Connect**.

## D. Theme and startup

13. Left rail → **Tree view** → click **App** (top of the tree).
14. Property dropdown (left of the formula bar) → **Formulas**. Paste all of
    `src/App.Formulas.powerfx`.
15. Property dropdown → **OnStart**. Paste all of `src/App.OnStart.powerfx`.
16. Right-click **App** in the tree → **Run OnStart**.

## E. Screens

17. **+ New screen** → **Blank**. Do this four times.
18. Rename them (double-click the name in the tree) to exactly:
    - `scrPortfolioBoard`
    - `scrPortfolioList`
    - `scrPursuitWorkspace`
    - `scrPursuitDocsAI`
19. Delete the original `Screen1` if one exists.
20. Click **App** → property **StartScreen** → `=scrPortfolioBoard`.

## F. Paste the screens

Do these four in order. For each one:

21. Click the screen in the tree → property **Fill** → `=ClrPage`.
22. Open the YAML file, select all, copy.
23. **Delete any controls already on that screen first**, then right-click the screen name
    in the tree → **Paste**. Approve the browser clipboard prompt the first time.
    Pasting over an existing screen adds a second copy of everything — you get doubled,
    overlapping headers rather than a replacement.

| Screen | File |
|---|---|
| `scrPortfolioBoard` | `src/yaml/01-PortfolioBoard.pa.yaml` |
| `scrPortfolioList` | `src/yaml/02-PortfolioList.pa.yaml` |
| `scrPursuitWorkspace` | `src/yaml/03-PursuitWorkspace.pa.yaml` |
| `scrPursuitDocsAI` | `src/yaml/04-PursuitDocsAI.pa.yaml` |

## G. Screen OnVisible

24. `scrPortfolioBoard` → property **OnVisible** → paste everything in
    `src/App.OnStart.powerfx` **below** the `LoadPortfolio` banner comment, then add on a
    new line at the end:

    ```
    Set(gblMoving, LookUp('pursuit-tracker-pursuits', ID < 0))
    ```

25. `scrPortfolioList` → **OnVisible** → paste the same `LoadPortfolio` block (without the
    `Set(gblMoving, Blank())` line).

26. `scrPursuitWorkspace` → **OnVisible** → paste the code block at the top of
    `docs/05-screen-pursuit-workspace.md` (the one under "Screen `OnVisible`").

27. `scrPursuitDocsAI` → **OnVisible** → paste the code block near the top of
    `docs/05a-screen-documents-ai.md`.

## H. Run it

28. **File → Save**.
29. **F5** to preview. On a responsive app, run the browser maximised at 1366×768 or
    larger — the layout is positioned for that size and a smaller window clips the bottom
    of the workspace.
30. Check against the expected results in `docs/08-deploy-and-test.md` §2.

**Preview writes to your real SharePoint lists.** Before testing the move handle or the
Add task button, add a throwaway row `PUR-999` in `pursuit-tracker-pursuits` and test on
that.

## I. Excel download (optional, do it later)

31. Build the flow: `docs/06-flows.md`.
32. Back in the app: **Data → Add data** → search `PursuitTracker-ExportPortfolio`.
33. Select `btnDownloadExcel` → **OnSelect** → replace the placeholder with the formula in
    `docs/04-screen-portfolio-list.md` (under "The download").

## J. Publish

34. **File → Save**, then **Publish** → **Publish this version**.
35. App detail page in make.powerapps.com → copy the **Web link**.

---

## If something looks wrong

| Symptom | Fix |
|---|---|
| Everything red after step 14 | Step 7 toggles are off, or you didn't reload after step 8 |
| Only the last five entries in the theme error | User-defined functions unavailable — inline them, see `docs/02-app-setup.md` |
| "No type found for variable 'x'" | You have an older `App.OnStart.powerfx` — re-copy it, the current one seeds every global with a typed value |
| "The function 'AddColumns' has some invalid arguments" | Same — re-copy. Column names are now identifiers (`OwnerName`), not strings (`"OwnerName"`) |
| Board has no columns | Right-click App → Run OnStart |
| All cards say "No open actions" | Right-click App → Run OnStart |
| Cards show email addresses | Step 12 was skipped |
| Workspace or Docs & AI tab greyed out | Correct — click a card on the board first. Both need a pursuit selected |
| Docs & AI screen empty | `scrPursuitDocsAI.OnVisible` is missing — step 27 |
| Blue squiggle under `Status.Value <> "Completed"` | Correct — ignore it |
| "Unknown property 'Fill' for control type 'Button'" | Older YAML — re-copy. Buttons and inputs need the `Classic/` prefix |
| "Unknown property 'RadiusTopLeft' for control type 'Rectangle'" | Same — re-copy. Rounded shapes are `Classic/Button`, not `Rectangle` |
| "Name isn't valid" on `Transparent` | Older YAML — re-copy. It's `Color.Transparent`; the bare name isn't in scope |
| Headers doubled / text overlapping itself | You pasted over existing controls. Delete the screen's controls and paste again |
| Workspace opens blank after clicking a card | `scrPursuitWorkspace.OnVisible` is missing or stale — step 26. Check `gblPursuitKey` in View → Variables: if it holds `PUR-nnn`, the navigation worked and OnVisible is the problem |
| Workspace always says "New pursuit" | `gblNewPursuit` stuck true from a cancelled Add pursuit. Fixed in current YAML; re-copy all three screens |
| A paste in step 23 is rejected | See the FALLBACKS block at the bottom of that YAML file |

Full triage: `docs/08-deploy-and-test.md`.

---

## Notes for someone coming from forms programming

- **Properties are formulas, not values.** Every property box takes an expression that
  recalculates on its own, like a spreadsheet cell. There is no `lblTitle.Text = "x"`
  assignment anywhere — you set `Text` to a formula and it re-evaluates itself.
- **`OnSelect` and `OnVisible` are the only imperative places.** Statements separate with
  `;`. Everything else is declarative.
- **`Set()` makes a global variable; `ClearCollect()` makes an in-memory table.** Both are
  visible app-wide.
- **Galleries are your repeater.** `Items` is the data, the controls inside are the row
  template, `ThisItem` is the current row.
- **There is no compile step.** Errors show as red underlines in the property box while
  you type.
