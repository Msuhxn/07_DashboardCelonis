# Technical Dashboard Creation in Celonis

## Step-by-Step Runbook

**Process Mining Seminar | TH Köln | Master of Science in Digital Sciences**
**Topic 07 | Group 07 | Seminar date: 9 November 2026**

### Authors

- Malik Mohsin Azhar
- Samira Aghajani
- Mohammed Suhan

### About this document

This runbook describes how to build a technical process-mining dashboard in Celonis, from data ingestion to a deployed dashboard. Every step states what is done, why it is done, the exact actions, the expected result and how to resolve typical errors.

Part 1 builds a basic case-centric dashboard with a single event log. Part 2 builds a relational dashboard with PQL, KPIs and charts. Part 3 introduces object-centric concepts and a custom KPI.

### Contents

- [Part 0: Overview and preparation](#part-0-overview-and-preparation)
- [Part 1: Pizza event log (basic case-centric flow)](#part-1-pizza-event-log-basic-case-centric-flow), steps P1-01 to P1-14
- [Part 2: Orders dataset with 10,000 cases (PQL, KPIs, charts, filter, export)](#part-2-orders-dataset-10000-cases-and-pql-dashboard), steps O2-01 to O2-18
- [Part 3: Object-centric concepts and a custom KPI](#part-3-object-centric-concepts-and-a-custom-kpi), steps B3-01 to B3-14
- [Appendix A: PQL reference](#appendix-a-pql-reference) | [Appendix B: Key concepts (questions and answers)](#appendix-b-key-concepts)

---

# Part 0: Overview and preparation

## 0.1 Purpose

Celonis is a cloud-based process intelligence platform. Traditional BI tools show numbers; Celonis reconstructs the real process flow from event logs and exposes bottlenecks and deviations, showing how a process actually runs rather than how it was designed.

The goal of this project is to load raw files into Celonis Data Integration, build a data model, and design PQL metrics, KPIs and interactive dashboards in Celonis Studio, covering the complete technical path to a deployed dashboard.

## 0.2 Pipeline overview

```
Raw files     ->  Data Pool  ->  Data Model                    ->  Studio                  ->  Version     ->  Apps
(CSV / XLSX)      (storage)      (case, activity, time, joins)     (space, package, view)      and deploy      (end-user view)
```

Data enters a pool, the data model gives it the shape of a process, Studio builds dashboards on the model, and deployment publishes them to end users.

## 0.3 Names used in this runbook

All objects created by the team use the prefix PM26. Names of Studio spaces must be unique across the organization, and perspective names may contain only letters and numbers.

| Object | Name | Note |
|---|---|---|
| Data Pool (Part 1) | `PM26_Pizza_Basics_Pool` | Created by the team |
| Data Model (Part 1) | `PM26_Pizza_CaseCentric_Model` | Created by the team |
| Studio Space (Part 1) | `PM26_Pizza_Studio_Space` | Created by the team |
| Package (Part 1) | `PM26_Pizza_Insights_Pkg` | Created by the team |
| Data Pool (Part 2) | `PM26_Orders_10K_Pool` | Created by the team |
| Data Model (Part 2) | `PM26_Orders_10K_Model` | Created by the team |
| Studio Space (Part 2) | `PM26_Orders_Studio_Space` | Created by the team |
| Package (Part 2) | `PM26_Orders_Insights_Pkg` | Created by the team |
| Table aliases (Part 2) | `cases`, `events` | Short names used in PQL formulas |
| Data Pool (Part 3) | `ExampleOrderOCPM` | Provided by Celonis; not renamed |
| Perspective (Part 3) | `PM26OCPMOrderPerspective` | Letters and numbers only; underscores are not allowed |
| Studio Space / Package (Part 3) | `ExampleOrder` / `ExampleOrderOCPM` | Provided by Celonis; not renamed |
| View (Part 3) | `OCPM_Process_Overview` | New view created inside the package |

## 0.4 Common issues and resolutions

| Where | Symptom | Cause | Resolution |
|---|---|---|---|
| Studio: Create space | Space with this name already exists | Space names must be unique across the organization. | Cancel and choose a unique name (the PM26 prefix avoids clashes), or open the existing space. |
| Studio: Deploy | No versions to deploy yet | Celonis requires a version snapshot before deployment. | Click Create version, keep 1.0.0, click Create Version, then Deploy. |
| Data Model: activity table | The wizard lists two tables and the wrong one is selected | The cases table is listed before the events table. | Select the table in which one case has many rows (the events table). See O2-05. |
| Data Model: alias | No rename option in the wizard | Renaming is not part of the wizard. | Open Table settings of the table on the model canvas and fill in the Alias field (O2-06). |
| Data Model: warnings | Yellow banner: Missing Identifiers | Identifiers are optional. | Ignore it. It does not block Process Explorer or dashboards. |
| Studio: KPI card | Data requirements for this component are not met | The editor contains a plain column, not an aggregation. | Clear the editor and wrap the case column in `COUNT(...)` (O2-11). |
| Studio: OLAP table | Red PQL error column, or a column in which every value is 1 | A non-aggregated item or an incomplete COUNT was left in a column. | Delete that column through its three-dot menu and keep Activity, Case Count and Resource (O2-12). |
| Studio: Bar chart | Syntax error near [table] after reading `TABLE(events.ACTIVITY), COUNT()` | Dimension and metric were entered into the same editor field. | Clear the Metrics editor and enter a single COUNT formula there. Activity belongs only in Dimensions (O2-13). |
| Studio: export | The column header menu offers only Clear all sorting and Column display | That menu is not the export menu. | Hover over the table and use the download icon in its toolbar (.xlsx or .csv) (O2-17). |
| Objects and Events: perspective name | Perspective name must begin with a letter, and only contain alphanumeric characters | Underscores and spaces are not allowed in perspective names. | Use a name such as `PM26OCPMOrderPerspective` (B3-05). |
| Objects and Events: perspective | The + Add button is disabled: All available objects have already been linked | Celonis detected the object relationships automatically. | Not an error. Click Done (B3-06). |
| Objects and Events: perspective | Yellow banner: Not all objects are connected | Informational; data permissions and filters may not apply to every object. | Ignore it for this exercise (B3-06). |
| Studio: data model lists | ExampleOrderOCPM is not offered in Create space or Create package | These lists only show case-centric data models. | Do not create a new package. Create a new view inside the existing package (B3-09). |
| Data Pool: Create Data Model | A classic wizard opens (Tables, Activity Table, Process) with 24 raw tables | That button opens the case-centric wizard. | Cancel without selecting anything (B3-09). |

## 0.5 Pitfall: choosing the activity table

> **Select the table in which one case has many rows**
>
> When a model contains a cases table and an events table, the Activity Table must be the events table. The cases table has one row per order and describes attributes such as product, price, quantity and address.
>
> If the cases table is selected by mistake, the wizard preview shows product names and prices, the Activity becomes the product, and the Process Explorer shows products instead of business steps. With the events table, the preview shows activities such as place order, send invoice, confirm payment, make delivery and pay.
>
> The PQL names of the tables are shown in the Data tree of the PQL editor. In this runbook the case column is referenced as `"cases"."CASE"` and activity columns as `"events"."ACTIVITY"`.

## 0.6 Preparation

- **Files:** `pizza-log.csv`, `table-10000-cases.xlsx` and `table-10000-events.xlsx`.
- **Access:** a Celonis account of the university (Academic Alliance team).
- **Browser:** Chrome or Edge, zoom 90 to 100%.
- **Order of work:** Part 1, then Part 2, then Part 3.

## 0.7 Scope of Part 3

> **What Part 3 covers**
>
> Part 3 creates a perspective (`PM26OCPMOrderPerspective`) in Objects and Events on the Celonis example pool `ExampleOrderOCPM`, and builds a new dashboard view inside the Celonis example package `ExampleOrderOCPM`.
>
> The new view uses the knowledge model ExampleOrders KM, which provides the order event log and the case tables. The object-centric content of Part 3 is therefore the objects, the event type and the perspective, while the dashboard components analyse the same order data in the case-centric form used in Part 2.

---

# Part 1: Pizza event log (basic case-centric flow)

The pizza log is the simplest dataset: one table with three columns. It teaches the complete flow (upload, model, dashboard, deploy) that Part 2 repeats with more complex data.

## P1-01 | Sign in to Celonis

| | |
|---|---|
| **What we do** | Sign in with the university account and open the team workspace. |
| **Why** | Celonis is a cloud platform. Data Integration and Studio run in the browser, so nothing is installed locally. |
| **Benefit** | One login gives access to both data preparation and dashboards. |
| **Role in the project** | Foundation of the project: no pool, model or dashboard can exist without a workspace. |
| **In detail** | Celonis is delivered as a cloud service, similar to web email: the software and the data stay on Celonis servers and can be opened from any device. The university account places the user in an academic environment. |

**Steps**

1. Open Chrome or Edge with the browser zoom at 100% (screenshots stay sharp).
2. On the Celonis sign-in page enter the university email and password, then click Sign in.
3. The Celonis Accounts page opens. Under Teams, click the team card (Academic Alliance).
4. The Celonis EMS Apps landing page opens.

**Expected result:** The left sidebar shows the Data Integration and Studio icons and the app switcher (nine dots) at the top left.

*Documentation: P1-01a sign-in page (password hidden); P1-01b Accounts and Teams page; P1-01c Apps landing page.*

## P1-02 | Open Data Integration

| | |
|---|---|
| **What we do** | Open the Data Integration module from the left sidebar. |
| **Why** | Raw data enters Celonis and is structured here. A dashboard can only be built after the data exists in Celonis. |
| **Benefit** | All data pools are listed in one place and new pools are created from here. |
| **Role in the project** | First stage of the pipeline: Data Sources, Data Integration, Data Consumers (Studio). |
| **In detail** | Celonis consists of two main areas: Data Integration (bringing data in and preparing it) and Studio (building dashboards). Process mining depends on data quality, so work starts in Data Integration. |

**Steps**

1. Click the Data Integration icon (database symbol) in the left sidebar, or use the app switcher.
2. The list of Data Pools opens. Pre-installed example pools (such as Example and ExampleOrderOCPM) may be visible; leave them unchanged.

**Expected result:** The Data Pools page with a button at the top right for creating a new pool.

*Documentation: P1-02 Data Pools list (full screen).*

## P1-03 | Create a Data Pool

| | |
|---|---|
| **What we do** | Create the Data Pool `PM26_Pizza_Basics_Pool` for Part 1. |
| **Why** | A Data Pool is the container for tables, connections, data models and jobs. Nothing can be uploaded or modelled without one. |
| **Benefit** | Each dataset lives in its own organized environment, so pizza and orders data never mix. |
| **Role in the project** | It shows that the project starts with a proper pipeline. |
| **In detail** | Think of a pool as a separate kitchen: all ingredients (tables), recipes (data jobs) and finished dishes (data models) of one project are kept together. Separate pools keep table names, loads and permissions independent. |

**Steps**

1. Click the blue + New Data Pool button at the top right.
2. In the dialog choose Create from Scratch if offered, enter the name `PM26_Pizza_Basics_Pool` and click Save or Create.
3. The pool pipeline screen opens with the sections Input, Data Processing and Output.

**Expected result:** A pipeline diagram with the blue Connect to Data Source card.

*Documentation: P1-03a New Data Pool dialog with the name; P1-03b empty pool pipeline.*

## P1-04 | Upload pizza-log.csv

| | |
|---|---|
| **What we do** | Use Connect to Data Source then Upload Files to upload `pizza-log.csv` from the local folder. |
| **Why** | Celonis needs the event log as a table. The pizza log is a flat file with three columns: CASE, ACTIVITY and TIME. |
| **Benefit** | The smallest dataset teaches the complete flow (upload, model, dashboard) before it is repeated on complex data. |
| **Role in the project** | Baseline example of case-centric process mining with a single table. |
| **In detail** | An event log is a table in which each row is one event. The upload only transfers the file to Celonis; no analysis happens yet, which is why this stage is called staging. |

**Steps**

1. Click the blue Connect to Data Source button on the pipeline.
2. Choose Upload Files in the connector list.
3. Open the local data folder and drag `pizza-log.csv` into the Drop files here box (or use Select Files).
4. The table pizza-log appears in the file list.

**Expected result:** pizza-log is listed with a blue icon (staged, not yet imported).

*Documentation: P1-04a connector list with Upload Files; P1-04b uploaded file list.*

## P1-05 | Import the file

| | |
|---|---|
| **What we do** | Click the blue Import button in the pizza-log row. |
| **Why** | An uploaded file is only staged. Import parses it and creates a real table in the pool. |
| **Benefit** | Only imported tables can be selected in a data model. |
| **Role in the project** | It separates the raw file from a queryable table. |
| **In detail** | Import reads the file, detects the type of every column (text, number, date) and creates the table in the pool. Without it the data model wizard shows no tables. |

**Steps**

1. Click Import in the pizza-log row.
2. Wait for the green check mark.
3. Use the breadcrumb Data Pools > PM26_Pizza_Basics_Pool to return to the pool pipeline.

**Expected result:** A green check mark in the row.

*Documentation: P1-05 green check mark after import.*

## P1-06 | Create the Data Model and select the table

| | |
|---|---|
| **What we do** | Open Data Models in the pool Output, create `PM26_Pizza_CaseCentric_Model` and add pizza-log. |
| **Why** | A data model tells Celonis which tables exist and how they relate. |
| **Benefit** | Every Studio widget (Process Explorer, KPI cards and so on) reads from this model. |
| **Role in the project** | Without a model the dashboard has no data source. |
| **In detail** | The data model is a map: it states where the data lives and how it is organized. Studio never reads the file directly, it queries the model. |

**Steps**

1. Click the Data Models card (0 Data Models) in the Output block.
2. On the empty page click + Add Data Model at the top right.
3. Enter `PM26_Pizza_CaseCentric_Model` and click Save.
4. Step 1 (Tables): click + next to pizza-log so it moves to Selected items.
5. Click Next at the bottom right.

**Expected result:** Wizard step 2 (Activity Table) opens.

*Documentation: P1-06a empty Data Models page; P1-06b Tables step with pizza-log selected.*

## P1-07 | Map Case ID, Activity and Timestamp

| | |
|---|---|
| **What we do** | Select pizza-log as the Activity Table and map CASE to Case ID, ACTIVITY to Activity and TIME to Timestamp. |
| **Why** | An event log needs three answers: which case an event belongs to, what happened, and when. Process flows and variants are derived from them. |
| **Benefit** | With a correct mapping the process map, variants and throughput times are generated automatically. |
| **Role in the project** | Core concept of the seminar: how a raw table becomes an event log. |
| **In detail** | In the pizza example one order is one case and a step such as add cheese is one activity. If the mapping is wrong, events are joined in the wrong order and the resulting process map is meaningless. |

**Steps**

1. In step 2 (Activity Table) click the pizza-log row.
2. Step 1/4: Select Case ID column: click the CASE header.
3. Step 2/4: Select Activity column: click the ACTIVITY header.
4. Step 3/4: Select Timestamp column: click the TIME header.
5. Step 4/4 (sorting column) is optional. Click Finish.

**Expected result:** The model editor shows pizza-log with the activity table icon. A yellow Missing Identifiers banner may appear; it can be ignored.

**If this occurs**

- *Missing Identifiers banner* -> Optional; it does not block the process explorer.

*Documentation: P1-07a Case ID selection; P1-07b Timestamp selection; P1-07c model editor after Finish.*

## P1-08 | Run a full data load

| | |
|---|---|
| **What we do** | Open the Data loads tab of the model and start a full load. |
| **Why** | Until now the model is only a definition. The load prepares the data in the in-memory engine. |
| **Benefit** | Dashboards answer in seconds after a load. |
| **Role in the project** | Without a load the Process Explorer shows no data. |
| **In detail** | A model is like building plans: it describes the structure. During the load Celonis prepares the data in a fast in-memory engine. If the data changes, the model must be loaded again. |

**Steps**

1. Click the Data loads tab next to Model.
2. Click the blue Load Data Model button at the top right.
3. Choose a full (complete) load and wait until it finishes.

**Expected result:** A green check mark with Currently loaded Data Model (1 tables successfully loaded).

*Documentation: P1-08 successful load screen.*

## P1-09 | Create a Studio space

| | |
|---|---|
| **What we do** | Open Studio and create the space `PM26_Pizza_Studio_Space` with the data model attached. |
| **Why** | Studio is organized as Space (project folder), Package and View (dashboard). |
| **Benefit** | A data model attached to the space is inherited by the packages inside it. |
| **Role in the project** | Shows that dashboards are organized in a structured way. |
| **In detail** | A space is the project folder inside Studio. Names must be unique because every user in the organization shares the same namespace. |

**Steps**

1. Open Studio from the app switcher.
2. Click + Create space at the top right.
3. Enter the Space Name `PM26_Pizza_Studio_Space`.
4. In Suggested Data Models select `PM26_Pizza_CaseCentric_Model`.
5. Click Create.

**Expected result:** An empty space opens and the model name is shown at the top right.

**If this occurs**

- *Space with this name already exists* -> Space names must be unique. Cancel and choose another name, or open the existing space.

*Documentation: P1-09a Create space dialog; P1-09b empty space.*

## P1-10 | Create a package and view

| | |
|---|---|
| **What we do** | Create the package `PM26_Pizza_Insights_Pkg`; it opens with a first view (the dashboard canvas). |
| **Why** | A package bundles the view, the knowledge model and the versions of a dashboard. |
| **Benefit** | Versioning and deployment happen at package level. |
| **Role in the project** | This is where the dashboard creation itself begins. |
| **In detail** | A package is a dashboard application: it holds the view (the screen), the knowledge model (business definitions) and versions. That is why deployment is done per package. |

**Steps**

1. Click Create package in the center of the space.
2. Package name `PM26_Pizza_Insights_Pkg`; Initial content View; the data model is mapped automatically. Click Create.

**Expected result:** An empty view canvas opens; the right panel lists components (KPI card, Process Explorer, Variant Explorer and others).

*Documentation: P1-10a Create package dialog; P1-10b empty view canvas.*

## P1-11 | Add the Process Explorer

| | |
|---|---|
| **What we do** | Drag the Process Explorer component onto the canvas. |
| **Why** | The Process Explorer is the discovered process map: activities and the paths between them. |
| **Benefit** | It shows how work really flows. |
| **Role in the project** | First visual result and core demo of the seminar. |
| **In detail** | The Process Explorer orders the events of all cases and shows which activity follows which and how often. It reveals what actually happened, not what a procedure says should happen. |

**Steps**

1. In the Components panel search for Process Explorer (section Process visualizations).
2. Drag it onto the canvas.

**Expected result:** A graph: take order, create base, add mushrooms / cheese / tomato / salami, bake in oven, eat pizza, clean kitchen. The log contains 1.28K cases.

*Documentation: P1-11 rendered Process Explorer (full screen).*

## P1-12 | Add the Variant Explorer

| | |
|---|---|
| **What we do** | In edit mode add the Variant Explorer next to the Process Explorer. |
| **Why** | The Variant Explorer shows how many cases follow exactly the same path. |
| **Benefit** | The standard path and the deviations can be compared. |
| **Role in the project** | Introduces variant analysis. |
| **In detail** | A variant is one distinct path through the process. With 111 variants for about 1,280 orders the process is quite diverse. The Variant Explorer lists the top variants so common and rare paths can be told apart. |

**Steps**

1. Click the pencil icon (Edit) at the top right.
2. Search for Variant Explorer in Components.
3. Resize the Process Explorer and drop the Variant Explorer beside it.

**Expected result:** The most common variant covers 72 of 1.28K cases (6%); the log contains 111 variants.

*Documentation: P1-12 Process Explorer and Variant Explorer side by side.*

## P1-13 | Create a version and deploy

| | |
|---|---|
| **What we do** | Use Deploy at the top right to create version 1.0.0 and publish it to Apps. |
| **Why** | Celonis requires a frozen snapshot (version) before publishing, which keeps releases controlled. |
| **Benefit** | Users see a stable dashboard while editing continues. |
| **Role in the project** | Final deliverable of the part: a live dashboard. |
| **In detail** | A version is a frozen copy. Editing continues in edit mode while end users only see the deployed version. If something breaks, an earlier version can be restored. |

**Steps**

1. Click the blue Deploy button at the top right.
2. The dialog shows No versions to deploy yet. Click Create version.
3. Keep version 1.0.0 with the View and Knowledge Model selected; click Create Version.
4. In the Deploy dialog click Deploy.

**Expected result:** Green banner: Deployment successful - Version 1.0.0 deployed to Apps.

**If this occurs**

- *No versions to deploy yet* -> Create a version first, then deploy.

*Documentation: P1-13a No versions dialog; P1-13b Create Version dialog; P1-13c deployment banner.*

## P1-14 | Check the dashboard in Apps

| | |
|---|---|
| **What we do** | Open the published view from the banner link and test the interaction. |
| **Why** | End users see the dashboard in this form, without editing controls. |
| **Benefit** | Confirms that deployment worked and that the widgets are connected. |
| **Role in the project** | Closing demo of Part 1. |
| **In detail** | Apps is where business users consume dashboards. Testing there shows that the widgets are connected: selecting a variant filters the map. |

**Steps**

1. Click Go to Apps in the banner (or open Apps from the sidebar).
2. In the published view click the top variant in the Variant Explorer.
3. Observe that the Process Explorer highlights the path of that variant.

**Expected result:** The Process Explorer filters to the selected variant.

*Documentation: P1-14a published Apps view; P1-14b filtered variant view.*

## Results of Part 1

- **Dataset:** pizza-log.csv | **Cases:** about 1,280 | **Variants:** 111 | **Most common variant:** 72 cases (6%)
- **Hierarchy:** PM26_Pizza_Studio_Space, PM26_Pizza_Insights_Pkg, Version 1.0.0

---

# Part 2: Orders dataset (10,000 cases) and PQL dashboard

The orders dataset has two tables (cases and events). This part covers the foreign key, PQL aggregations, KPI cards, an OLAP table, a bar chart, a filter, custom KPIs and export. Note: in step O2-05 the events table is the Activity Table.

## O2-01 | Create a Data Pool for the orders data

| | |
|---|---|
| **What we do** | Create the Data Pool `PM26_Orders_10K_Pool`. |
| **Why** | The orders data is more realistic than the pizza log: two tables and 10,000 cases. |
| **Benefit** | The orders tables stay isolated from the pizza data. |
| **Role in the project** | Part 2: advanced case-centric analysis with PQL tables and charts. |
| **In detail** | A separate pool keeps tables and load history of each dataset independent. |

**Steps**

1. Open Data Integration and click + New Data Pool.
2. Name: `PM26_Orders_10K_Pool`; click Save or Create.

**Expected result:** An empty pool pipeline.

*Documentation: O2-01 new pool pipeline.*

## O2-02 | Upload the cases and events files

| | |
|---|---|
| **What we do** | Upload `table-10000-cases.xlsx` and `table-10000-events.xlsx` through Connect to Data Source and Upload Files. |
| **Why** | The data is relational: order attributes are stored in the cases table and the individual steps in the events table. |
| **Benefit** | Joining the tables allows case attributes and activities to be analysed together. |
| **Role in the project** | Demonstrates multi-table case-centric modelling beyond the single-table pizza example. |
| **In detail** | In practice data is rarely in one table. The cases table holds order information, the events table holds each step. Celonis joins them later. |

**Steps**

1. Click Connect to Data Source and choose Upload Files.
2. Drag both xlsx files into the Drop files here box.
3. Two tables appear, named like `table-10000-cases_event_log-10000-orders` and `table-10000-events_event_log-10000-orders`.

**Expected result:** Both tables listed as staged files.

*Documentation: O2-02 list of both uploaded files.*

## O2-03 | Import both tables

| | |
|---|---|
| **What we do** | Click Import for each of the two rows. |
| **Why** | As in Part 1, a table can only be used in a model after it is imported. |
| **Benefit** | The tables become real tables in Data Storage. |
| **Role in the project** | Prerequisite for the data model. |
| **In detail** | The import logic is identical to Part 1. Each table is imported separately because each has its own column types. |

**Steps**

1. Click Import on each row.
2. Wait for green check marks on both.
3. Return to the pool with the breadcrumb Data Pools > PM26_Orders_10K_Pool.

**Expected result:** Green check marks on both rows.

*Documentation: O2-03 both imports completed.*

## O2-04 | Create the Data Model and select both tables

| | |
|---|---|
| **What we do** | Create `PM26_Orders_10K_Model` and move both tables to Selected items. |
| **Why** | The model now contains two tables that will be linked by a foreign key. |
| **Benefit** | Process data and case attributes become available in one query. |
| **Role in the project** | Foundation of the relational schema. |
| **In detail** | Selecting tables is not enough: Celonis must be told which one contains the events. That is the next step. |

**Steps**

1. Click the Data Models card in the Output block and then + Add Data Model.
2. Name: `PM26_Orders_10K_Model`; click Save.
3. Step 1 (Tables): click + for both tables so they appear under Selected items.
4. Click Next.

**Expected result:** Step 2 (Activity Table) lists both tables.

*Documentation: O2-04 both tables selected.*

## O2-05 | Select the events table as the Activity Table

| | |
|---|---|
| **What we do** | In step 2 select the events table and map CASE, ACTIVITY and START TIME. |
| **Why** | The activity table must be the table in which one case has many rows (one row per event). The cases table has one row per order. |
| **Benefit** | The correct table yields real business activities in the process map. |
| **Role in the project** | The correctness of the whole dashboard depends on this single choice. |
| **In detail** | An activity table has many rows per case, one per event. The cases table has a single row per order, so it cannot serve as the activity table. Choosing it turns products into activities. The correct table produces activities such as place order, send invoice and confirm payment. |

**Steps**

1. The Activity Table list shows two rows; the cases row is listed first. Click the row `table-10000-events_event_log-10000-orders`.
2. Step 1/4: Select Case ID: click the CASE header.
3. Step 2/4: Select Activity: click the ACTIVITY header.
4. Step 3/4: Select Timestamp: click the START TIME header. Do not use END TIME or the technical `_CELONIS_CHANGE_DATE` column.
5. Step 4/4 (sorting column) is optional. Click Finish.

**Expected result:** The preview shows business activities such as place order, send invoice, confirm payment, make delivery, pay and cancel order.

**If this occurs**

- *The preview shows product names, prices and addresses* -> The cases table was selected by mistake. Go back and select the events table. With the wrong table, products become activities and the process map is meaningless.

*Documentation: O2-05a Activity Table list with the events row; O2-05b timestamp selection with the events preview.*

## O2-06 | Set table aliases

| | |
|---|---|
| **What we do** | On the model canvas open Table settings and set the aliases `cases` and `events`. |
| **Why** | Automatic names such as `table-10000-events_event_log-10000-orders` are long and error-prone in PQL. |
| **Benefit** | Formulas become short and readable. |
| **Role in the project** | Shows clean modelling practice. |
| **In detail** | An alias is a short nickname for a table. The model wizard offers no rename option, so the alias is set in Table settings on the canvas. |

**Steps**

1. On the model canvas open the Table settings of the cases table.
2. Enter the Alias `cases` and click Save.
3. Repeat for the events table with the alias `events`.

**Expected result:** The two table cards now show the names cases and events.

**If this occurs**

- *Blue note: Please load the Data Model first to enable proper validation* -> Informational. The alias can be saved before the model is loaded.

*Documentation: O2-06 Table settings dialog with the alias.*

## O2-07 | Define the foreign key (1:N join)

| | |
|---|---|
| **What we do** | Use Set foreign keys to join cases (dimension, 1) to events (fact, N) on CASE. |
| **Why** | Celonis must know which order each event belongs to. |
| **Benefit** | Case attributes and activities can be queried together. |
| **Role in the project** | The technical core of the relational model. |
| **In detail** | A foreign key is the column that links two tables (here CASE). One order has many events, so cases is the one side (dimension) and events the many side (fact). After the join, events can be analysed by order attributes such as product. |

**Steps**

1. Two yellow banners (Missing Foreign Keys and Missing Identifiers) appear. Click the blue Set foreign keys button at the top right.
2. Choose cases as Dimension table (1).
3. Choose events as Fact table (N).
4. The CASE columns are selected on both sides. Click Save.

**Expected result:** A dotted line joins the two tables and the Missing Foreign Keys banner disappears. Missing Identifiers remains optional.

**If this occurs**

- *The join appears reversed* -> Use the Swap tables button.

*Documentation: O2-07a Foreign key settings; O2-07b joined tables on the canvas.*

## O2-08 | Run a full data load

| | |
|---|---|
| **What we do** | Run a full load from the Data loads tab. |
| **Why** | The load validates the foreign key and makes both tables queryable. |
| **Benefit** | The in-memory model of 10,000 cases becomes available. |
| **Role in the project** | Dashboard components show data only after the load. |
| **In detail** | During the load Celonis checks the foreign key and keeps both tables in memory as one logical database. COMPLETE means all data was loaded fresh. |

**Steps**

1. Open the Data loads tab next to Model.
2. Click Load Data Model and run a full load.
3. Wait for the green check mark.

**Expected result:** Green check mark: 2 tables successfully loaded, load type COMPLETE.

*Documentation: O2-08 load success (2 tables, COMPLETE).*

## O2-09 | Create the Space and Package in Studio

| | |
|---|---|
| **What we do** | Create `PM26_Orders_Studio_Space` and inside it the package `PM26_Orders_Insights_Pkg`. |
| **Why** | Same hierarchy as in Part 1, now with the orders model. |
| **Benefit** | A second package with its own versions and dashboard. |
| **Role in the project** | Container of the main dashboard. |
| **In detail** | The Studio hierarchy is the same as in Part 1. This time the package receives the orders model. |

**Steps**

1. In Studio click + Create space: name `PM26_Orders_Studio_Space`, suggested data model `PM26_Orders_10K_Model`, Create.
2. Click Create package: name `PM26_Orders_Insights_Pkg`, Initial content View, data model mapped automatically, Create.
3. The canvas shows empty Configure component boxes.

**Expected result:** An empty analysis canvas with the Components panel on the right.

**If this occurs**

- *Space with this name already exists* -> Use a unique name.

*Documentation: O2-09a Create space; O2-09b Create package; O2-09c empty canvas.*

## O2-10 | Add the Process Explorer and verify it

| | |
|---|---|
| **What we do** | Drop the Process Explorer and check that the nodes are business activities. |
| **Why** | This confirms that the correct activity table was selected (O2-05). |
| **Benefit** | A wrong mapping is detected immediately. |
| **Role in the project** | Process discovery output of Part 2. |
| **In detail** | This is a sanity check. Business steps on the map prove that the activity table is correct; product names would mean the wizard must be repeated. |

**Steps**

1. In Components open Process visualizations and drag Process Explorer into a box.
2. Review the graph.

**Expected result:** Nodes are business activities (place order, send invoice, send reminder, confirm payment, make delivery, pay, prepare delivery, cancel order). If product names appear, repeat O2-05.

**If this occurs**

- *Extra empty Configure component boxes* -> Hover over a box and use the trash icon to remove it.

*Documentation: O2-10 Process Explorer with business activities.*

## O2-11 | KPI card: Total Cases

| | |
|---|---|
| **What we do** | Add a KPI card that shows the total number of cases (10,000). |
| **Why** | A KPI card shows one number produced by an aggregation (COUNT). |
| **Benefit** | The scale of the data is visible at a glance. |
| **Role in the project** | First practical PQL example. |
| **In detail** | A KPI card displays a single number. In PQL a number needs an aggregation (COUNT, AVG, SUM). Giving only a column returns a list of 10,000 values and Celonis reports that the data requirements are not met. |

**Steps**

1. Click the top-right Configure component box and choose KPI card under KPIs.
2. Open Settings, then Main KPI and click + Add data or drag it here. The PQL editor opens.
3. Clear the text in the black editor.
4. Enter `COUNT("cases"."CASE")`. Tip: type `COUNT(` and press Ctrl + Space to pick the column.
5. The preview shows 10000 and the green banner Data requirements for this component have been met appears. Click Done.
6. Set the title to Total Cases.

**Expected result:** The KPI card shows 10,000.

**If this occurs**

- *Data requirements for this component are not met* -> The editor contains only a dimension column. Replace it with `COUNT(...)` around the case column.
- *The table name looks different* -> Click the column in the left Data tree; the tree shows the exact table name to use.

*Documentation: O2-11a KPI PQL editor (preview 10000); O2-11b KPI card on the dashboard.*

## O2-12 | OLAP table: Activity, Case Count, Resource

| | |
|---|---|
| **What we do** | Add an OLAP table with the columns Activity, Case Count and Resource. |
| **Why** | An OLAP table shows dimensions (grouping) next to metrics (aggregations): case counts per activity. |
| **Benefit** | Exact numbers complement the visual charts. |
| **Role in the project** | Combines BI-style analysis with process mining. |
| **In detail** | An OLAP table works like SQL GROUP BY: dimensions (Activity, Resource) form the groups and the metric (Case Count) gives the number. It provides exact numbers next to graphs. |

**Steps**

1. Click the top-left box, choose OLAP Table and open + Add data or drag it here under Columns.
2. Column 1: expand Events in the left tree and click Activity. In Display settings set Name to Activity; click Done.
3. Column 2: add a new column (+ or SHIFT + click on a tree item). Enter `COUNT("cases"."CASE")`, name it Case Count, click Done.
4. Column 3: click Events then Resource, name it Resource, click Done.

**Expected result:** A table of case counts per activity and resource (the count for place order is exactly 10,000).

**If this occurs**

- *A column with a red PQL error* -> Open its three-dot menu and choose Delete.
- *A column in which every value is 1* -> It is a non-aggregated item. Delete it.
- *Formulas such as `COUNT(events.ACTIVITY)` distort the counts* -> Keep only Activity, Case Count and Resource.

*Documentation: O2-12a PQL editor for the Activity column; O2-12b final OLAP table.*

## O2-13 | Bar chart: cases per activity

| | |
|---|---|
| **What we do** | Add a bar chart with Activity as the dimension and Case Count as the metric. |
| **Why** | It compares the volume of activities at a glance. |
| **Benefit** | Bottlenecks and rare activities become visible. |
| **Role in the project** | Adds visual analytics to the table. |
| **In detail** | A bar chart needs two things: what the bars represent (dimension) and how long each bar is (metric). If both end up in one editor, PQL reads them as one expression and reports a syntax error. |

**Steps**

1. In edit mode open Components, then Charts, and drop a Bar chart into an empty area.
2. Click the chart (Configure component).
3. In the right panel: Dimensions, + Add data or drag it here, Events, ACTIVITY, Done.
4. Metrics, + Add data or drag it here: clear the editor and enter only `COUNT("cases"."CASE")`, then Done.

**Expected result:** One bar per activity and the green banner Data requirements for this component have been met.

**If this occurs**

- *Syntax error near [table] after reading `TABLE("events"."ACTIVITY"), COUNT()`* -> Dimension and metric were entered in one editor. Clear the Metrics editor and keep only the COUNT formula.

*Documentation: O2-13a Dimensions and Metrics settings; O2-13b rendered bar chart.*

## O2-14 | Filter bar: Resource attribute filter

| | |
|---|---|
| **What we do** | Add an attribute filter on Resource through the filter icon. |
| **Why** | A global filter slices all components at once. |
| **Benefit** | Interactive analysis by employee or resource. |
| **Role in the project** | Makes the dashboard interactive for end users. |
| **In detail** | The filter bar is a global filter: selecting a resource once filters the KPI, table, chart and map together, which answers questions such as which cases a particular employee handled. |

**Steps**

1. Click the funnel (filter) icon at the top right.
2. Choose Attribute filter.
3. In the dialog expand Events and select Resource.
4. Click Select all (two overlapping squares) and then Apply.

**Expected result:** The top right shows 100% and Resource: 28 values selected.

*Documentation: O2-14a attribute filter dialog; O2-14b filter applied.*

## O2-15 | Define custom KPIs with PQL

| | |
|---|---|
| **What we do** | Add two custom KPIs: Order to Delivery (days) and Cancellation Rate (%). |
| **Why** | Built-in widgets provide counts. Real business questions, such as how many days pass from order to delivery and how many orders are cancelled, require a PQL formula. |
| **Benefit** | Any KPI that is needed can be defined. |
| **Role in the project** | Answers the request to show examples of defining KPIs with PQL. |
| **In detail** | PQL resembles SQL but is built for process data. CALC_THROUGHPUT computes the time between two activities (first occurrence of the source, last occurrence of the target), REMAP_TIMESTAMPS converts the time to days, and CASE WHEN counts conditionally. In a ratio, numerator and denominator must be calculated on the same table, which is why the number of cases is counted from the events table (COUNT DISTINCT of the case column). Combining these functions yields any business KPI. |

**Steps**

1. In edit mode drop a KPI card into an empty box.
2. Click + Add data or drag it here under Main KPI and enter:
   ```
   AVG(CALC_THROUGHPUT(FIRST_OCCURRENCE['place order'] TO LAST_OCCURRENCE['make delivery'], REMAP_TIMESTAMPS("events"."START TIME", DAYS)))
   ```
3. In the Metadata tab set Name Order to Delivery (days) and Unit days. If a number format with one decimal is offered under Format, select it. Click Done.
4. Drop a second KPI card and enter:
   ```
   100 * SUM(CASE WHEN "events"."ACTIVITY" = 'cancel order' THEN 1 ELSE 0 END) / COUNT(DISTINCT "events"."CASE")
   ```
5. Set Name Cancellation Rate and Unit %. Click Done.
6. Cross-check: the rate equals the number of cancel order occurrences in the OLAP table divided by 10,000 and multiplied by 100 (it equals the share of cancelled cases when a case is cancelled at most once).

**Expected result:** Order to Delivery shows 20.17 days, which matches the average of the Throughput Time Explorer in Part 3 (20.1 days). Cancellation Rate shows 12.48%, which fits the roughly 1.25K cancel order cases out of 10K cases shown in the Process Explorer.

**If this occurs**

- *Cancellation Rate is far too small (for example 1.9)* -> The numerator counts events while the denominator was taken from the cases table. Use `COUNT(DISTINCT "events"."CASE")` so that both parts of the ratio use the events table.
- *Source activity not found* -> Write the activity name exactly as it appears in the map: lowercase, in single quotes.
- *The formula is shown in red* -> Insert column names from the left Data tree instead of typing them.

*Documentation: O2-15a PQL editor of the first KPI; O2-15b PQL editor of the second KPI; O2-15c both KPIs on the dashboard.*

## O2-16 | Create a version and deploy

| | |
|---|---|
| **What we do** | Create the version and deploy once, after all components are in place. |
| **Why** | One final version keeps the release clean. |
| **Benefit** | Repeated releases are avoided. |
| **Role in the project** | Final deliverable of Part 2. |
| **In detail** | Creating one version and deploying once, after all components exist, avoids repeated releases and gives end users one stable dashboard. |

**Steps**

1. Click Create version at the top right. Keep the version number that Celonis proposes (for example 1.0.2), keep View and Knowledge Model selected and click Create Version.
2. Click Deploy and confirm.

**Expected result:** Green banner: Deployment successful - Version 1.0.2 deployed to Apps (the number depends on earlier versions).

**If this occurs**

- *No versions to deploy yet* -> Create a version first.

*Documentation: O2-16 deployment banner.*

## O2-17 | Export to Excel or CSV

| | |
|---|---|
| **What we do** | Download the OLAP table data as .xlsx or .csv. |
| **Why** | Analysts often need the same numbers in a spreadsheet. |
| **Benefit** | Shows data portability. |
| **Role in the project** | Export is controlled per component in Studio. |
| **In detail** | Export lets an analyst take the exact numbers into Excel. The option appears only when Allow exporting from table is enabled for the component. |

**Steps**

1. In the table settings check that Allow exporting from table is enabled (default). Path: Settings tab, Interactions, Export settings.
2. Hover over the table. A small toolbar appears at its top right with fullscreen, undo, a download icon and a three-dot menu.
3. Click the download icon. The menu offers .xlsx and .csv.
4. Choose a format; the file downloads.

**Expected result:** A file with the columns Activity, COUNT and Resource is downloaded.

**If this occurs**

- *No export in the column header menu* -> That menu is only for sorting and column display. Export is in the toolbar download icon.

*Documentation: O2-17a Allow exporting from table; O2-17b the .xlsx / .csv menu; O2-17c downloaded file.*

## O2-18 | Final review in Apps

| | |
|---|---|
| **What we do** | Review the complete dashboard in the published view. |
| **Why** | One last live check before the presentation. |
| **Benefit** | Final screenshots are taken from here. |
| **Role in the project** | Closing demo of Part 2. |
| **In detail** | Reviewing the dashboard live confirms that every widget is connected to the others. |

**Steps**

1. Open Apps and let the dashboard load.
2. Click a bar in the bar chart and check that the other components filter.
3. Select two or three resources in the filter, then reset.

**Expected result:** KPI 10,000, OLAP table (Activity, Case Count, Resource), bar chart, Process Explorer and filter bar are live.

*Documentation: O2-18 complete dashboard (full screen, 100% zoom).*

## Results of Part 2

- **Total cases:** 10,000 | **Components:** KPI cards, OLAP table, bar chart, Process Explorer, Resource filter (28 values), custom KPIs
- **Hierarchy:** PM26_Orders_Studio_Space, PM26_Orders_Insights_Pkg, Version 1.0.2

---

# Part 3: Object-centric concepts and a custom KPI

Until now every event belonged to one case (an order). Here order, item and package are separate objects and one event can involve several of them. Steps B3-01 to B3-08 create and deploy a perspective; steps B3-09 to B3-14 build a dashboard view with a process map, a throughput time component and KPIs.

## B3-01 | Open Objects and Events

| | |
|---|---|
| **What we do** | Open the Objects and Events layer of the pool ExampleOrderOCPM. |
| **Why** | Object-centric data is managed in the Objects and Events layer, not on the classic Data Models page. |
| **Benefit** | Objects, events and perspectives are managed in one place. |
| **Role in the project** | Part 1 and Part 2 were case-centric. Here the same process is viewed through objects. |
| **In detail** | In a case-centric model every event belongs to exactly one case. In an object-centric model one event can belong to several objects (order, item, package). That is why this model has its own layer, Objects and Events. |

**Steps**

1. Open the Data menu (left sidebar or app switcher).
2. Hover over Objects and Events. A submenu lists the data pools.
3. Click ExampleOrderOCPM. The pool dashboard opens.

**Expected result:** The dashboard shows Issues to fix in draft (0) and the message There are no issues to fix for your model. The left menu lists Dashboard, Objects, Events, Transformations, Perspectives and Catalog.

**If this occurs**

- *ExampleOrderOCPM is the only pool with objects and events* -> In the Data Pools list only ExampleOrderOCPM shows 3 Objects / 1 Events. It is an example pool provided by Celonis, so do not edit or delete its objects or events.

*Documentation: B3-01a Data menu submenu; B3-01b pool dashboard.*

## B3-02 | Inspect the object types

| | |
|---|---|
| **What we do** | Open Objects and review the object types and their attributes. |
| **Why** | Before building a perspective it is necessary to know which business objects exist. |
| **Benefit** | Missing or unexpected objects are noticed early. |
| **Role in the project** | Order, item and package are separate objects that each have their own life cycle. |
| **In detail** | An object is a business entity with its own life cycle. In a case-centric view one of them has to be picked as the case and the information about the others is lost. |

**Steps**

1. Click Objects in the left menu.
2. The list shows 3 object types: item, order and package.
3. Click item: its attributes are ID, PRODUCTNAME, WEIGHT and PRICE.

**Expected result:** Object types (3/3) and the attribute table of item.

*Documentation: B3-02a object types list; B3-02b attributes of item.*

## B3-03 | Inspect the event type

| | |
|---|---|
| **What we do** | Open Events and review the event type and its attributes. |
| **Why** | The event type defines which activities are recorded and when. |
| **Benefit** | The source of activities and time is clear. |
| **Role in the project** | First step towards understanding event-to-object (E2O) relationships. |
| **In detail** | An event type describes the kind of occurrence that is recorded. Each event is linked (E2O) to the objects it involves, so a single event can contribute to the history of an order and of an item at the same time. |

**Steps**

1. Click Events in the left menu.
2. Open the event type event. Its attributes are EVENT (primary key), ID, Time and Activities.

**Expected result:** The event type event with its attribute list.

*Documentation: B3-03 Events screen.*

## B3-04 | Open the Perspectives page

| | |
|---|---|
| **What we do** | Open Perspectives and review how a perspective is created. |
| **Why** | A perspective defines which objects and events are included in an analysis. |
| **Benefit** | The same object data can be analysed from different viewpoints. |
| **Role in the project** | The perspective is the new concept that object-centric process mining introduces. |
| **In detail** | A perspective is a viewpoint: the same data is looked at with one object as the lead. When a perspective is deployed, Celonis generates a data model from it that can be analysed. |

**Steps**

1. Click Perspectives in the left menu.
2. Read the page: View a perspective and Create a perspective. The creation flow is: select the object types, choose how they are linked, create event logs, and analyse the data model generated from the perspective.

**Expected result:** The Perspectives page with the blue + Create Perspective button at the bottom right.

*Documentation: B3-04 Perspectives introduction page.*

## B3-05 | Create the perspective

| | |
|---|---|
| **What we do** | Create a perspective named `PM26OCPMOrderPerspective`. |
| **Why** | A unique name avoids a clash with the example perspective that may already exist. |
| **Benefit** | The perspective is clearly identifiable. |
| **Role in the project** | Core object of this part. |
| **In detail** | Perspective names follow stricter rules than the names of Studio objects: letters and numbers only, beginning with a letter. |

**Steps**

1. Click the blue + Create Perspective button.
2. In the dialog enter the Perspective Name `PM26OCPMOrderPerspective`.
3. Click Create. The button stays disabled while the name is invalid.

**Expected result:** The perspective builder opens with the tabs Objects and Event logs in the left panel.

**If this occurs**

- *Perspective name must begin with a letter, and only contain alphanumeric characters* -> Remove underscores and spaces. Use letters and numbers only, starting with a letter.

*Documentation: B3-05a Create Perspective dialog with the name; B3-05b empty builder.*

## B3-06 | Add the objects to the perspective

| | |
|---|---|
| **What we do** | Add item, order and package to the perspective and click Done. |
| **Why** | Only the objects included in the perspective appear in its analysis. |
| **Benefit** | The scope of the analysis is controlled. |
| **Role in the project** | The relationship between order, item and package is what makes the object-centric view valuable. |
| **In detail** | A perspective contains only the objects added to it. Celonis detects the object-to-object relationships itself, which is why the Add button is disabled. |

**Steps**

1. In the left panel open All objects (3).
2. Click + next to item, order and package one after another. The three nodes appear on the canvas.
3. The Linked objects section shows a disabled + Add with the message All available objects have already been linked.
4. Click the blue Done button at the bottom left.

**Expected result:** The canvas shows the nodes package, order and item. A yellow banner Not all objects are connected may appear.

**If this occurs**

- *+ Add is disabled (All available objects have already been linked)* -> Not an error. Celonis already detected the relationships. Click Done.
- *Yellow banner: Not all objects are connected* -> Informational. Data permissions and filters may not apply to every object. It can be ignored here.

*Documentation: B3-06a All objects list; B3-06b three objects on the canvas.*

## B3-07 | Review the event logs and save

| | |
|---|---|
| **What we do** | Open the Event logs tab and save the perspective. |
| **Why** | Celonis creates an event log for every object automatically, so no manual selection of a lead object is needed. |
| **Benefit** | Fewer manual steps and fewer errors. |
| **Role in the project** | The perspective must be saved before it can be deployed. |
| **In detail** | An event log is the table that lists events from the viewpoint of one object. Celonis builds one per object so the analyst does not have to choose a lead object. |

**Steps**

1. Click the Event logs tab at the top of the left panel. A notice explains that event logs are created automatically for each object.
2. Click Save at the top right.
3. A green message appears: Success: Perspective successfully saved.

**Expected result:** Deploy and Create version at the top right become available.

*Documentation: B3-07a Event logs tab; B3-07b save confirmation.*

## B3-08 | Deploy the perspective

| | |
|---|---|
| **What we do** | Deploy the saved perspective to the target Development. |
| **Why** | The generated data model is created during deployment. |
| **Benefit** | The perspective is available as a deployed asset. |
| **Role in the project** | Bridge between the object layer and the analysis layer. |
| **In detail** | During deployment Celonis runs a background job that prepares the perspective. Development means the perspective is deployed in the build environment. |

**Steps**

1. Click the blue Deploy button at the top right.
2. In the dialog keep the target Development and the version shown (Version 1.0.0).
3. Click Deploy.
4. Two notifications appear: Deployment started and then Deployment successful: Version 1.0.0 deployed to Development.

**Expected result:** The top-right deployment indicator disappears once the deployment is complete.

**If this occurs**

- *The dialog shows No changes found* -> The perspective is already deployed. Cancel the dialog.

*Documentation: B3-08a Deploy dialog; B3-08b deployment notifications.*

## B3-09 | Create a new view in the example package

| | |
|---|---|
| **What we do** | In Studio open the package ExampleOrderOCPM inside the space ExampleOrder and create the new view `OCPM_Process_Overview`. |
| **Why** | The existing example view is Celonis-provided. A new view starts empty, so every component is built from scratch and the work is reproducible. |
| **Benefit** | A clean canvas and clear naming. |
| **Role in the project** | Dashboard of this part. |
| **In detail** | A package already contains Celonis' example view. Creating a new view keeps the exercise clean. The view uses the knowledge model ExampleOrders KM, which provides the order event log (Events Activity) and the tables cases and events. |

**Steps**

1. Open Studio and open the space ExampleOrder.
2. Open the package ExampleOrderOCPM.
3. In the left panel click + New asset and choose View.
4. In the Create View dialog enter the View Name `OCPM_Process_Overview` and keep the Knowledge Model ExampleOrders KM.
5. Click Create. The message View created appears and an empty canvas opens.

**Expected result:** The left panel lists OCPM_Process_Overview next to ExampleOrderOCPM View and ExampleOrders KM.

**If this occurs**

- *ExampleOrderOCPM is not offered in Create space or Create package* -> Those lists contain only case-centric data models. Do not create a new space or package. Create the view inside the existing package.
- *The pool button Create Data Model opens a classic wizard (24 raw tables)* -> That wizard is not needed. Cancel without selecting anything.

*Documentation: B3-09a New asset menu; B3-09b Create View dialog; B3-09c empty canvas.*

## B3-10 | Add the Process Explorer

| | |
|---|---|
| **What we do** | Add the Process Explorer component to the new view. |
| **Why** | It shows the order process as a map of activities and paths. |
| **Benefit** | The complete process is visible at a glance. |
| **Role in the project** | Process discovery result of this part. |
| **In detail** | The Process Explorer orders the events of the selected event log and shows which activity follows which. The Event Log dropdown allows another event log to be chosen. |

**Steps**

1. In the Components panel open Process visualizations.
2. Drag Process Explorer onto the canvas.
3. Review the map. The Event Log shown is Events Activity (Default).

**Expected result:** A process map of the orders: place order, send invoice, pay, prepare delivery, confirm payment, send reminder, make delivery, cancel order.

*Documentation: B3-10 rendered process map.*

## B3-11 | Add the Throughput Time Explorer

| | |
|---|---|
| **What we do** | Add the Throughput Time Explorer and measure the time from place order to make delivery. |
| **Why** | The process map shows what happens, the throughput time shows how long it takes. |
| **Benefit** | Delays and bottlenecks become visible. |
| **Role in the project** | Adds a performance view to the dashboard. |
| **In detail** | Throughput time is the time between two events. First and Last occurrence define which occurrence counts when an activity appears more than once. |

**Steps**

1. In Components drag Throughput Time Explorer onto the canvas.
2. In the right panel keep the Event Log Events Activity.
3. Choose place order with First in the from field.
4. Choose make delivery with Last in the to field.

**Expected result:** A histogram with the statistics avg. 20.1 days, med. 19.5 days, min. 3.38 days and max. 58.9 days.

**If this occurs**

- *The component stays empty* -> Both a source and a target event must be selected.

*Documentation: B3-11a source and target selection; B3-11b histogram and statistics.*

## B3-12 | KPI card: Total Orders

| | |
|---|---|
| **What we do** | Add a KPI card that counts all orders. |
| **Why** | A headline number gives the scale of the data. |
| **Benefit** | Quick orientation. |
| **Role in the project** | Reuses the COUNT aggregation from Part 2. |
| **In detail** | The same COUNT aggregation as in Part 2 works here, which shows that PQL principles are the same in both views. |

**Steps**

1. Drag a KPI card from KPIs onto the canvas.
2. Click + Add data or drag it here. The PQL editor opens.
3. Enter `COUNT("cases"."CASE")`.
4. The preview shows 10000 and the green banner Data requirements for this component have been met. Click Done.

**Expected result:** A KPI card with the value 10000.

**If this occurs**

- *The Name stays COUNT* -> Change it in the Metadata tab under Name.

*Documentation: B3-12a PQL editor; B3-12b KPI card.*

## B3-13 | Define a custom KPI with PQL

| | |
|---|---|
| **What we do** | Add a second KPI card with the average number of days from place order to make delivery. |
| **Why** | Built-in components do not provide every business measure. PQL allows any KPI to be defined. |
| **Benefit** | A custom KPI can be checked against the built-in Throughput Time Explorer. |
| **Role in the project** | Shows how a KPI is defined with PQL. |
| **In detail** | CALC_THROUGHPUT calculates the time between two activities, REMAP_TIMESTAMPS converts it into days and AVG averages it over all cases. Matching the built-in widget confirms that the formula is correct. |

**Steps**

1. Drag a second KPI card onto the canvas and click + Add data or drag it here.
2. Enter:
   ```
   AVG(CALC_THROUGHPUT(FIRST_OCCURRENCE['place order'] TO LAST_OCCURRENCE['make delivery'], REMAP_TIMESTAMPS("events"."START TIME", DAYS)))
   ```
3. In the Metadata tab set Name Order to Delivery (days) and Unit days.
4. Click Done.

**Expected result:** The KPI shows 20.166... days, which matches the average of 20.1 days in the Throughput Time Explorer.

**If this occurs**

- *Source activity not found* -> Write the activity name exactly as shown in the process map, in single quotes.

*Documentation: B3-13a PQL editor with the formula; B3-13b the KPI next to the Throughput Time Explorer.*

## B3-14 | Create a version and deploy

| | |
|---|---|
| **What we do** | Create version 1.0.0 of the package and deploy it. |
| **Why** | A version is the snapshot that is published. |
| **Benefit** | The dashboard is released in a controlled way. |
| **Role in the project** | Final deliverable of this part. |
| **In detail** | The routine is identical to Part 1 and Part 2: create a version, deploy, check. |

**Steps**

1. Click Create version at the top right. The new view is listed with the status added.
2. Click Create Version.
3. Click Deploy and confirm in the Deploy dialog.
4. The notifications Deployment started and Deployment successful appear.

**Expected result:** The new view is deployed.

*Documentation: B3-14a Create Version dialog; B3-14b deployment notifications.*

## Results of Part 3

- **Objects:** item, order, package | **Perspective:** PM26OCPMOrderPerspective (deployed to Development)
- **View OCPM_Process_Overview:** process map, Throughput Time Explorer (average 20.1 days, median 19.5 days), KPI Total Orders = 10000, custom KPI Order to Delivery (days) = 20.17

---

# Appendix A: PQL reference

Select table and column names from the Data tree in the PQL editor; clicking an item inserts its exact quoted name.

| Purpose | Expression | Used in |
|---|---|---|
| Total cases | `COUNT("cases"."CASE")` | O2-11, B3-12 |
| Case count (table or chart metric) | `COUNT("cases"."CASE")` | O2-12, O2-13 |
| Activity (dimension) | `"events"."ACTIVITY"` | O2-12, O2-13 |
| Resource (dimension or filter) | `"events"."Resource"` (as written in the Data tree) | O2-12, O2-14 |
| Order to Delivery (days) | `AVG(CALC_THROUGHPUT(FIRST_OCCURRENCE['place order'] TO LAST_OCCURRENCE['make delivery'], REMAP_TIMESTAMPS("events"."START TIME", DAYS)))` | O2-15, B3-13 |
| Cancellation Rate (%) | `100 * SUM(CASE WHEN "events"."ACTIVITY" = 'cancel order' THEN 1 ELSE 0 END) / COUNT(DISTINCT "events"."CASE")` | O2-15 |
| Autocomplete | Type `COUNT(` and press Ctrl + Space | O2-11 |
| New table column | SHIFT + click on an item in the Data tree | O2-12 |

> **Rule:** KPI and chart metrics always need an aggregation (COUNT, SUM, AVG). A plain column returns a list of values and causes an error.

---

# Appendix B: Key concepts

**Q1. Which three columns does an event log need?**
A case ID (which instance the event belongs to), an activity (what happened) and a timestamp (when it happened). From these Celonis orders events by case and derives paths, variants and throughput times.

**Q2. What is the difference between a Data Pool and a Data Model?**
A Data Pool is the container for data (files, tables, jobs). A Data Model is the logical schema on top of the pool that tells Celonis where case, activity and timestamp are and how tables are linked.

**Q3. Why are import and load separate steps?**
Import turns an uploaded file into a table of the pool. Load Data Model prepares that data in the in-memory process engine so Studio can query it.

**Q4. Why is the foreign key between cases and events 1:N?**
One order (case) has many events. The cases table is the dimension (one side) and the events table is the fact (many side).

**Q5. Which table is the activity table and why?**
The one in which a case has many rows, one per event: the events table. The cases table has one row per order and would turn products into activities.

**Q6. What is the difference between the Process Explorer and the Variant Explorer?**
The Process Explorer shows the complete discovered process map. The Variant Explorer shows the distinct paths cases followed, with their frequency.

**Q7. Why are versions and deployment needed?**
A version is a frozen snapshot. Deployment publishes it for end users while editing continues in edit mode.

**Q8. What is PQL and how does it differ from SQL?**
PQL is the Celonis query language for process data. It offers process functions (for example CALC_THROUGHPUT) and relies on the data model for joins.

**Q9. How is a custom KPI defined?**
With an aggregation such as COUNT, AVG or SUM. Example: `AVG(CALC_THROUGHPUT(FIRST_OCCURRENCE['place order'] TO LAST_OCCURRENCE['make delivery'], REMAP_TIMESTAMPS(timestamp, DAYS)))` returns the average days from order to delivery.

**Q10. What is a perspective?**
A viewpoint on object-centric data: which objects and events are included. After deployment Celonis generates a data model from it.

**Q11. Case-centric versus object-centric process mining?**
Case-centric assigns every event to one case, which causes two problems. Convergence: one event is copied into many cases (with items as the case, one place order event appears once per item). Divergence: one case shows the same activity many times for different objects, which looks like a loop (pick item appears 10 times in one order). Object-centric links an event to all objects it involves, so these problems do not arise.
