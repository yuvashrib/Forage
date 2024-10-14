from flask import Flask, render_template, request
import csv

app = Flask(__name__)

def load_financial_data(filename):
    companies = {}
    with open(filename, mode='r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            company_name = row['Company'].lower()
            year = row['Fiscal Year']
            if company_name not in companies:
                companies[company_name] = {}
            companies[company_name][year] = {
                "revenue": int(row['Total Revenue']),
                "net_income": int(row['Net Income']),
                "cash_flow": float(row['Cash Flow from Operating Activities']),
                "assets": int(row['Total Assets']),
                "liabilities": int(row['Total Liabilities']),
                "net_income_growth": float(row['Net Income Growth (%)']),
                "previous_net_income": int(row['Net Income']) if int(year) > 2021 else None,
                "previous_year": str(int(year) - 1) if int(year) > 2021 else None,
            }
    return companies

companies = load_financial_data('Financial Data.csv')

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/query', methods=['POST'])
def query():
    user_input = request.form['query'].strip().lower()
    year = request.form['year'].strip()
    response = ""

    # Normalize year input
    year = str(year)  # Ensure it's treated as a string for comparison

    if "total revenue" in user_input:
        company_name = user_input.split("for")[-1].strip()
        if company_name in companies and year in companies[company_name]:
            revenue = companies[company_name][year]['revenue']
            response = f"{company_name.capitalize()} {year}: The total revenue was ${revenue} million."
        else:
            response = "Company or year not found. Please try again."
    elif "net income changed" in user_input:
        company_name = user_input.split("for")[-1].strip()
        if company_name in companies and year in companies[company_name] and companies[company_name][year]['previous_year']:
            previous_year = companies[company_name][year]['previous_year']
            previous_income = companies[company_name][previous_year]['net_income']
            current_income = companies[company_name][year]['net_income']
            change_percentage = ((current_income - previous_income) / previous_income) * 100
            response = f"{company_name.capitalize()}: Net income changed by {change_percentage:.2f}% from ${previous_income} million to ${current_income} million."
        else:
            response = "Company not found or previous year data not available. Please try again."
    elif "cash flow" in user_input:
        company_name = user_input.split("for")[-1].strip()
        if company_name in companies and year in companies[company_name]:
            cash_flow = companies[company_name][year]['cash_flow']
            response = f"{company_name.capitalize()} {year}: Cash flow from operating activities was ${cash_flow} million."
        else:
            response = "Company or year not found. Please try again."
    elif "income growth percentage" in user_input:
        company_name = user_input.split("for")[-1].strip()
        if company_name in companies and year in companies[company_name]:
            net_income_growth = companies[company_name][year]['net_income_growth']
            response = f"{company_name.capitalize()} {year}: The net growth was {net_income_growth:.2f} %."
        else:
            response = "Company or year not found. Please try again."
    elif "total assets and liabilities" in user_input:
        company_name = user_input.split("for")[-1].strip()
        if company_name in companies and year in companies[company_name]:
            assets = companies[company_name][year]['assets']
            liabilities = companies[company_name][year]['liabilities']
            response = f"{company_name.capitalize()}: Assets: ${assets} million, Liabilities: ${liabilities} million."
        else:
            response = "Company or year not found. Please try again."
    else:
        response = "Sorry, I didn't understand that question. Please try again."

    return render_template('index.html', response=response)

if __name__ == '__main__':
    app.run(debug=True)
