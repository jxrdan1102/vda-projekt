"""Wer sieht welche Daten?

- Firmen-Nutzer (company_id gesetzt): alle Daten seiner Firma.
- Superadmin (company_id None): nur seine eigenen Daten (fk_user_id).
- Eingebaute Modelle samt Komponenten sieht jeder (nur lesen/kopieren).
"""
from sqlalchemy import or_, select

from app.models.components import Component
from app.models.modell import Modell


def scope_filter(model, company_id: int | None, user_id: int | None):
    """Bedingung für .where(), oder None wenn nicht gefiltert wird."""
    if company_id is not None:
        cond = model.fk_company == company_id
    elif user_id is not None:
        cond = model.fk_user_id == user_id
    else:
        return None
    if model is Modell:
        cond = or_(cond, Modell.is_builtin.is_(True))
    elif model is Component:
        cond = or_(cond, Component.fk_modell.in_(select(Modell.id).where(Modell.is_builtin.is_(True))))
    return cond


def apply_scope(stmt, model, company_id: int | None, user_id: int | None):
    cond = scope_filter(model, company_id, user_id)
    return stmt if cond is None else stmt.where(cond)
