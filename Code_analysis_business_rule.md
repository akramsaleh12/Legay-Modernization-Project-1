# Legacy Payroll System — Code Analysis & Business Rule Extraction

**System:** Employee Management / Payroll (CICS BMS + COBOL + DB2)
**Components reviewed:** 1 mapset, 1 menu driver, 4 transaction programs, 1 DB2 table, 1 COMMAREA copybook

---

## 1. Component Inventory

| Component | Type | Purpose |
|---|---|---|
| `MAINSET` | BMS Mapset | Defines 5 maps: MAINMAP (menu), ADDMAP, INQMAP, UPDMAP, DELMAP |
| `EMPMAIN` | COBOL/CICS program | Menu driver — displays menu, routes to sub-transactions |
| `EMPADD` | COBOL/CICS/DB2 program | Add employee (INSERT) |
| `EMPINQ` | COBOL/CICS/DB2 program | Inquiry (SELECT) |
| `EMPUPD` | COBOL/CICS/DB2 program | Update employee (UPDATE) |
| `EMPDEL` | COBOL/CICS/DB2 program | Delete employee (DELETE) |
| `DFHCOMMAREA` | Copybook | Shared communication area, 12 fields |
| `employee_table` | DB2 table | Persistent employee/payroll data |

---

## 2. Structural Parse

### 2.1 Mapset (`MAINSET`)
One physical mapset, five logical maps sharing `SIZE=(24,80)`. Field-naming convention: `<Map-prefix><Field><I/L>` — `L` = label (ASKIP), `I` = input/output field (UNPROT).

- **MAINMAP**: `MOPT1I`–`MOPT4I` are **four separate 1-character input fields**, one per menu line, rather than a single "selection" field.
- **ADDMAP / UPDMAP**: identical field layout (emp#, name, basic, housing, transport, tax, insurance) — UPDMAP additionally repeats the same 7 fields under a `U`-prefix.
- **INQMAP / DELMAP**: input field (`IEMPNI` / `DEMPNI`) + one output/message field (`IRESULT` / `DELMSG`).

### 2.2 COMMAREA (`DFHCOMMAREA`)
```
CA-OPTION            X(1)
CA-EMP-NUM           9(9)
CA-EMP-NAME          X(100)
CA-BASIC-SAL         S9(9)V99 COMP-3
CA-HOUSING-ALLOW     S9(9)V99 COMP-3
CA-TRANSPORT-ALLOW   S9(9)V99 COMP-3
CA-TAX               S9(9)V99 COMP-3
CA-INSURANCE         S9(9)V99 COMP-3
CA-TOT-INCOME        S9(9)V99 COMP-3
CA-TOT-DEDUCTIONS    S9(9)V99 COMP-3
CA-NET-SALARY        S9(9)V99 COMP-3
CA-DATE              X(10)
```
Total length ≈ 168 bytes (1 + 9 + 100 + 8×6 packed... actual packed field is 6 bytes each for S9(9)V99 COMP-3 → 8 fields × 6 = 48, plus 10 = 168). All `LINK` calls hard-code `LENGTH(200)`, which is larger than the actual structure — not incorrect, but a magic number disconnected from the copybook (see §4.3).

### 2.3 Program Dependency Graph

```
EMPMAIN (menu driver)
  │
  ├── SEND/RECEIVE MAINMAP (MAINSET)
  │
  ├──[option 1]── LINK EMPADD ── SEND/RECEIVE ADDMAP ── SQL INSERT employee_table
  ├──[option 2]── LINK EMPINQ ── SEND/RECEIVE INQMAP ── SQL SELECT employee_table
  ├──[option 3]── LINK EMPUPD ── SEND/RECEIVE UPDMAP ── SQL UPDATE employee_table
  └──[option 4]── LINK EMPDEL ── SEND/RECEIVE DELMAP ── SQL DELETE employee_table

All programs → COPY MAINSET (BMS symbolic map)
All sub-programs → COPY DFHCOMMAREA (LINKAGE SECTION)
All sub-programs → EXEC SQL INCLUDE SQLCA
```

**Coupling notes:**
- Control flow is strictly **hierarchical via LINK** (not XCTL/pseudo-conversational) — each sub-program executes fully (SEND+RECEIVE+SQL) inside one `LINK`, then returns control to `EMPMAIN`, which loops back to `SEND-MENU`. This is a **conversational** design (holds the CICS task, and any DB2 locks, across a terminal "think time") — a known anti-pattern in CICS for scalability.
- Data dependency: all four sub-programs depend on `employee_table`'s exact column order and on `DFHCOMMAREA` layout — any field reorder breaks every program.
- `EMPMAIN`'s own `LINKAGE SECTION` declares **only `CA-OPTION`** (1 byte), not the full COMMAREA, even though it passes `LENGTH(200)` on every `LINK`. This is a structural inconsistency (see §4.2).

### 2.4 Data Flow per Transaction
| Program | Map → COMMAREA | COMMAREA → SQL | SQL → COMMAREA | COMMAREA → Map |
|---|---|---|---|---|
| EMPADD | 7 fields in | computed totals + all fields | — | status message only |
| EMPINQ | emp# in | emp# only | 9 fields out | formatted string out |
| EMPUPD | 7 fields in | computed totals + all fields | — | status message only |
| EMPDEL | emp# in | emp# only | — | status message only |

---

## 3. Business Rule Extraction

### 3.1 Payroll Calculation Rules (core business logic — EMPADD & EMPUPD, duplicated identically in both)

**Rule 1 — Total Income**
```
Total Income = Basic Salary + Housing Allowance + Transportation Allowance
```

**Rule 2 — Total Deductions**
```
Total Deductions = Tax + Insurance
```

**Rule 3 — Net Salary**
```
Net Salary = Total Income − Total Deductions
```

These three rules constitute the entire payroll computation. There is no tax-bracket logic, no percentage-based deduction, no proration, no min/max salary rule, and no currency/rounding rule — tax and insurance are **entered as fixed amounts by the user**, not derived.

### 3.2 Data Capture Rule
Employee number (`emp_num`) is the natural/primary key (DB2 `PRIMARY KEY` constraint) — uniqueness is enforced **only at the database level**; no application-level duplicate check exists before `INSERT`.

### 3.3 Record Existence Rule
Update and Delete both treat **SQLCODE 100** (DB2 "row not found") as the single business exception path:
- EMPUPD: `SQLCODE = 100` → `'NOT FOUND'`, else → `'UPDATED'` (assumes any non-100 code is success)
- EMPDEL: `SQLCODE = 100` → `'NOT FOUND'`, else → `'DELETED'` (same assumption)
- EMPINQ: `SQLCODE = 100` → `'NOT FOUND'`, else → build result string

**Implicit rule (undocumented/unenforced):** any other SQL error (deadlock, constraint violation, connection loss) is silently reported as success — a business-rule gap, not just a coding style choice.

### 3.4 Audit/Traceability Rule
`CA-DATE` is stamped with `FUNCTION CURRENT-DATE` **only on Add**, not on Update or Delete — so the table's `date` column only ever reflects creation date, never last-modified date. If the intent was "last touched date," that rule is not implemented for UPDATE.

### 3.5 Menu Authorization Rule
No operator/role check exists — every terminal user reaching `EMPMAIN` has equal access to Add/Inquire/Update/Delete. There is no separation of duties (e.g., delete requiring supervisor approval).

---

## 4. Findings — Structural & Logic Risks

These are defects/gaps surfaced by the parse, not style preferences:

1. **Menu option capture is likely broken.** `MAINMAP` defines four independent input fields (`MOPT1I`, `MOPT2I`, `MOPT3I`, `MOPT4I`) — one per line — but `EMPMAIN` unconditionally does `MOVE MOPT1I TO CA-OPTION`. Regardless of which line the user actually types into, only `MOPT1I` is ever read. Options 2–4 as designed cannot be reliably selected. This looks like the map should have had a single shared "selection" field.

2. **Unchecked RESP codes.** `EMPMAIN` requests `RESP(WS-RESP) RESP2(WS-RESP2)` on the menu `RECEIVE` but never evaluates them — errors (e.g., `MAPFAIL` if the user presses Enter with no input) fall through silently into the `EVALUATE`, likely hitting `WHEN OTHER`.

3. **No terminal exit path.** `EMPMAIN` ends with `GO TO SEND-MENU`, looping indefinitely; there is no PF-key (e.g., PF3) or `EIBAID` check to end the pseudo-conversation, and no `HANDLE AID`.

4. **COMMAREA length mismatch.** `EMPMAIN`'s `LINKAGE SECTION` only declares `CA-OPTION` (1 byte) but every `LINK` passes `LENGTH(200)` — this works only because CICS doesn't validate the sender's own view of the area, but it means EMPMAIN cannot see/set any of the other 11 fields even though it is nominally the owner of the exchange. Also, `200` doesn't match the copybook's true length (~168 bytes) — a hard-coded, undocumented magic number instead of `LENGTH(OF DFHCOMMAREA)`.

5. **No numeric edit-checks before COMPUTE.** `ABASICI`, `AHOUI`, `ATRANI`, `ATAXI`, `AINSURI` (and the UPDMAP equivalents) are BMS `UNPROT` alphanumeric fields moved directly into signed packed-decimal (`COMP-3`) COMMAREA fields, then used in `COMPUTE`. Non-numeric or blank input would cause a data exception (abend) at runtime — there's no `IF ... NUMERIC` / `NUMVAL` validation layer.

6. **EMPINQ `STRING` of a packed field.** `CA-NET-SALARY` (`COMP-3`) is concatenated directly into an alphanumeric result via `STRING ... CA-NET-SALARY ... INTO IRESULT`. Packed-decimal bytes strung as if they were display text will not render as a readable number — this needs an explicit numeric-to-display edit (e.g., through a `PIC -9(9).99` intermediate field) before `STRING`.

7. **Business logic duplicated, not shared.** The three payroll formulas (§3.1) are copy-pasted identically into `EMPADD` and `EMPUPD`. Any future rule change (e.g., adding a bonus or a percentage tax) requires updating both programs in lockstep — a maintenance/consistency risk typical of legacy sprawl.

8. **No application-level duplicate-key or negative-value validation.** Relies entirely on the DB2 `PRIMARY KEY` for uniqueness and has no rule preventing negative salary/allowance entries.

9. **Generic SQLCODE handling.** Only `SQLCODE = 100` is distinguished; all other SQLCODEs (constraint violations, deadlocks, connection errors) are folded into the "success" branch across EMPADD, EMPUPD, and EMPDEL.

---

## 5. Summary

The system implements a straightforward **4-function CRUD payroll transaction set** (Add/Inquire/Update/Delete) fronted by a single menu, with all payroll math reduced to three additive formulas (§3.1) computed and persisted at Add/Update time. Structurally, it's a classic small-shop CICS/COBOL/DB2 design — synchronous `LINK`-based routing, BMS symbolic maps, embedded SQL — but it carries several latent defects (menu field mismatch, no RESP/SQLCODE discrimination, no numeric edit checks, packed-field STRING misuse) that would surface as production abends or silent data-quality issues rather than compile-time errors, which is typical of undocumented legacy code that has likely never been exercised end-to-end against real user input.
