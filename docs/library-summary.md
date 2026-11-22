# The document library in one table

**Shaped with Kyle on November 22, 2026.** This is the summary to use whenever the library is described: one total, broken down by what the documents are and how far along they are. Who collected a document, or when, is not part of the picture.

| | Sets | Docs | Contracts | Amend-ments | SOWs | Rate cards | Invoices, time-sheets | Other | | Read by the engine | Likely to contain rates (estimate) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Contract sets | 228 | 363 | 237 | 52 | 19 | 24 | 13 | 18 | | 9 | 40 to 80 |
| Other references | 20 | 73 | 11 | | 3 | 9 | | 50 | | 0 | 10 to 20 |
| **Total** | **248** | **436** | **248** | **52** | **22** | **33** | **13** | **68** | | **9** | **50 to 100** |

## How to read it

- **A document** is one file: one PDF or one web page. There are 436 distinct documents (438 files on disk; two are duplicates).
- **A contract set** is one agreement between one vendor and one client, with every document that belongs to it: the main agreement, its amendments, the SOWs under it, its pricing exhibits. The plain answer to "how many contracts do we have" is **about 228**.
- **Other references** are documents with no vendor named, so they are not a contract between two parties: solicitations and templates (the documents a government publishes before choosing a vendor), published rate lists that cover many vendors at once (Texas, New York, US federal, Canadian wage data), role and level definitions, and 14 contracts whose vendor the catalogue did not record and which will move up once the engine reads them.
- **The six columns from Contracts to Other add up to Docs** in every row; each document is exactly one kind. "Contracts" there means the main agreement document (a master agreement, a signed contract, a services agreement). "Other" is solicitations, templates, reference documents and a few unlabelled items.
- **Read by the engine** stands apart from the kinds: 9 documents, from three contract sets (Texas DIR and Accenture, 7 of its 21; the Accenture UK G-Cloud rate card; Michigan and Deloitte).
- **Likely to contain rates** is an estimate, deliberately a range. The Rate cards column counts only documents that *are* rate cards; rate tables also sit inside contracts, SOWs and invoices (the Michigan and Deloitte contract gave 42 rates). About 39 of the company contracts filed with the SEC mention rates but have the figures blanked out; those give terms and conditions, not rates.

## Behind the first row

Of the 228 contract sets, 55 have more than one document and 173 have just one.

| Contract sets | Sets | Docs |
|---|---|---|
| Large (10 or more documents): UK Dept for Work and Pensions with IBM and Oracle; Texas DIR with Accenture | 2 | 45 |
| Medium (3 to 9 documents) | 16 | 71 |
| Two documents | 37 | 74 |
| One document | 173 | 173 |
| **Total** | **228** | **363** |

Three documents have no readable text at all (scanned pages saved as pictures) and need Azure's document reader: two UK rate exhibits and one Michigan contract.

## Keeping it current

The counts come from the catalogue and the files on disk. The "read by the engine" column changes with every run, and the "likely to contain rates" range is to be replaced by a measured count from the engine's own table detector (first run started November 22, 2026). Update this file when either changes, and after the full run.
