from decimal import Decimal
import pandas as pd


class Amoritize:
    """
    A class used to calculate loan payments and total interest paid

    - some floats are converted to Decimal types for accounting and compatibility purposes
      - See https://realpython.com/python-rounding/#the-decimal-class for more details

    Attributes
    ----------

    total_interest : decimal.Decimal
        The total intrest paid on the loan
    bal : float
        The orignal loan balance
    pv : Decimal
        The present value of the loan
    apr: float
        The annual percentage rate
    n : int
        The number of payments
    mpr : Decimal
        The monthly periodic rate
    dpr : Decimal
        The daily periodic rate
    """

    total_interest = Decimal(0)

    def __init__(self, bal, apr, n):
        """
        Paramaters
        ----------

        bal : float
            The original loan balance
        apr: float
            The annual percentage rate
        n : int
            The number of payments
        """

        self.bal = bal
        self.pv = Decimal(bal).quantize(Decimal('0.00'))
        self.apr = apr
        self.n = n
        self.mpr = Decimal(apr / 12)
        self.dpr = Decimal(apr / 365)

    def calculate_pmt(self):
        """
        Calculates the monthly periodic payment
        """
        return Decimal(self.pv * (self.mpr / (1 - (1 + self.mpr) ** -self.n))).quantize(Decimal('0.00'))

    def calculate_interest_due(self):
        """
        Calculates the interest due for the current month
        """
        return Decimal(self.pv * self.mpr).quantize(Decimal('0.00'))

    def calculate_principal_paid(self, pmt, interest):
        """
        Calculates the principal paid for the current month
        """
        return Decimal(pmt - interest).quantize(Decimal('0.00'))

    def calculate_new_balance(self, principal_paid):
        """
        Calculates the new blance of the loan by substracting the principal paid from pv
        """
        return Decimal(self.pv - principal_paid).quantize(Decimal('0.00'))

    # creates an amoritization schedule
    def schedule(self):
        """
        Creates an amoritization schedule
        """

        count = self.n
        pmt = self.calculate_pmt()

        # list of of every payment
        payments = []

        # compute the interest paid, pricinpal paid, and the updated present-value for each month
        while count > 0:
            monthly_interest = self.calculate_interest_due()
            principal_paid = self.calculate_principal_paid(
                pmt, monthly_interest)
            updated_balance = self.calculate_new_balance(principal_paid)

            # for the last payment, we need to account for rounding the montly payment and interest
            if count == 1 and updated_balance > 0:
                pmt += updated_balance
                principal_paid = self.calculate_principal_paid(
                    pmt, monthly_interest)
                updated_balance = self.calculate_new_balance(principal_paid)

            # update present value
            self.pv = updated_balance

            # create dictoinary of values for this month
            month = {
                'payment': float(pmt),
                'interest': float(monthly_interest),
                'principal_paid': float(principal_paid),
                'present_value': float(self.pv)
            }

            # add current month to list of payments
            payments.append(month)

            # update total intrest
            self.total_interest += monthly_interest

            # decrement month counter
            count -= 1

        response = {
            'payments': payments,
            'total_interest': float(self.total_interest)
        }

        return response


test = Amoritize(32397.75, 0.10313, 39)
test_schedule = test.schedule()

final_month = test_schedule['payments'][-1]
total_interest = test_schedule['total_interest']

assert final_month == {'present_value': 0.0, 'payment': 981.28, 'interest': 8.36, 'principal_paid': 972.92}
assert total_interest == 5869.89

payments = pd.DataFrame(test_schedule['payments'])

print()
print('Last 5 Months')
print('-' * 30)
print(payments.tail())
print()

print('Total Interest Paid')
print('-' * 30)
print(total_interest)
print()