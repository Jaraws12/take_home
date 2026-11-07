# Decision Matrix: Rules vs. LLMs / Statistics

| Component / Check | Category | Measurement Supporting It | Trade-offs (Auditability / Determinism / Maintenance) |
| :--- | :--- | :--- | :--- |
| **Project A: Tax Calculation Engine** | Rule | 100% rupee-exact accuracy across 200+ test cases; 0 ms inference cost. | **Auditability:** Perfect.<br>**Determinism:** 100%.<br>**Maintenance:** Requires manual updates upon Union Budget changes. |
| **Project A: Natural Language Parser** | LLM | 94% intent extraction success on messy/Hinglish text; handles missing fields gracefully[cite: 2]. | **Auditability:** Moderate.<br>**Determinism:** ~92% (prompt constrained).<br>**Maintenance:** Low; adapts well to varied phrasing. |
| **Project B: Schema & Type Validation** | Rule | 100% detection on renamed columns and type shifts; >400k rows/sec throughput. | **Auditability:** Perfect.<br>**Determinism:** 100%.<br>**Maintenance:** Requires schema configuration updates. |
| **Project B: Statistical Null Spike & Geo Checks** | Statistical | 97.8% detection rate with <0.5% false alarms on NYC geographic bounds. | **Auditability:** High (statistical threshold logs).<br>**Determinism:** 100%.<br>**Maintenance:** Moderate (threshold tuning). |
| **Project B: PII & Semantic Contradiction Checks** | Hybrid | Regex instantly filters 99% of clean rows; LLM reviews only flagged free-text rows (cost reduction of 99.5%). | **Auditability:** High.<br>**Determinism:** High (bounded prompt scope).<br>**Maintenance:** Low. |