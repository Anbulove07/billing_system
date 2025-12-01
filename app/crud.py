# app/crud.py
from sqlmodel import select
from app.models import Product, Customer, Purchase, PurchaseItem, Denomination
from app.db import async_session
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

async def get_product_by_code(session: AsyncSession, code: str):
    q = select(Product).where(Product.product_id == code)
    res = await session.execute(q)
    return res.scalars().first()

async def list_products(session: AsyncSession):
    q = select(Product)
    res = await session.execute(q)
    return res.scalars().all()

async def upsert_customer(session: AsyncSession, email: str):
    q = select(Customer).where(Customer.email == email)
    res = await session.execute(q)
    cust = res.scalars().first()
    if cust:
        return cust
    cust = Customer(email=email)
    session.add(cust)
    await session.commit()
    await session.refresh(cust)
    return cust

async def create_purchase(session: AsyncSession, customer: Customer, items: List[dict], total_amount: float, paid_amount: float):
    purchase = Purchase(customer_id=customer.id, total_amount=total_amount, paid_amount=paid_amount)
    session.add(purchase)
    await session.commit()
    await session.refresh(purchase)
    for it in items:
        pi = PurchaseItem(
            purchase_id=purchase.id,
            product_code=it['product_code'],
            qty=it['qty'],
            unit_price=it['unit_price'],
            tax_percent=it['tax_percent'],
            line_total=it['line_total']
        )
        session.add(pi)
        # reduce stock
        prod = await get_product_by_code(session, it['product_code'])
        if prod:
            prod.available_stocks = max(0, prod.available_stocks - it['qty'])
            session.add(prod)
    await session.commit()
    return purchase

async def list_purchases_by_email(session: AsyncSession, email: str):
    q = select(Customer).where(Customer.email == email)
    res = await session.execute(q)
    cust = res.scalars().first()
    if not cust:
        return []
    q2 = select(Purchase).where(Purchase.customer_id == cust.id).order_by(Purchase.timestamp.desc())
    res2 = await session.execute(q2)
    return res2.scalars().all()

async def get_purchase_items(session: AsyncSession, purchase_id: int):
    q = select(PurchaseItem).where(PurchaseItem.purchase_id == purchase_id)
    res = await session.execute(q)
    return res.scalars().all()

async def list_denominations(session: AsyncSession):
    q = select(Denomination).order_by(Denomination.value.desc())
    res = await session.execute(q)
    return res.scalars().all()

async def update_denominations(session: AsyncSession, changes: dict):
    denoms = await list_denominations(session)
    val_to_obj = {d.value: d for d in denoms}
    for val, new_count in changes.items():
        if val in val_to_obj:
            val_to_obj[val].count = new_count
            session.add(val_to_obj[val])
    await session.commit()
    return await list_denominations(session)
