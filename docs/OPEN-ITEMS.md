# Open items

Work state, not project knowledge — this file is expected to shrink. Tick items off as they
land rather than leaving them for a future session to re-flag.

## Data fixes, in SharePoint

These are data problems, not code problems. Don't work around them in the app.

### `pursuit-tracker-lookups` values must match the Choice sets exactly

A lookup row whose text differs from the column's Choice value makes the dropdown offer a
value the list will reject on save.

| List | Change |
|---|---|
| Workflow Stage | `Unassigned / Intake` → `Intake` |
| Workflow Stage | `Proposal / Quote` → `Proposal/Quote` |
| Workflow Stage | `Review / Decision` → `Review/Decision` |
| Workflow Stage | delete `Completed / Closed` |
| Hyperscaler | `GCP` → `Google/GCP`; add `SAP` and `Databricks` |
| SI | add `Everforth/Apex Systems` |
| Action Status | `Complete` → `Completed` |

### `Action Owner Entra ID` uses a different domain from the sign-in address

The actions list holds `dmishory@westmonroe.com`; `User().Email` returns
`dmishory@westmonroepartners.com`. My Actions matched neither and showed nothing, so the
screen now also matches on the part before the `@` — see `docs/09-screen-my-actions.md`.
That is a workaround with a real limit: it can't match an action owned by a different name,
and it would collide if two people ever shared a mailbox name across the two domains. Put
the sign-in address in the column and the loose half of the match stops mattering.

### Three pursuits hold `0` in `Active`

Left over from when `Active` was a Number column. It is now a Choice (`Yes` / `No` /
`Suspended`), and until those three rows are cleaned the board's Active filter stays
commented out in `src/App.OnStart.powerfx`.

---

## Deferred in the app

- **Height doesn't adapt.** The workspace stacks cards to a fixed bottom; a browser window
  shorter than ~800px clips the last card. Fixing it means rebuilding that screen on the
  Scrollable layout — no formula changes, but a full repaste. See `docs/02-app-setup.md`.
