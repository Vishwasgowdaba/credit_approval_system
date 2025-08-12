import math
from datetime import date

def emi_amount(principal, annual_rate_percent, tenure_months):
    if tenure_months == 0:
        return 0
    if annual_rate_percent <= 0:
        return round(principal / tenure_months,2)
    r = annual_rate_percent / 100 / 12
    n = tenure_months
    emi = principal * r * (1 + r)**n / ((1 + r)**n - 1)
    return round(emi,2)

def nearest_lakh(value):
    lakh = 100000
    return round(value / lakh) * lakh

def compute_credit_score(customer, loans):
    score = 50
    total_loans = len(loans)
    if total_loans == 0:
        score += 20
    else:
        score += max(0, 10 - total_loans)
    on_time = sum(1 for l in loans if getattr(l,'emis_paid_on_time',0) > 0)
    if total_loans>0:
        ratio = on_time/total_loans
        score += int(ratio*30)
    current_year = date.today().year
    activity = sum(1 for l in loans if (getattr(l,'start_date',None) and l.start_date.year==current_year))
    score += min(activity*2,10)
    volume = sum(getattr(l,'loan_amount',0) for l in loans)
    if volume > customer.approved_limit:
        return 0
    if volume > customer.approved_limit*0.5:
        score -= 15
    return max(0, min(100, score))
