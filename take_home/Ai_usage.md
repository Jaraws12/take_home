# AI Usage & Verification Log

## 1. AI Tools Utilized
* **Google Gemini (Flash 2.5):** Used for generating boilerplate test cases, drafting complex regular expressions for free-text parsing, and assisting in structuring Markdown documentation reports.
* **GitHub Copilot / Coding Agent:** Used for accelerating syntax completion during Python class design for Project B's data corruption injector.

---

## 2. Mandatory AI Failure Analysis & Verification

* **Where the AI was wrong:** 
  During the development of Project A's tax calculation rules under FY 2025-26 regulations, the LLM-assisted drafting code initially proposed a simplified marginal relief formula for Section 87A rebate thresholds. Specifically, it failed to account for the exact marginal tax cliff where total tax payable exceeds the marginal income increment above the ₹12,00,000 threshold.
  
* **How we caught it:** 
  While running our automated test suite (`project_a/tests/test_calculator.py`) against edge-case test case #42 (an income of ₹12,40,000), our unit test flagged a discrepancy when comparing the output against the official Income Tax Department calculator reference value. 

* **How it was fixed:** 
  We discarded the AI's simplified heuristic formula and replaced it with a rigorous, hand-coded deterministic boundary check that computes exact marginal relief as `max(0.0, raw_tax - (taxable_income - rebate_threshold))`, ensuring 100% rupee-exact compliance.