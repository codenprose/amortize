import pandas as pd
from decimal import Decimal
from datetime import date
from dateutil.relativedelta import relativedelta


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

    def __init__(self, bal, apr, n, start_date):
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

        self.bal = Decimal(bal).quantize(Decimal("0.00"))
        self.pv = Decimal(bal).quantize(Decimal("0.00"))
        self.apr = apr
        self.n = n
        self.mpr = Decimal(apr / 12)
        self.dpr = Decimal(apr / 365)
        self.date = date(start_date["year"], start_date["month"], start_date["day"])

    def calculate_pmt(self):
        """
        Calculates the monthly periodic payment
        """
        return Decimal(self.pv * (self.mpr / (1 - (1 + self.mpr) ** -self.n))).quantize(
            Decimal("0.00")
        )

    def calculate_interest_due(self):
        """
        Calculates the interest due for the current month
        """
        return Decimal(self.pv * self.mpr).quantize(Decimal("0.00"))

    def calculate_principal_paid(self, pmt, interest):
        """
        Calculates the principal paid for the current month
        """
        return Decimal(pmt - interest).quantize(Decimal("0.00"))

    def calculate_new_balance(self, principal_paid):
        """
        Calculates the new blance of the loan by substracting the principal paid from pv
        """
        return Decimal(self.pv - principal_paid).quantize(Decimal("0.00"))

    # creates an amoritization schedule
    def schedule(self):
        """
        Creates an amoritization schedule
        """

        counter = self.n
        month_counter = 0
        pmt = self.calculate_pmt()

        # list of of every payment
        schedule = []

        # compute the interest paid, pricinpal paid, and the updated present-value for each month
        while counter > 0:
            monthly_interest = self.calculate_interest_due()
            principal_paid = self.calculate_principal_paid(pmt, monthly_interest)
            updated_balance = self.calculate_new_balance(principal_paid)

            # for the last payment, we need to account for rounding the montly payment and interest
            if counter == 1 and updated_balance > 0:
                pmt += updated_balance
                principal_paid = self.calculate_principal_paid(pmt, monthly_interest)
                updated_balance = self.calculate_new_balance(principal_paid)

            # update present value
            self.pv = updated_balance

            # create dictoinary of values for this month
            date = self.date + relativedelta(months=+month_counter)
            month = {
                "payment": float(pmt),
                "interest": float(monthly_interest),
                "principal_paid": float(principal_paid),
                "present_value": float(self.pv),
                "date": date.isoformat(),
            }

            # add current month to list of payments
            schedule.append(month)

            # update total intrest
            self.total_interest += monthly_interest

            # decrement month counter
            counter -= 1

            ## increment month counter
            month_counter += 1

        response = {
            "balance": self.bal,
            "apr": self.apr,
            "monthly_payment": pmt,
            "schedule": schedule,
            "total_interest": float(self.total_interest),
            "total_cost": float(self.bal + self.total_interest),
        }

        return response


test = Amoritize(32397.75, 0.065, 39, {"year": 2019, "month": 7, "day": 1})
test_schedule = test.schedule()

payments = pd.DataFrame(test_schedule["schedule"])
# print(payments.to_json(orient='records'))

print()
print("Last 5 Months")
print("-" * 30)
print(payments.tail())
print()
