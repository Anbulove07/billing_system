# app/main.py
import os
from dotenv import load_dotenv
from fastapi import FastAPI, Request, BackgroundTasks, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from app.db import async_session, init_db
from app import crud
from aiosmtplib import SMTP
from email.message import EmailMessage

load_dotenv()

app = FastAPI()
app.mount('/static', StaticFiles(directory='app/static'), name='static')
templates = Jinja2Templates(directory='app/templates')

@app.on_event('startup')
async def on_startup():
    await init_db()

@app.get('/', response_class=HTMLResponse)
async def billing_page(request: Request):
    async with async_session() as session:
        products = await crud.list_products(session)
        denoms = await crud.list_denominations(session)
    return templates.TemplateResponse('billing.html', {'request': request, 'products': products, 'denominations': denoms})

@app.get('/history/{email}')
async def purchase_history(email: str):
    async with async_session() as session:
        purchases = await crud.list_purchases_by_email(session, email)
        return [{'id': p.id, 'timestamp': p.timestamp.isoformat(), 'total': p.total_amount, 'paid': p.paid_amount} for p in purchases]

@app.get('/purchase/{purchase_id}')
async def get_purchase(purchase_id: int):
    async with async_session() as session:
        purchase_items = await crud.get_purchase_items(session, purchase_id)
        return [{'product_code': pi.product_code, 'qty': pi.qty, 'unit_price': pi.unit_price, 'line_total': pi.line_total} for pi in purchase_items]

@app.post('/generate', response_class=HTMLResponse)
async def generate_bill(request: Request, background_tasks: BackgroundTasks):
    form = await request.form()
    email = form.get('customer_email')
    try:
        paid_amount = float(form.get('paid_amount') or 0)
    except ValueError:
        paid_amount = 0.0

    items = []
    idx = 1
    while True:
        p_key = f'product_code_{idx}'
        q_key = f'qty_{idx}'
        if p_key not in form:
            break
        code = form.get(p_key)
        qty_raw = form.get(q_key)
        try:
            qty = int(qty_raw or 0)
        except ValueError:
            qty = 0
        if not code or qty <= 0:
            idx += 1
            continue
        items.append({'product_code': code, 'qty': qty})
        idx += 1

    denominations_input = {}
    for key in form:
        if key.startswith('denom_count_'):
            val = int(key.replace('denom_count_', ''))
            denominations_input[val] = int(form.get(key) or 0)

    async with async_session() as session:
        customer = await crud.upsert_customer(session, email)
        enriched_items = []
        total = 0.0
        for it in items:
            prod = await crud.get_product_by_code(session, it['product_code'])
            if not prod:
                continue
            unit = prod.price_per_unit
            tax = prod.tax_percent
            line_net = unit * it['qty']
            tax_amt = line_net * (tax / 100.0)
            line_total = round(line_net + tax_amt, 2)
            total += line_total
            enriched_items.append({
                'product_code': it['product_code'],
                'qty': it['qty'],
                'unit_price': unit,
                'tax_percent': tax,
                'line_total': line_total
            })
        total = round(total, 2)
        change_required = round(paid_amount - total, 2)

        change_breakdown, leftover = compute_change(change_required, denominations_input)

        purchase = await crud.create_purchase(session, customer, enriched_items, total, paid_amount)

    background_tasks.add_task(send_invoice_email, email, purchase.id)

    return templates.TemplateResponse('invoice.html', {'request': request,
                                                       'purchase': purchase,
                                                       'items': enriched_items,
                                                       'total': total,
                                                       'paid': paid_amount,
                                                       'change': change_required,
                                                       'change_breakdown': change_breakdown,
                                                       'leftover': leftover})


def compute_change(change_amount: float, denominations: dict):
    if change_amount <= 0:
        return {}, 0.0
    remaining = int(round(change_amount))
    breakdown = {}
    for val in sorted(denominations.keys(), reverse=True):
        if remaining <= 0:
            break
        available = denominations.get(val, 0)
        need = remaining // val
        take = min(need, available)
        if take > 0:
            breakdown[val] = take
            remaining -= val * take
    leftover = remaining
    return breakdown, leftover


async def send_invoice_email(to_email: str, purchase_id: int):
    smtp_host = os.getenv('SMTP_HOST')
    smtp_port = int(os.getenv('SMTP_PORT', 587))
    smtp_user = os.getenv('SMTP_USER')
    smtp_password = os.getenv('SMTP_PASSWORD')
    from_email = os.getenv('FROM_EMAIL')

    body = f"Your invoice (Purchase ID: {purchase_id}) is attached. Thank you for your purchase."
    message = EmailMessage()
    message['From'] = from_email
    message['To'] = to_email
    message['Subject'] = f'Invoice - Purchase {purchase_id}'
    message.set_content(body)

    try:
        smtp = SMTP(hostname=smtp_host, port=smtp_port)
        await smtp.connect()
        await smtp.starttls()
        await smtp.login(smtp_user, smtp_password)
        await smtp.send_message(message)
        await smtp.quit()
    except Exception as e:
        print('Failed to send email:', e)
