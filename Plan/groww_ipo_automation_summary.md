# Summary: Groww IPO Automation Discussion

## Overview
Discussion regarding whether IPO applications can be automated programmatically via the Groww platform or broker APIs within the Personal Assistant project.

## Key Points & Findings
1. **Official API Limitations:** 
   - Groww's official Trading APIs (and community SDK wrappers like `growwapi`) are strictly restricted to secondary market activities (Stocks, F&O, MTF, market data, and portfolio management).
   - They do **not** provide endpoints or developer methods for submitting or triggering retail IPO bids.

2. **Regulatory Constraints (SEBI & NPCI):**
   - Retail IPO applications in India require a **UPI Mandate** authorization (explicit user consent and UPI PIN entry). Automated scripts/bots cannot bypass this compliance check.

3. **Alternative Approaches Discussed:**
   - **Assistant as an Intelligence Hub:** Tracking IPO calendars, fetching Grey Market Premium (GMP) data, setting up notification alerts, and checking allotment status via registrars (Link Intime, KFintech).
   - **Browser Automation (Playwright/Selenium):** Technically possible to simulate UI clicks up to the UPI mandate popup, but highly fragile due to OTPs, captchas, UI updates, and Terms of Service (ToS) violations.
