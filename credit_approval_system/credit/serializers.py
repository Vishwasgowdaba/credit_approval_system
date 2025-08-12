from rest_framework import serializers
from .models import Customer, Loan
class CustomerSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    class Meta:
        model = Customer
        fields = ['customer_id','first_name','last_name','name','age','monthly_salary','approved_limit','phone_number']
    def get_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"

class LoanSerializer(serializers.ModelSerializer):
    class Meta:
        model = Loan
        fields = ['loan_id','customer','loan_amount','tenure','interest_rate','monthly_repayment','emis_paid_on_time','start_date','end_date','is_active']
