import plotly.graph_objects as go
from decimal import Decimal
import requests

API_URL = 'https://api.exchangerate-api.com/v4/latest/'

def get_latest_exchange_rate(base_currency):
    response = requests.get(f'{API_URL}{base_currency}')
    data = response.json()
    if response.status_code == 200:
        return data.get('rates', {})
    else:
        return {}

def get_income_vs_expense_chart(user):
    from django.utils.timezone import now
    from .models import Transaction

    current_month = now().month
    current_year = now().year
    exchange_rates = get_latest_exchange_rate(user.currency)

    income = Decimal('0.0')
    expense = Decimal('0.0')

    transactions = Transaction.objects.filter(
        user=user,
        date__month=current_month,
        date__year=current_year
    )

    for transaction in transactions:
        if transaction.original_currency != user.currency:
            rate = Decimal(str(exchange_rates.get(transaction.original_currency, '1.0')))
            converted_amount = transaction.original_amount / rate
        else:
            converted_amount = transaction.original_amount

        if transaction.type == 'Income':
            income += converted_amount
        else:
            expense += converted_amount

    data = {'Income': float(income), 'Expense': float(expense)}

    fig = go.Figure(data=[
        go.Bar(
            x=list(data.keys()),
            y=list(data.values()),
            marker_color=['#16a34a', '#dc2626'],  # Tailwind green/red
            hovertemplate='%{x}: %{y:.2f}<extra></extra>',
            marker_line_color='rgba(255,255,255,0.2)',
            marker_line_width=2,
        )
    ])

    fig.update_layout(
        xaxis_title=None,
        yaxis_title=None,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#94a3b8', size=16),
        showlegend=False,
        margin=dict(l=20, r=20, t=20, b=20),
    )

    return fig.to_html(full_html=False, config={'displayModeBar': False})

def get_category_expense_chart(user):
    from django.utils.timezone import now
    from .models import Transaction

    current_month = now().month
    current_year = now().year
    exchange_rates = get_latest_exchange_rate(user.currency)

    transactions = Transaction.objects.filter(
        user=user,
        type='Expense',
        date__month=current_month,
        date__year=current_year
    )

    category_data = {}
    for transaction in transactions:
        if transaction.original_currency != user.currency:
            rate = Decimal(str(exchange_rates.get(transaction.original_currency, '1.0')))
            converted_amount = transaction.original_amount / rate
        else:
            converted_amount = transaction.original_amount

        category_data[transaction.category] = category_data.get(transaction.category, Decimal('0.0')) + converted_amount

    if not category_data:
        return None

    fig = go.Figure(data=[
        go.Pie(
            labels=list(category_data.keys()),
            values=[float(v) for v in category_data.values()],
            hole=0.4,
            textinfo='label+percent',
            marker=dict(line=dict(color='white', width=2))
        )
    ])

    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#94a3b8', size=16),
        showlegend=True,
        margin=dict(l=20, r=20, t=20, b=20),
    )

    return fig.to_html(full_html=False, config={'displayModeBar': False})

def get_monthly_trend_chart(user):
    from django.utils.timezone import now
    from .models import Transaction

    current_year = now().year
    exchange_rates = get_latest_exchange_rate(user.currency)

    transactions = Transaction.objects.filter(
        user=user,
        type='Expense',
        date__year=current_year
    )

    monthly_data = {}
    for transaction in transactions:
        if transaction.original_currency != user.currency:
            rate = Decimal(str(exchange_rates.get(transaction.original_currency, '1.0')))
            converted_amount = transaction.original_amount / rate
        else:
            converted_amount = transaction.original_amount

        month = transaction.date.month
        monthly_data[month] = monthly_data.get(month, Decimal('0.0')) + converted_amount

    if not monthly_data:
        return None

    months = list(range(1, 13))
    values = [float(monthly_data.get(month, Decimal('0.0'))) for month in months]

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=months,
        y=values,
        mode='lines+markers',
        line=dict(color='#3b82f6', width=3),
        marker=dict(size=8),
        hovertemplate='Month %{x}: %{y:.2f}<extra></extra>'
    ))

    fig.update_layout(
        xaxis_title=None,
        yaxis_title=None,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#94a3b8', size=16),
        showlegend=False,
        margin=dict(l=20, r=20, t=20, b=20),
        xaxis=dict(tickmode='array', tickvals=list(range(1, 13)), ticktext=[
            'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
            'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'
        ])
    )

    return fig.to_html(full_html=False, config={'displayModeBar': False})
