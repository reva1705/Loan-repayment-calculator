import pandas as pd


def emi(principal, annual_rate, years, periods_per_year=12):
    """Return the fixed repayment per period for an amortising loan."""
    r = annual_rate / 100 / periods_per_year
    n = years * periods_per_year

    if r == 0:
        return principal / n

    growth = (1 + r) ** n
    return principal * r * growth / (growth - 1)


def loan_summary(principal, annual_rate, years, periods_per_year=12):
    """Return the repayment, total paid and total interest."""
    payment = emi(principal, annual_rate, years, periods_per_year)
    n = years * periods_per_year
    total_paid = payment * n
    total_interest = total_paid - principal
    return {
        "repayment": payment,
        "total_paid": total_paid,
        "total_interest": total_interest,
    }


def schedule(principal, annual_rate, years, periods_per_year=12):
    """Return a period-by-period amortisation schedule as a DataFrame."""
    r = annual_rate / 100 / periods_per_year
    n = years * periods_per_year
    payment = emi(principal, annual_rate, years, periods_per_year)

    balance = principal
    rows = []
    for period in range(1, n + 1):
        interest = balance * r
        principal_paid = payment - interest
        balance = balance - principal_paid
        rows.append({
            "period": period,
            "payment": payment,
            "interest": interest,
            "principal": principal_paid,
            "balance": balance,
        })

    return pd.DataFrame(rows)


if __name__ == "__main__":
    pd.options.display.float_format = "{:,.2f}".format
    pd.options.display.width = 120

    # (name, principal, annual rate %, years, periods per year)
    scenarios = [
        ("Home loan, 30 yrs monthly", 500000, 6, 30, 12),
        ("Home loan, 25 yrs monthly", 500000, 6, 25, 12),
        ("Home loan, 30 yrs fortnightly", 500000, 6, 30, 26),
        ("Car loan, 5 yrs", 30000, 8.5, 5, 12),
        ("Interest-free, 2 yrs", 20000, 0, 2, 12),
    ]

    results = []
    for name, principal, rate, years, freq in scenarios:
        s = loan_summary(principal, rate, years, freq)
        results.append({"scenario": name, **s})

    comparison = pd.DataFrame(results).set_index("scenario")
    print(comparison)

    # Final balance check: every loan should end at zero
    print("\nFinal balance check:")
    for name, principal, rate, years, freq in scenarios:
        final = schedule(principal, rate, years, freq)["balance"].iloc[-1]
        print(f"  {name}: {abs(final):.2f}")

