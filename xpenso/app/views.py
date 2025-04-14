import json
from django.utils import timezone
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator
from django.db.models import Sum, ExpressionWrapper, F
from django.db.models import Sum, F, ExpressionWrapper, FloatField
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import get_user_model
from django.urls import reverse
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from django.core.mail import send_mail
from django.core.cache import cache
from django.contrib.auth.decorators import login_required
import random
import plotly.graph_objs as go
import plotly.offline as opy
from django.views.decorators.csrf import csrf_exempt
from plotly import plot
from .charts import *
from django.contrib import messages
import requests
from django.contrib.auth import authenticate, login, logout
from .models import *
import csv
from reportlab.pdfgen import canvas
from .stocks import *
from .utils import *
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet

def landing_page(request):
    return render(request, 'landing.html')

User = get_user_model()

@csrf_exempt
def submit_contact(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        message = request.POST.get('message')

        # Save to DB
        ContactQuery.objects.create(name=name, email=email, message=message)

        # Send confirmation email
        send_mail(
            subject='Thanks for contacting Valorra!',
            message=f"Hi {name},\n\nThanks for reaching out! We’ve received your message:\n\n\"{message}\"\n\nWe'll get back to you shortly.\n\n— Team Valorra",
            from_email='noreplyy.project.mail@gmail.com',
            recipient_list=[email],
            fail_silently=False,
        )

        return redirect('thank_you')  # or use JsonResponse if it's AJAX

    return redirect('landing')

def thank_you(request):
    return render(request, 'thank_you.html')


def generate_otp():
    return str(random.randint(100000, 999999))

def register(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']

        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return redirect('register')

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email is already registered.")
            return redirect('register')

        # Generate OTP and send via email
        otp = generate_otp()
        cache.set(f'otp_{email}', otp, timeout=300)  # Cache OTP for 5 minutes

        subject = 'Verify your email'
        message = f'Your OTP is: {otp}'
        send_mail(subject, message, settings.EMAIL_HOST_USER, [email])

        # Save user data temporarily in cache
        cache.set(f'registration_data_{email}', {
            'username': username,
            'email': email,
            'password': password
        }, timeout=300)

        messages.success(request, "OTP sent to your email.")
        return redirect(reverse('verify_email') + f'?email={email}')

    return render(request, 'register.html')

def verify_email(request):
    email = request.GET.get('email')

    if request.method == 'POST':
        entered_otp = request.POST['otp']
        cached_otp = cache.get(f'otp_{email}')

        if entered_otp == cached_otp:
            data = cache.get(f'registration_data_{email}')
            user = User.objects.create_user(
                username=data['username'],
                email=data['email'],
                password=data['password']
            )
            user.is_verified = True
            user.save()

            cache.delete(f'otp_{email}')
            cache.delete(f'registration_data_{email}')

            messages.success(request, "Account verified! Please log in.")
            return redirect('login')
        else:
            messages.error(request, "Invalid OTP. Try again.")

    return render(request, 'verify_email.html', {'email': email})


def user_login(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        user = authenticate(request, email=email, password=password)

        if user is not None:
            if user.is_verified:
                login(request, user)
                messages.success(request, "Login successful.")
                return redirect('dashboard')
            else:
                messages.error(request, "Account not verified.")
        else:
            messages.error(request, "Invalid email or password.")

    return render(request, 'login.html')

@login_required
def user_logout(request):
    logout(request)
    messages.success(request, "Logged out successfully.")
    return redirect('login')

def forgot_password(request):
    if request.method == 'POST':
        email = request.POST['email']
        if User.objects.filter(email=email).exists():
            otp = generate_otp()
            cache.set(f'password_reset_otp_{email}', otp, timeout=300)

            subject = 'Reset your password'
            message = f'Your OTP is: {otp}'
            send_mail(subject, message, settings.EMAIL_HOST_USER, [email])

            messages.success(request, "OTP sent to your email.")
            return redirect(reverse('reset_password') + f'?email={email}')
        else:
            messages.error(request, "Email not found.")

    return render(request, 'forgot_password.html')

def reset_password(request):
    email = request.GET.get('email')
    if request.method == 'POST':
        otp = request.POST['otp']
        new_password = request.POST['new_password']
        cached_otp = cache.get(f'password_reset_otp_{email}')

        if otp == cached_otp:
            user = User.objects.get(email=email)
            user.set_password(new_password)
            user.save()

            cache.delete(f'password_reset_otp_{email}')

            messages.success(request, "Password reset successful. Please log in.")
            return redirect('login')
        else:
            messages.error(request, "Invalid OTP.")

    return render(request, 'reset_password.html', {'email': email})


from decimal import Decimal
import requests


API_KEY = 'fca_live_uvpRZhgejJkX7iBvbaN3U14KKQkvEhEn4admRZ6o'

def get_latest_exchange_rate(from_currency, to_currency):
    if from_currency == to_currency:
        return Decimal('1.0')

    url = f"https://api.freecurrencyapi.com/v1/latest?apikey={API_KEY}&base_currency={from_currency}"
    try:
        response = requests.get(url)
        data = response.json()
        rate = data['data'].get(to_currency)
        if rate:
            return Decimal(rate)
    except:
        pass
    return Decimal('1.0')  # fallback if API fails

@login_required
def dashboard(request):
    user = request.user
    current_date = now()
    current_month = current_date.month
    current_year = current_date.year

    # All user transactions
    all_transactions = Transaction.objects.filter(user=user).order_by('-date')
    monthly_transactions = all_transactions.filter(date__year=current_year, date__month=current_month)

    # Split by type
    monthly_income = monthly_transactions.filter(type='Income')
    monthly_expense = monthly_transactions.filter(type='Expense')

    all_income = all_transactions.filter(type='Income')
    all_expense = all_transactions.filter(type='Expense')

    # Convert original amount to user's currency
    def convert_amount(t):
        if t.original_currency == user.currency:
            return Decimal(t.original_amount)
        return Decimal(t.original_amount) * get_latest_exchange_rate(t.original_currency, user.currency)

    # Monthly totals
    total_income = sum(convert_amount(t) for t in monthly_income)
    total_expense = sum(convert_amount(t) for t in monthly_expense)

    # Total balance
    total_income_all = sum(convert_amount(t) for t in all_income)
    total_expense_all = sum(convert_amount(t) for t in all_expense)
    total_balance = total_income_all - total_expense_all

    # Recent 5 transactions
    recent_transactions = [
        {
            'date': t.date.date(),
            'type': t.type,
            'category': t.category,
            'original_currency': t.original_currency,
            'original_amount': t.original_amount,
            'converted_amount': convert_amount(t)
        }
        for t in all_transactions[:5]
    ]

    # Generate charts
    income_vs_expense_chart = get_income_vs_expense_chart(user)
    category_expense_chart = get_category_expense_chart(user)
    monthly_trend_chart = get_monthly_trend_chart(user)

    context = {
        'user': user,
        'currency': user.currency,
        'total_income': round(total_income, 2),
        'total_expense': round(total_expense, 2),
        'total_balance': round(total_balance, 2),
        'recent_transactions': recent_transactions,
        'income_vs_expense_chart': income_vs_expense_chart,
        'category_expense_chart': category_expense_chart,
        'monthly_trend_chart': monthly_trend_chart,
    }

    return render(request, 'dashboard.html', context)


@login_required
def settings_view(request):
    if request.method == 'POST':
        currency = request.POST.get('currency')
        theme = request.POST.get('theme')

        # Validate and update currency
        if currency and currency in dict(CURRENCY_CHOICES):
            request.user.currency = currency
        else:
            messages.error(request, "Invalid currency selection.")

        # Validate and update theme
        if theme in ['light', 'dark']:
            request.user.theme_preference = theme
        else:
            messages.error(request, "Invalid theme selection.")

        request.user.save()
        messages.success(request, "Settings updated successfully.")
        return redirect('dashboard')  # or 'settings' if you want to stay on the page

    currencies = [code for code, _ in CURRENCY_CHOICES]
    return render(request, 'settings.html', {
        'currencies': currencies,
    })

@login_required
def add_transaction(request):
    if request.method == 'POST':
        type = request.POST.get('type')
        category = request.POST.get('category')
        original_amount = request.POST.get('amount')
        description = request.POST.get('description')
        receipt = request.FILES.get('receipt')
        date = request.POST.get('date')

        if not original_amount:
            messages.error(request, 'Amount is required.')
            return redirect('add_transaction')

        if not date:
            messages.error(request, 'Date is required.')
            return redirect('add_transaction')

        try:
            original_amount = Decimal(original_amount)
            conversion_rate = Decimal(1.0)  # Fixed since currency is based on user setting
            amount = original_amount * conversion_rate
        except Exception:
            messages.error(request, 'Invalid amount.')
            return redirect('add_transaction')

        try:
            date = now().strptime(date, '%Y-%m-%d').date()
        except ValueError:
            messages.error(request, 'Invalid date format.')
            return redirect('add_transaction')

        # Save transaction
        Transaction.objects.create(
            user=request.user,
            type=type,
            category=category,
            original_amount=original_amount,
            original_currency=request.user.currency,
            amount=amount,
            conversion_rate=conversion_rate,
            description=description,
            receipt=receipt,
            date=date
        )

        messages.success(request, 'Transaction added successfully!')
        return redirect('dashboard')

    context = {
        'today': now().date(),
    }
    return render(request, 'add_transaction.html', context)

@login_required
def transaction_list(request):
    user = request.user
    transactions = Transaction.objects.filter(user=user).order_by('-date')

    # Convert amount to user's currency
    for transaction in transactions:
        if transaction.original_currency != user.currency:
            rate = get_latest_exchange_rate(transaction.original_currency, user.currency)
            transaction.converted_amount = transaction.original_amount * Decimal(rate)
        else:
            transaction.converted_amount = transaction.original_amount

    # Pagination (10 transactions per page)
    paginator = Paginator(transactions, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'transactions': page_obj,
        'currency': user.currency,
    }
    return render(request, 'transactions.html', context)

@login_required
def edit_transaction(request, transaction_id):
    transaction = get_object_or_404(Transaction, id=transaction_id, user=request.user)

    if request.method == 'POST':
        transaction.type = request.POST.get('type')
        transaction.category = request.POST.get('category')
        transaction.original_amount = Decimal(request.POST.get('amount'))
        transaction.description = request.POST.get('description')
        transaction.date = request.POST.get('date')

        # Update conversion rate
        if transaction.original_currency != request.user.currency:
            rate = get_latest_exchange_rate(transaction.original_currency, request.user.currency)
            transaction.amount = transaction.original_amount * Decimal(rate)
            transaction.conversion_rate = rate
        else:
            transaction.amount = transaction.original_amount
            transaction.conversion_rate = 1.0

        transaction.save()
        messages.success(request, 'Transaction updated successfully!')
        return redirect('transactions')

    context = {
        'transaction': transaction,
        'currency': request.user.currency,
    }
    return render(request, 'edit_transaction.html', context)

@login_required
def delete_transaction(request, transaction_id):
    transaction = get_object_or_404(Transaction, id=transaction_id, user=request.user)
    transaction.delete()
    messages.success(request, 'Transaction deleted successfully!')
    return redirect('transactions')

API_KEY = 'fca_live_uvpRZhgejJkX7iBvbaN3U14KKQkvEhEn4admRZ6o'
API_URL = 'https://api.freecurrencyapi.com/v1/latest'

def get_exchange_rate(from_currency, to_currency):
    if from_currency == to_currency:
        return Decimal('1.0')
    try:
        response = requests.get(API_URL, params={'apikey': API_KEY, 'base_currency': from_currency})
        data = response.json()
        rate = data['data'].get(to_currency)
        if rate:
            return Decimal(rate)
    except Exception:
        pass
    return Decimal('1.0')


@login_required
def filter_transactions(request):
    user = request.user
    user_currency = user.currency or 'USD'

    transactions = Transaction.objects.filter(user=user).order_by('-date')

    # Filters
    t_type = request.GET.get('type')
    category = request.GET.get('category')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    min_amount = request.GET.get('min_amount')
    max_amount = request.GET.get('max_amount')

    if t_type:
        transactions = transactions.filter(type=t_type)
    if category:
        transactions = transactions.filter(category=category)
    if start_date:
        transactions = transactions.filter(date__gte=start_date)
    if end_date:
        transactions = transactions.filter(date__lte=end_date)
    if min_amount:
        transactions = transactions.filter(original_amount__gte=Decimal(min_amount))
    if max_amount:
        transactions = transactions.filter(original_amount__lte=Decimal(max_amount))

    # Convert and annotate
    for txn in transactions:
        rate = get_exchange_rate(txn.original_currency, user_currency)
        txn.converted_amount = (txn.original_amount * rate).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

    export_format = request.GET.get('export')

    # 📥 CSV EXPORT
    if export_format == 'csv':
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="transactions.csv"'

        writer = csv.writer(response)
        writer.writerow(['Date', 'Type', 'Category', f'Amount ({user_currency})', 'Description'])

        for txn in transactions:
            writer.writerow([
                txn.date.strftime('%Y-%m-%d'),
                txn.type,
                txn.category,
                f"{txn.converted_amount} {user_currency}",
                txn.description
            ])
        return response

    # 📄 PDF EXPORT
    if export_format == 'pdf':
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="transactions.pdf"'

        doc = SimpleDocTemplate(response, pagesize=A4)
        styles = getSampleStyleSheet()
        buffer = [Paragraph("Transaction Report", styles['Title']), Spacer(1, 12)]

        table_data = [['Date', 'Type', 'Category', f'Amount ({user_currency})', 'Description']]
        for txn in transactions:
            table_data.append([
                txn.date.strftime('%B %d, %Y'),
                txn.type,
                txn.category,
                f"{txn.converted_amount} {user_currency}",
                txn.description
            ])

        table = Table(table_data, colWidths=[100, 60, 80, 90, 150])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#4a90e2")),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.whitesmoke, colors.lightgrey]),
        ]))

        buffer.append(table)
        doc.build(buffer)
        return response

    # 🌐 Render HTML
    context = {
        'transactions': transactions,
        'currency': user_currency,
    }
    return render(request, 'filter_transactions.html', context)



@login_required
def market_dashboard(request):
    chart_stocks = {}
    price_stocks = {}

    for stock_name, ticker in STOCK_TICKERS.items():
        stock_info = search_stock(ticker)
        if not stock_info:
            continue

        # Only generate chart for index tickers
        if stock_name in ["NIFTY 50", "Bank NIFTY"]:
            chart_html = generate_stock_chart(ticker, stock_name)
            chart_stocks[stock_name] = {
                'chart': chart_html,
                'price': stock_info['price'],
                'change': stock_info['change']
            }
        else:
            price_stocks[stock_name] = stock_info

    context = {
        'chart_stocks': chart_stocks,        # NIFTY 50 & Bank NIFTY with charts
        'price_stocks': price_stocks,        # Others like Apple, Google, etc.
        'crypto_data': get_crypto_data(),
        'forex_data': get_forex_rates(),
        'news_articles': get_market_news(),
    }

    return render(request, 'market_dashboard.html', context)


@login_required
def stock_detail(request, symbol):
    symbol = symbol.strip()

    if not symbol:
        messages.error(request, "Stock symbol is required.")
        return redirect('search_results')

    try:
        # Try to perform a search for matching stocks
        matched_stocks = dynamic_search_stock(symbol)
    except Exception as e:
        print(f"[Error] Stock search failed for '{symbol}': {e}")
        messages.error(request, f"An error occurred while searching for '{symbol}'. Please try again later.")
        return redirect('search_results')

    if not matched_stocks:
        messages.error(request, f"No results found for '{symbol}'.")
        return redirect('search_results')

    stock_info = matched_stocks[0]  # Only one result expected here

    # Required fields for display
    required_fields = ['symbol', 'name', 'price', 'change', 'currency', 'exchange', 'market_cap']
    missing_fields = [field for field in required_fields if field not in stock_info or stock_info[field] is None]

    if missing_fields:
        messages.error(request, f"Incomplete data received for '{stock_info.get('symbol', symbol)}'. Missing: {', '.join(missing_fields)}.")
        return redirect('search_results')

    # Normalize field types and handle missing fields gracefully
    stock_info = {
        'symbol': str(stock_info.get('symbol', 'N/A')),
        'name': str(stock_info.get('name', 'N/A')),
        'price': str(stock_info.get('price', '0.00')),
        'change': str(stock_info.get('change', '0')),
        'currency': str(stock_info.get('currency', 'N/A')),
        'exchange': str(stock_info.get('exchange', 'N/A')),
        'market_cap': str(stock_info.get('market_cap', 'N/A')),
        'previous_close': str(stock_info.get('previous_close', 'N/A')),
        'open': str(stock_info.get('open', 'N/A')),
        'high': str(stock_info.get('high', 'N/A')),
        'low': str(stock_info.get('low', 'N/A')),
        'year_high': str(stock_info.get('year_high', 'N/A')),
        'year_low': str(stock_info.get('year_low', 'N/A')),
    }

    # Try generating the stock chart
    try:
        chart_html = generate_stock_chart(stock_info['symbol'], stock_info['name'])
    except Exception as e:
        print(f"[Chart Error] Chart generation failed for '{stock_info['symbol']}': {e}")
        chart_html = "<div class='text-danger'>Chart currently unavailable.</div>"

    return render(request, 'stock_detail.html', {
        'search_result': stock_info,
        'chart_html': chart_html,
    })

@login_required
def search_results(request):
    query = request.GET.get('query', '').strip()

    if not query:
        messages.error(request, "Search query is required.")
        return redirect('market')

    try:
        # Try to perform a search for matching stocks
        matched_stocks = dynamic_search_stock(query)
    except Exception as e:
        print(f"[Error] Stock search failed for '{query}': {e}")
        messages.error(request, f"An error occurred while searching for '{query}'. Please try again later.")
        return redirect('market')

    if not matched_stocks:
        messages.error(request, f"No results found for '{query}'.")
        return redirect('market')

    return render(request, 'search_results.html', {
        'matched_stocks': matched_stocks,
        'search_query': query,
    })



@login_required
def manage_budget(request):
    user = request.user
    budgets = Budget.objects.filter(user=user)
    today = timezone.now().date()
    user_currency = user.currency

    budget_data = []

    for budget in budgets:
        expenses = Transaction.objects.filter(user=user, type='Expense')

        if budget.time_period == 'daily':
            expenses = expenses.filter(date__date=today)
        elif budget.time_period == 'weekly':
            start_date = today - timedelta(days=7)
            expenses = expenses.filter(date__date__range=(start_date, today))
        elif budget.time_period == 'monthly':
            start_date = today.replace(day=1)
            expenses = expenses.filter(date__date__range=(start_date, today))
        else:
            expenses = Transaction.objects.none()

        # Convert each transaction to user's currency
        total_spent = Decimal("0.00")
        for tx in expenses:
            converted = Decimal(str(convert_currency(tx.original_amount, tx.original_currency, user_currency)))
            total_spent += converted

        # Convert budget amount (assumed in USD) to user's currency
        converted_limit = Decimal(str(convert_currency(budget.amount, 'USD', user_currency)))

        # Prevent division by zero
        percent_used = (total_spent / converted_limit * 100) if converted_limit else Decimal("0.00")
        percent_used = round(percent_used, 2)

        # Send alert if 90% or more used
        if percent_used >= 90:
            subject = f"⚠ {budget.time_period.capitalize()} Budget Alert"
            message = f"""Hi {user.email},

Your {budget.time_period} budget is {percent_used}% used!

Budget Limit: {converted_limit} {user_currency}
Spent: {total_spent} {user_currency}

Please keep an eye on your spending.
– Valorra
"""
            send_mail(subject, message, settings.EMAIL_HOST_USER, [user.email], fail_silently=True)

        budget_data.append({
            'budget': budget,
            'spent': round(total_spent, 2),
            'limit': round(converted_limit, 2),
            'percent': float(min(percent_used, 100)),
        })

    return render(request, 'manage_budget.html', {
        'budget_data': budget_data,
        'currency': user_currency
    })

def get_conversion_rate(user_currency):
    if user_currency == 'USD':
        return 1.0
    api_key = "fca_live_uvpRZhgejJkX7iBvbaN3U14KKQkvEhEn4admRZ6o"
    url = f"https://api.freecurrencyapi.com/v1/latest?apikey={api_key}&base_currency={user_currency}"
    response = requests.get(url)
    data = response.json()
    return data.get('data', {}).get('USD', 1.0)

@login_required
def add_budget(request):
    if request.method == 'POST':
        amount_input = float(request.POST['amount'])
        time_period = request.POST['time_period']
        user_currency = request.user.currency

        # Convert amount to USD for saving
        conversion_rate = get_conversion_rate(user_currency)
        converted_amount = amount_input * float(conversion_rate)

        # Update or create budget
        budget, created = Budget.objects.get_or_create(
            user=request.user,
            time_period=time_period,
            defaults={'amount': converted_amount}
        )

        if not created:
            budget.amount = converted_amount
            budget.save()
            messages.success(request, f"{time_period.capitalize()} budget updated successfully!")
        else:
            messages.success(request, f"{time_period.capitalize()} budget added successfully!")

        return redirect('manage_budget')

    return render(request, 'set_budget.html')


import re
import requests
from django.contrib.auth.decorators import login_required
from django.shortcuts import render

GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_API_KEY = "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"

headers = {
    "Authorization": f"Bearer {GROQ_API_KEY}",
    "Content-Type": "application/json"
}

# ✨ Formatter to make Lumi's responses beautiful
def format_response(response):
    # Convert Markdown bold **text** to <strong>text</strong>
    response = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', response)

    # Format numbered lists (adds <ul><li>)
    response = re.sub(r'\n(\d+)\.\s', r'</li><li><strong>\1.</strong> ', response)
    response = f"<ul class='space-y-2 list-none ml-1'><li>{response}</li></ul>"

    # Replace remaining newlines with <br> for readability
    response = response.replace('\n', '<br>')

    return response


@login_required
def chatbot_view(request):
    user_input = ""
    response = ""
    formatted_response = ""

    if request.method == "POST":
        user_input = request.POST.get("message")

        if user_input:
            data = {
                "model": "llama-3.3-70b-versatile",
                "messages": [
                    {"role": "system", "content": "Your name is Lumi. You are a helpful expense tracking assistant. Always give responses in well-structured bullet or numbered points when possible."},
                    {"role": "user", "content": user_input}
                ],
                "temperature": 0.7
            }

            try:
                res = requests.post(GROQ_API_URL, headers=headers, json=data)
                if res.status_code == 200:
                    response_data = res.json()
                    response = response_data['choices'][0]['message']['content']
                    formatted_response = format_response(response)
                else:
                    response = f"API Error: {res.status_code} - {res.text}"
                    formatted_response = format_response(response)
            except Exception as e:
                response = f"Error: {str(e)}"
                formatted_response = format_response(response)
        else:
            response = "Please enter a message."
            formatted_response = format_response(response)

    return render(request, "chatbot.html", {
        "user_input": user_input,
        "response": response,
        "formatted_response": formatted_response
    })
