Transaction processing
============================

The raw transaction data is persisted to the database. However, raw transactions are processed in three ways after receipt:

Counterparty name
-----------------
By default, the counterparty name assigned by the bank is displayed. This display name can be adjusted e.g. *Pizza biz plc* becomes *Pizza Hut*. Secondly, a display name can be assigned based on a pattern e.g. *DWP 4376564*, *DWP 4634236*, etc. become *DWP*.

Category
--------
A simple feature to organise transactions by category is provided. Categories are mapped to counterparties and automatically assigned to new transactions. Categories can be overridden for each transaction e.g. a *Sainsbury's* counterparty that maps to *Essential/Groceries* may be reassigned to *Discretionary/Petrol*.

Processing sequence
-------------------
Transactions are processed as follows:

1. New transactions for a time interval are retrieved from the financial provider and stored.

2. Counterparty names for each transaction are compared to a table of existing whole- or part-name mappings. If a match is found, the display name is set to the mapped value. Otherwise, it's set to the raw value.

3. Display names are compared to a table of existing category mappings. If a match is found, the category is set to the mapped value. Otherwise, it's set to "unassigned.".

4. API endpoints are provided to set and alter counterparty display name and category mappings.

