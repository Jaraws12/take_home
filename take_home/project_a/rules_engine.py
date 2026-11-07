"""
Hand-coded deterministic tax calculator for Indian Income Tax (FY 2024-25 & FY 2025-26).
Covers Standard Deduction, HRA Exemption, 80C, 80CCD(1B), 80D, Home Loan Interest,
Section 87A Rebate with Marginal Relief, Surcharge, and 4% Health & Education Cess.
"""

from typing import Dict, Any, Tuple

class IncomeTaxCalculator:
    def __init__(self, fy: str = "2024-25"):
        if fy not in ["2024-25", "2025-26"]:
            raise ValueError("Supported FYs are '2024-25' and '2025-26'")
        self.fy = fy

    def calculate_hra_exemption(self, basic_salary: float, hra_received: float, rent_paid: float, is_metro: bool) -> float:
        """Calculates HRA exemption under Section 10(13A)."""
        if hra_received <= 0 or rent_paid <= 0:
            return 0.0
        
        excess_rent = max(0.0, rent_paid - 0.10 * basic_salary)
        metro_cap = 0.50 * basic_salary if is_metro else 0.40 * basic_salary
        
        exemption = min(hra_received, excess_rent, metro_cap)
        return round(exemption, 2)

    def calculate_tax_from_slabs(self, taxable_income: float, slabs: list[Tuple[float, float]]) -> float:
        """Calculates base tax using progressive tax slabs."""
        tax = 0.0
        prev_limit = 0.0
        
        for limit, rate in slabs:
            if taxable_income <= prev_limit:
                break
            taxable_in_slab = min(taxable_income, limit) - prev_limit
            tax += taxable_in_slab * rate
            prev_limit = limit
            
        return round(tax, 2)

    def calculate_surcharge(self, income: float, base_tax: float, regime: str) -> float:
        """Calculates surcharge and marginal relief for high earners."""
        if income <= 5000000:
            return 0.0
        
        # Surcharge rates
        if regime == "new":
            if income <= 10000000:
                rate = 0.10
            elif income <= 20000000:
                rate = 0.15
            else:
                rate = 0.25 # New regime caps surcharge at 25%
        else:
            if income <= 10000000:
                rate = 0.10
            elif income <= 20000000:
                rate = 0.15
            elif income <= 50000000:
                rate = 0.25
            else:
                rate = 0.37

        raw_surcharge = base_tax * rate
        
        # Marginal relief calculation
        threshold = 5000000 if income <= 10000000 else (10000000 if income <= 20000000 else (20000000 if income <= 50000000 else 50000000))
        tax_at_threshold = self.calculate_tax_from_slabs(threshold, self._get_slabs(regime))
        excess_income = income - threshold
        max_tax_increase = base_tax + raw_surcharge - tax_at_threshold
        
        if max_tax_increase > excess_income:
            surcharge = max(0.0, excess_income - (base_tax - tax_at_threshold))
        else:
            surcharge = raw_surcharge

        return round(surcharge, 2)

    def _get_slabs(self, regime: str) -> list[Tuple[float, float]]:
        if regime == "old":
            return [
                (250000, 0.0),
                (500000, 0.05),
                (1000000, 0.20),
                (float('inf'), 0.30)
            ]
        else:
            if self.fy == "2024-25":
                return [
                    (300000, 0.0),
                    (700000, 0.05),
                    (1000000, 0.10),
                    (1200000, 0.15),
                    (1500000, 0.20),
                    (float('inf'), 0.30)
                ]
            else: # FY 2025-26 updated slabs
                return [
                    (400000, 0.0),
                    (800000, 0.05),
                    (1200000, 0.10),
                    (1600000, 0.15),
                    (2000000, 0.20),
                    (2400000, 0.25),
                    (float('inf'), 0.30)
                ]

    def compute_tax(self, details: Dict[str, Any]) -> Dict[str, Any]:
        """Calculates total tax for both regimes with complete breakdown."""
        gross_salary = details.get("gross_salary", 0.0)
        basic_salary = details.get("basic_salary", gross_salary * 0.5)
        hra_received = details.get("hra_received", 0.0)
        rent_paid = details.get("rent_paid", 0.0)
        is_metro = details.get("is_metro", False)
        
        # Deductions
        sec_80c = min(150000.0, details.get("sec_80c", 0.0))
        sec_80ccd_1b = min(50000.0, details.get("sec_80ccd_1b", 0.0))
        
        # 80D Limits (Self + Parents)
        sec_80d_self = min(50000.0 if details.get("self_senior", False) else 25000.0, details.get("sec_80d_self", 0.0))
        sec_80d_parents = min(50000.0 if details.get("parents_senior", False) else 25000.0, details.get("sec_80d_parents", 0.0))
        sec_80d_total = sec_80d_self + sec_80d_parents
        
        home_loan_interest = min(200000.0, details.get("home_loan_interest", 0.0))

        # --- OLD REGIME ---
        std_ded_old = 50000.0
        hra_exemption = self.calculate_hra_exemption(basic_salary, hra_received, rent_paid, is_metro)
        total_deductions_old = std_ded_old + hra_exemption + sec_80c + sec_80ccd_1b + sec_80d_total + home_loan_interest
        taxable_old = max(0.0, gross_salary - total_deductions_old)
        
        base_tax_old = self.calculate_tax_from_slabs(taxable_old, self._get_slabs("old"))
        
        # 87A Rebate (Old)
        rebate_old = 0.0
        if taxable_old <= 500000:
            rebate_old = min(base_tax_old, 12500.0)
        
        tax_after_rebate_old = base_tax_old - rebate_old
        surcharge_old = self.calculate_surcharge(taxable_old, tax_after_rebate_old, "old")
        cess_old = round((tax_after_rebate_old + surcharge_old) * 0.04, 2)
        total_tax_old = round(tax_after_rebate_old + surcharge_old + cess_old, 2)

        # --- NEW REGIME ---
        std_ded_new = 75000.0 if self.fy == "2025-26" else 75000.0 # Standard deduction in new regime
        taxable_new = max(0.0, gross_salary - std_ded_new)
        
        base_tax_new = self.calculate_tax_from_slabs(taxable_new, self._get_slabs("new"))
        
        # 87A Rebate & Marginal Relief (New)
        rebate_new = 0.0
        rebate_threshold = 1200000.0 if self.fy == "2025-26" else 700000.0
        max_rebate = 60000.0 if self.fy == "2025-26" else 25000.0
        
        if taxable_new <= rebate_threshold:
            rebate_new = min(base_tax_new, max_rebate)
        elif self.fy == "2024-25" and 700000 < taxable_new <= 727777: # Marginal relief under 87A for New Regime
            excess = taxable_new - 700000
            if base_tax_new > excess:
                rebate_new = base_tax_new - excess

        tax_after_rebate_new = base_tax_new - rebate_new
        surcharge_new = self.calculate_surcharge(taxable_new, tax_after_rebate_new, "new")
        cess_new = round((tax_after_rebate_new + surcharge_new) * 0.04, 2)
        total_tax_new = round(tax_after_rebate_new + surcharge_new + cess_new, 2)

        recommended = "New Regime" if total_tax_new <= total_tax_old else "Old Regime"

        return {
            "financial_year": self.fy,
            "old_regime": {
                "taxable_income": taxable_old,
                "base_tax": base_tax_old,
                "rebate": rebate_old,
                "surcharge": surcharge_old,
                "cess": cess_old,
                "total_tax": total_tax_old
            },
            "new_regime": {
                "taxable_income": taxable_new,
                "base_tax": base_tax_new,
                "rebate": rebate_new,
                "surcharge": surcharge_new,
                "cess": cess_new,
                "total_tax": total_tax_new
            },
            "recommended_regime": recommended,
            "savings": abs(total_tax_old - total_tax_new)
        }