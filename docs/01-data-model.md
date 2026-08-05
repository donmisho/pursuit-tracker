# Data model — the real schema

Read from the five list exports, replacing the version I inferred from the mockups.
Several things are materially different from that guess; the differences are called out
in **[What changed](#what-changed-from-the-inferred-model)** at the bottom, and the
handful of SharePoint edits the mockups actually require are in
**[Required changes](#four-changes-you-need-to-make-in-sharepoint)**.

## Two structural facts that shape every formula

**Internal names are `field_0`, `field_1`, `field_2`…** These lists were created from a
spreadsheet import, so SharePoint auto-generated the internal names and they carry no
meaning. Power Apps binds by *display* name, so formulas read `ThisItem.'Account Name'`
— but any tool that goes through the REST API sees `field_1`. Don't rename a display
name and expect the internal name to follow; it won't.

**The keys are text, not list item IDs.** Pursuits are keyed `PUR-001` in the `Title`
column, and every child list points back with a text `Pursuit ID`. That's better than
what I assumed: SharePoint delegates `=` on a text column, so
`Filter(list, 'Pursuit ID' = "PUR-001")` runs server-side with no row-limit games. The
`PursuitKey` number columns I recommended last round are unnecessary — don't add them.

The `Title` column means something different in each list:

| List | `Title` holds | View header shows |
|---|---|---|
| pursuits | `PUR-001` | Title |
| actions | `ACT-001` | Action ID |
| status updates | `UPD-001` | Update ID |
| ai history | `AI-001` | Overview ID |
| documents | the document's name | Title |

Documents is the odd one — its `Title` is a real name and its `DOC-001` identifier lives
in a separate `Document ID` column.

> **List titles.** I've used `pursuit-tracker-pursuits`, `-actions`,
> `-status-updates`, `-documents`, `-ai-history` throughout, inferred from your export
> filenames. Check them against the site and find-and-replace across `docs/` and `src/`
> if they differ.

---

## 1. `pursuit-tracker-pursuits`

| Display name | Internal | Type | Notes |
|---|---|---|---|
| `Title` | `Title` | Text | `PUR-001` — the join key |
| `Account Name` | `field_1` | Text | Frazier, Elevance Health, CD&R |
| `Pursuit Name` | `field_2` | Text | The card and row heading |
| `Salesforce Opportunity ID` | `field_3` | Text | |
| `Salesforce Opportunity URL` | `field_4` | Text | Lightning URL. Blank on 8 of 14 |
| `WM Pursuit Owner Entra ID` | `field_5` | Text | **Email string, not a Person column** |
| `Workflow Stage` | `field_6` | Choice | Board columns |
| `Health` | `field_7` | Choice | On track / At risk |
| `Target Decision Date` | `field_8` | DateTime | "TARGET CLOSE" on the workspace |
| `Aligned SIs` | `field_9` | Choice | **Single-select today** — see required changes |
| `Hyperscalers` | `field_10` | Choice | **Single-select today** |
| `AI Overview Current Version` | `field_11` | Text | Pointer to the current `AI-nnn`. Empty in all rows |
| `Active` | `field_12` | **Number** | Not Yes/No. `0` in all 14 rows |
| `Estimated Fees` | `field_13` | Currency | Empty in all rows |

**Stage values present in the data**, in workflow order:

1. `Unassigned`
2. `WM Account Team Assimilation`
3. `Partner Introduction`
4. `Preliminary Scoping`
5. `Proposal/Quote`

Note the casing differs from the mockups ("WM account team assimilation"). The app uses
the data's casing — matching the mockup would mean rewriting 14 rows to buy nothing.

**`Active` is a number and every row is `0`.** If the app filtered on it, the board
would be empty. So it doesn't filter on it at all, and `docs/07` explains how to switch
that on once the column means something. Treat this as the first thing to decide.

## 2. `pursuit-tracker-actions`

Feeds "Actions and dependencies" on the workspace and "Next task due" everywhere else.

| Display name | Internal | Type | Notes |
|---|---|---|---|
| `Title` | `Title` | Text | `ACT-001` |
| `Pursuit ID` | `field_1` | Text | → pursuits `Title` |
| `Action Title` | `field_2` | Text | "Confirm buying committee" |
| `Workflow Stage` | `field_3` | Choice | Qualify / Proposal / Quote / Review / Decision |
| `Action Owner Entra ID` | `field_4` | Text | Email |
| `Status` | `field_5` | Choice | Not started / In progress / **Completed** |
| `Health` | `field_6` | Choice | On track / **At risk** |
| `Effort Size` | `field_7` | Choice | Small / Medium / XL |
| `Due Date` | `field_8` | DateTime | |
| `Predecessor Action ID` | `field_9` | Text | → another action's `Title` |
| `Completed Date` | `field_10` | DateTime | |
| `Notes` | `field_11` | Note | |

Two corrections to what I had:

**The "At risk" pill is `Health`, not `Status`.** ACT-002 is `Status = In progress`,
`Health = At risk` — the mockup's red pill on "Draft executive proposal". Status and
health are independent, which is right: an in-progress task can be at risk, and so can a
not-started one.

**The done value is `Completed`, not `Complete`.** "Next task due" filters on it, and
the wrong string means completed actions keep showing as next up.

**"After proposal" is derived, not stored.** The mockup shows that where Legal review's
date should be. There's no free-text due column — but there is `Predecessor Action ID`.
When an action has a predecessor and no due date, the app renders "After " plus the
predecessor's workflow stage. ACT-003 points at ACT-002 (`Proposal / Quote`), so it would
read "after proposal / quote".

Note the two stage vocabularies disagree: pursuits say `Proposal/Quote`, actions say
`Proposal / Quote`. They're different columns on different lists so nothing breaks, but
it's the kind of drift worth fixing while there are only three action rows.

## 3. `pursuit-tracker-status-updates`

| Display name | Internal | Type | Notes |
|---|---|---|---|
| `Title` | `Title` | Text | `UPD-001` |
| `Pursuit ID` | `field_1` | Text | |
| `Update Date` | `field_2` | DateTime | |
| `Update Type` | `field_3` | Choice | "Voice update" — the mockup's byline |
| `Update Text` | `field_4` | **Note** | Full body. Correctly multi-line |
| `Risk / Decision` | `field_5` | Choice | Risk / Decision |
| `Created By Entra ID` | `field_6` | Text | Email |

`Risk / Decision` isn't in the mockups and is worth surfacing — UPD-001 is tagged `Risk`,
which is exactly the thing a pursuit review needs to see. The app renders it as a small
pill on the update; drop the control if you'd rather match the mockup exactly.

## 4. `pursuit-tracker-documents`

| Display name | Internal | Type | Notes |
|---|---|---|---|
| `Title` | `Title` | Text | **Required.** The document's name |
| `Document ID` | `field_0` | Text | `DOC-001` |
| `Pursuit ID` | `field_1` | Text | |
| `Document Type` | `field_3` | Choice | "RFP Q&A" |
| `Document URL` | `field_4` | Text | Plain text, not a Hyperlink column |
| `Added Date` | `field_6` | DateTime | |
| `Added By Entra ID` | `field_7` | Text | Email |
| `Include in AI Overview` | `field_8` | Choice | Yes / No |

**The stored URL has no scheme** —
`westmonroepartners1-my.sharepoint.com/personal/…`. `Launch()` treats that as relative
and opens a broken address, so the app prepends `https://` when it's missing rather than
requiring the data to be cleaned first.

`Include in AI Overview` is the input filter for overview generation, and `Source
Summary` on the history list ("four included documents") is its output. The app counts
documents where this is `Yes` when it writes a new version.

Also note `field_2` and `field_5` don't exist — the import dropped two spreadsheet
columns. Harmless, but it's why the numbering skips.

## 5. `pursuit-tracker-ai-history`

| Display name | Internal | Type | Notes |
|---|---|---|---|
| `Title` | `Title` | Text | `AI-001` |
| `Pursuit ID` | `field_1` | Text | |
| `Version Number` | `field_2` | Number | |
| `Overview Text` | `field_3` | **Text (255 max)** | See below |
| `Refreshed Date` | `field_4` | DateTime | |
| `Source Summary` | `field_5` | Text | "Salesforce opportunity + four included documents" |
| `Is Current` | `field_6` | Choice | **"Yes" / "No" strings, not a boolean** |

**`Overview Text` is a single-line Text column, capped at 255 characters.** The sample
row is 197. The overview in your workspace mockup is about 430. Overviews will be
silently truncated on write — SharePoint doesn't error, it just cuts. This is the one
schema problem that will cost you real content, so it's first on the list below.

`Is Current` being a Choice means the test is `'Is Current'.Value = "Yes"`, and writes
patch `{ 'Is Current': { Value: "Yes" } }`.

---

## Four changes you need to make in SharePoint

Only the first is strictly blocking. The rest are what separates "close to the mockups"
from "matches them".

**1. `Overview Text` → Multiple lines of text.** List settings → the column → change
type. Existing values survive. Without this, every overview longer than a tweet gets
cut.

**2. `Aligned SIs` and `Hyperscalers` → allow multiple selections.** Both are
single-select today. The mockups need multi — NiSource carries Fujitsu *and* NTT Data,
Evergreen carries Microsoft *and* AWS — and single-select can't represent that. Column
settings → "Allow multiple selections". Existing single values convert cleanly.

The formulas in `docs/03`–`05` are written for multi-select. If you'd rather leave them
single, each chip gallery becomes a single label bound to `ThisItem.'Aligned SIs'.Value`
and you lose nothing else.

**3. Define the choice values.** Every Choice column on all five lists currently has an
*empty* choice list with `FillInChoice` on — values exist only because rows filled them
in ad hoc. That means `Choices('pursuit-tracker-pursuits'.'Workflow Stage')` returns
nothing, which is why the board no longer reads its columns from SharePoint (`src/App.OnStart.powerfx`
carries an explicit ordered stage table instead). Filling in the real choice values gives
you validated dropdowns in the SharePoint UI and stops "Proposal/Quote" and "Proposal /
Quote" style drift. The app works either way.

**4. Decide what `Active` means.** It's a Number, and it's `0` on all 14 rows. Either
populate `1` for live pursuits and switch the filter on in `LoadPortfolio`, or change it
to Yes/No, or drop it. Until then the board shows everything including `Unassigned`.

---

## What changed from the inferred model

For traceability, since the previous commit's formulas were built on the guess:

| I assumed | Actually |
|---|---|
| Integer `ID` joins, needing `PursuitKey` number columns | Text `PUR-nnn` keys, which delegate fine on their own |
| `PursuitOwner` as a Person column | Email text. Display names come from Office 365 Users at load |
| Multi-choice SIs and hyperscalers | Single-choice, needs converting |
| `IsActive` Yes/No | `Active` Number, all zero |
| `IsCurrent` Yes/No | `Is Current` Choice, "Yes"/"No" |
| Board columns from `Choices()` | Choice lists are empty; explicit ordered table |
| `DueDescription` free text for dependencies | Derived from `Predecessor Action ID` |
| Status `Complete`; at-risk from `Status` | Status `Completed`; at-risk from `Health` |
| `BoardOrder`, `Portfolio`, `ShortName` columns | Don't exist; board sorts by target date |
| `OverviewText` multi-line | 255-char Text |
| Documents URL a Hyperlink column | Text, sometimes without a scheme |

`tools/dump-list-schema.js` is still worth a run once you've made the changes above —
it prints the choice values, which the CSV exports don't carry.
