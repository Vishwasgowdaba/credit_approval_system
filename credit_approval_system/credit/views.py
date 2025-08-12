from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Customer, Loan
from .serializers import CustomerSerializer, LoanSerializer
from .utils import emi_amount, nearest_lakh, compute_credit_score
from django.shortcuts import get_object_or_404

class RegisterView(APIView):
    def post(self, request):
        data = request.data
        first = data.get('first_name')
        last = data.get('last_name')
        age = data.get('age')
        salary = float(data.get('monthly_income') or data.get('monthly_salary') or 0)
        phone = str(data.get('phone_number'))
        approved = nearest_lakh(36*salary)
        customer = Customer.objects.create(first_name=first,last_name=last,age=age,monthly_salary=salary,approved_limit=approved,phone_number=phone)
        ser = CustomerSerializer(customer)
        return Response(ser.data, status=status.HTTP_201_CREATED)

class CheckEligibilityView(APIView):
    def post(self, request):
        cid = request.data.get('customer_id')
        loan_amount = float(request.data.get('loan_amount',0))
        interest = float(request.data.get('interest_rate',0))
        tenure = int(request.data.get('tenure',12))
        customer = get_object_or_404(Customer, customer_id=cid)
        loans = list(customer.loans.all())
        score = compute_credit_score(customer, loans)
        total_emi = sum([l.monthly_repayment for l in loans if l.is_active])
        if total_emi > 0.5 * customer.monthly_salary:
            return Response({'customer_id': cid, 'approval': False, 'message': 'Total EMIs exceed 50% of salary'}, status=200)
        corrected_interest = interest
        approval = False
        if score > 50:
            approval = True
        elif score > 30:
            if interest >= 12:
                approval = True
            else:
                corrected_interest = 12.0
        elif score > 10:
            if interest >= 16:
                approval = True
            else:
                corrected_interest = 16.0
        else:
            approval = False
        if sum([l.loan_amount for l in loans if l.is_active]) > customer.approved_limit:
            approval = False
            score = 0
        monthly_installment = emi_amount(loan_amount, corrected_interest, tenure)
        return Response({'customer_id': cid,'approval': approval,'interest_rate': interest,'corrected_interest_rate': corrected_interest,'tenure': tenure,'monthly_installment': monthly_installment,'credit_score': score})

class CreateLoanView(APIView):
    def post(self, request):
        cid = request.data.get('customer_id')
        loan_amount = float(request.data.get('loan_amount',0))
        interest = float(request.data.get('interest_rate',0))
        tenure = int(request.data.get('tenure',12))
        customer = get_object_or_404(Customer, customer_id=cid)
        from .views import CheckEligibilityView
        resp = CheckEligibilityView().post(request)
        approval = resp.data.get('approval')
        corrected = resp.data.get('corrected_interest_rate')
        if not approval:
            return Response({'loan_id': None,'customer_id': cid,'loan_approved': False,'message': resp.data.get('message','Not approved'),'monthly_installment': None}, status=200)
        emi = emi_amount(loan_amount, corrected, tenure)
        loan = Loan.objects.create(customer=customer, loan_amount=loan_amount, tenure=tenure, interest_rate=corrected, monthly_repayment=emi, is_active=True)
        return Response({'loan_id': loan.loan_id,'customer_id': cid,'loan_approved': True,'message': 'Loan approved','monthly_installment': emi}, status=201)

class ViewLoanView(APIView):
    def get(self, request, loan_id):
        loan = get_object_or_404(Loan, loan_id=loan_id)
        loan_ser = LoanSerializer(loan)
        cust = CustomerSerializer(loan.customer).data
        out = loan_ser.data
        out['customer'] = {'customer_id': cust['customer_id'],'first_name': cust['first_name'],'last_name': cust['last_name'],'phone_number': cust['phone_number'],'age': cust.get('age')}
        return Response(out)

class ViewLoansByCustomerView(APIView):
    def get(self, request, customer_id):
        customer = get_object_or_404(Customer, customer_id=customer_id)
        loans = customer.loans.filter(is_active=True)
        items = []
        for l in loans:
            items.append({'loan_id': l.loan_id,'loan_amount': l.loan_amount,'interest_rate': l.interest_rate,'monthly_installment': l.monthly_repayment,'repayments_left': max(0, l.tenure)})
        return Response(items)
