# Copyright (c) 2025, João Izidro and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from datetime import datetime, timedelta

class Appointment(Document):
    def validate(self):
        if isinstance(self.start_date, str):
            self.start_date = datetime.strptime(self.start_date, "%Y-%m-%d %H:%M:%S")

        if self.start_date and self.duration:
            duration_seconds = 0

            if isinstance(self.duration, int):
                duration_seconds = self.duration
            elif isinstance(self.duration, str):
                try:
                    h, m = map(int, self.duration.split(":"))
                    duration_seconds = h * 3600 + m * 60
                except Exception:
                    frappe.throw("Formato de duração inválido. Use 'HH:MM' ou um número inteiro de segundos.")
            else:
                frappe.throw("Tipo de duração inválido.")

            self.end_date = self.start_date + timedelta(seconds=duration_seconds)

        # Verificar conflitos com outros compromissos do mesmo vendedor
        if self.seller and self.start_date and self.end_date:
            conflicts = frappe.db.sql("""
                SELECT name FROM `tabAppointment`
                WHERE seller = %s AND name != %s
                AND (
                    (start_date < %s AND end_date > %s)
                )
            """, (
                self.seller,
                self.name,
                self.end_date,
                self.start_date
            ))

            if conflicts:
                frappe.throw("O vendedor já tem um compromisso nesse intervalo.")
