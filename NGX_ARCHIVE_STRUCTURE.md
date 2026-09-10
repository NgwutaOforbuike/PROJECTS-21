# NGX Issuer Intelligence Vault — Permanent Structure

## Objective
Maintain a professional, transaction-ready archive for investment research, public M&A, capital markets, financing, corporate actions, governance review and historical diligence.

## Permanent issuer structure

`01_ISSUER_INTELLIGENCE_VAULT/<COMPANY> [<TICKER>]/`

- `00_Company_Profile_and_Identifiers/`
  - Company profile
  - Ticker/ISIN history
  - Incorporation and listing information
  - Sector/sub-sector/board classification
  - Registrar/auditor/company secretary/registered office
  - Name changes and predecessor/successor entities
  - Coverage register
- `01_Listing_Capital_and_Ownership_History/`
  - Listing/admission documents
  - Share-capital changes
  - Rights issues, public offers, placements, bonus/splits/consolidations
  - Significant ownership and shareholder disclosures
  - Delisting/relisting/migration records
- `02_Filings_By_Year/<YYYY>/`
  - `01_Audited_Annual_Reports/`
  - `02_Interim_and_Quarterly_Financials/`
  - `03_Corporate_Actions_and_Dividends/`
  - `04_Governance_Board_and_Director_Dealings/`
  - `05_AGM_EGM_and_Shareholder_Matters/`
  - `06_Capital_Raising_and_Securities_Issuance/`
  - `07_Debt_Bonds_Commercial_Paper_and_Credit/`
  - `08_MA_Restructuring_Schemes_and_Strategic_Transactions/`
  - `09_Regulatory_Compliance_Litigation_and_Enforcement/`
  - `10_Material_Announcements_and_Other_Disclosures/`
- `03_Transaction_Readiness/`
  - Change-of-control analysis
  - Takeover/mandatory-tender considerations
  - Free-float/listing-rule issues
  - Material consents and approvals
  - Security/debt covenant flags
  - Related-party and governance flags
- `04_Research_and_Valuation/`
  - Normalised financial series
  - Valuation work
  - Earnings/cash-flow history
  - Peer/sector comparisons
  - Event-study outputs
- `05_Risk_and_Red_Flags/`
  - Filing gaps
  - Late filings
  - Restatements
  - Regulatory breaches
  - Litigation/default/distress
  - Going-concern/audit qualifications
  - Governance issues

## Coverage rule
The issuer coverage register runs from the verified NGX listing year to the current year. A year is marked Complete, Partial, No Public Filing Found, Pre-Archive Gap, or Listing Date Unresolved. Empty year folders are not created merely for appearance; year folders are created when source material exists, while the coverage register preserves the full chronological record.

## Source rule
Primary NGX/issuer/regulator documents are preserved in raw form. ZIPs are temporary transfer containers only and are not the permanent browsing format. Individual PDFs are stored in the correct company/year/category path after verification.
