from celery import shared_task
import pandas as pd
from .models import Customer, Loan
from .utils import emi_amount, nearest_lakh

@shared_task
def ingest_customers_from_excel(path):
    df = pd.read_excel(path)
    created = 0
    for _, row in df.iterrows():
        sal = float(row.get('monthly_salary', row.get('monthly_income',0) or 0))
        approved = nearest_lakh(36*sal)
        c, _ = Customer.objects.update_or_create(
            phone_number=str(row.get('phone_number') or row.get('phone','')),
            defaults={
                'first_name': row.get('first_name','').strip(),
                'last_name': row.get('last_name','').strip(),
                'monthly_salary': sal,
                'approved_limit': approved,
                'current_debt': row.get('current_debt',0) or 0,
            }
        )
        created += 1
    return {'created': created}

@shared_task
def ingest_loans_from_excel(path):
    df = pd.read_excel(path)
    created = 0
    for _, row in df.iterrows():
        try:
            cust_id = int(row.get('customer_id') or row.get('customer id'))
            customer = Customer.objects.filter(customer_id=cust_id).first()
            if not customer:
                continue
            loan_amount = float(row.get('loan amount') or row.get('loan_amount') or 0)
            tenure = int(row.get('tenure') or 12)
            interest = float(row.get('interest rate') or row.get('interest_rate') or 0)
            emi = emi_amount(loan_amount, interest, tenure)
            l, _ = Loan.objects.update_or_create(
                # update_or_create by unique natural key not implemented here, using create
                defaults={
                    'customer': customer,
                    'loan_amount': loan_amount,
                    'tenure': tenure,
                    'interest_rate': interest,
                    'monthly_repayment': emi,
                    'emis_paid_on_time': int(row.get('EMIs paid on time') or row.get('emis_paid_on_time') or 0),
                    'start_date': pd.to_datetime(row.get('start date') or row.get('start_date')).date() if row.get('start date') else None,
                    'end_date': pd.to_datetime(row.get('end date') or row.get('end_date')).date() if row.get('end date') else None,
                }
            )
            created += 1
        except Exception:
            continue
    return {'created': created}
