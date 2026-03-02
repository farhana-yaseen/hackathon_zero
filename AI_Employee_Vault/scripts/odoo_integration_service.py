#!/usr/bin/env python3
"""
Odoo Integration Service for Golden Tier
Handles ERP operations using JSON-RPC APIs
"""
import os
import sys
import time
import json
import xmlrpc.client
from datetime import datetime
from pathlib import Path

class OdooService:
    def __init__(self, vault_path):
        self.vault_path = vault_path
        self.erp_dir = os.path.join(vault_path, "ERP_Integration")
        self.accounting_dir = os.path.join(vault_path, "Accounting")

        # Create directories
        os.makedirs(self.erp_dir, exist_ok=True)
        os.makedirs(self.accounting_dir, exist_ok=True)

        # Odoo connection details - in production, these would come from config
        self.url = "http://localhost:8069"
        self.db = "odoo_db"
        self.username = "admin"
        self.password = "password"

        self.common = None
        self.models = None
        self.uid = None

        # Connect to Odoo
        self.connect_to_odoo()

    def connect_to_odoo(self):
        """Connect to Odoo instance."""
        try:
            self.common = xmlrpc.client.ServerProxy(f"{self.url}/xmlrpc/2/common")
            self.uid = self.common.authenticate(self.db, self.username, self.password, {})

            if self.uid:
                self.models = xmlrpc.client.ServerProxy(f"{self.url}/xmlrpc/2/object")
                print("Successfully connected to Odoo ERP")
                return True
            else:
                print("Failed to authenticate with Odoo")
                return False
        except Exception as e:
            print(f"Error connecting to Odoo: {e}")
            return False

    def process_accounting_requests(self):
        """Process accounting requests from the vault."""
        accounting_requests_dir = os.path.join(self.vault_path, "Needs_Action")

        if not os.path.exists(accounting_requests_dir):
            return

        for filename in os.listdir(accounting_requests_dir):
            if "accounting" in filename.lower() and filename.endswith(".json"):
                filepath = os.path.join(accounting_requests_dir, filename)

                try:
                    with open(filepath, 'r') as f:
                        request_data = json.load(f)

                    if request_data.get("type") == "accounting_operation":
                        self._handle_accounting_request(request_data)

                        # Move processed file to Done
                        done_dir = os.path.join(self.vault_path, "Done")
                        os.makedirs(done_dir, exist_ok=True)

                        import shutil
                        done_filepath = os.path.join(done_dir, f"processed_{filename}")
                        shutil.move(filepath, done_filepath)

                        print(f"Processed accounting request: {filename}")

                except Exception as e:
                    print(f"Error processing accounting request {filename}: {e}")

    def _handle_accounting_request(self, request_data):
        """Handle a specific accounting request."""
        operation = request_data.get("operation")

        if operation == "create_invoice":
            self._create_invoice(request_data)
        elif operation == "record_payment":
            self._record_payment(request_data)
        elif operation == "update_account":
            self._update_account(request_data)
        elif operation == "generate_report":
            self._generate_accounting_report(request_data)
        else:
            print(f"Unknown accounting operation: {operation}")

    def _create_invoice(self, request_data):
        """Create an invoice in Odoo."""
        try:
            partner_id = request_data.get("partner_id")
            lines = request_data.get("invoice_lines", [])

            if not partner_id or not lines:
                print("Missing required fields for invoice creation")
                return

            invoice_id = self.models.execute_kw(
                self.db, self.uid, self.password,
                "account.move", "create",
                [{
                    "partner_id": partner_id,
                    "move_type": "out_invoice",
                    "invoice_line_ids": [(0, 0, line) for line in lines]
                }]
            )

            print(f"Invoice created successfully with ID: {invoice_id}")

            # Log the operation
            self._log_operation("create_invoice", {"invoice_id": invoice_id, **request_data})

        except Exception as e:
            print(f"Error creating invoice: {e}")

    def _record_payment(self, request_data):
        """Record a payment in Odoo."""
        try:
            payment_vals = {
                "payment_type": request_data.get("payment_type", "inbound"),
                "partner_type": request_data.get("partner_type", "customer"),
                "partner_id": request_data.get("partner_id"),
                "amount": request_data.get("amount"),
                "currency_id": request_data.get("currency_id", 1),  # USD
            }

            payment_id = self.models.execute_kw(
                self.db, self.uid, self.password,
                "account.payment", "create",
                [payment_vals]
            )

            print(f"Payment recorded successfully with ID: {payment_id}")

            # Log the operation
            self._log_operation("record_payment", {"payment_id": payment_id, **request_data})

        except Exception as e:
            print(f"Error recording payment: {e}")

    def _update_account(self, request_data):
        """Update account information in Odoo."""
        try:
            account_id = request_data.get("account_id")
            update_values = request_data.get("update_values", {})

            if not account_id or not update_values:
                print("Missing required fields for account update")
                return

            self.models.execute_kw(
                self.db, self.uid, self.password,
                "account.account", "write",
                [[account_id], update_values]
            )

            print(f"Account {account_id} updated successfully")

            # Log the operation
            self._log_operation("update_account", {"account_id": account_id, **request_data})

        except Exception as e:
            print(f"Error updating account: {e}")

    def _generate_accounting_report(self, request_data):
        """Generate an accounting report."""
        try:
            report_type = request_data.get("report_type", "general_ledger")
            date_from = request_data.get("date_from")
            date_to = request_data.get("date_to")

            # This would call Odoo's reporting engine
            # For now, we'll simulate the report generation
            report_data = {
                "report_type": report_type,
                "date_range": {"from": date_from, "to": date_to},
                "generated_at": datetime.now().isoformat(),
                "data": {"placeholder": "report_data"}
            }

            # Save report to accounting directory
            report_filename = f"accounting_report_{report_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            report_path = os.path.join(self.accounting_dir, report_filename)

            with open(report_path, 'w') as f:
                json.dump(report_data, f, indent=2)

            print(f"Accounting report generated: {report_filename}")

            # Log the operation
            self._log_operation("generate_report", {"report_path": report_path, **request_data})

        except Exception as e:
            print(f"Error generating accounting report: {e}")

    def _log_operation(self, operation_type, details):
        """Log an operation to the ERP integration directory."""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "operation": operation_type,
            "details": details,
            "status": "completed"
        }

        log_filename = f"odoo_operation_log_{datetime.now().strftime('%Y%m%d')}.json"
        log_path = os.path.join(self.erp_dir, log_filename)

        # Append to existing log or create new one
        if os.path.exists(log_path):
            with open(log_path, 'r') as f:
                logs = json.load(f)
        else:
            logs = []

        logs.append(log_entry)

        with open(log_path, 'w') as f:
            json.dump(logs, f, indent=2)

    def run_service(self):
        """Run the Odoo integration service."""
        print("Odoo Integration Service started...")

        if not self.uid:
            print("Cannot start service: Not connected to Odoo")
            return

        while True:
            try:
                # Process any pending accounting requests
                self.process_accounting_requests()

                # Sleep before next check
                time.sleep(60)  # Check every minute

            except KeyboardInterrupt:
                print("Odoo Integration Service stopped.")
                break
            except Exception as e:
                print(f"Error in Odoo service: {e}")
                time.sleep(300)  # Wait 5 minutes before retrying

def main():
    if len(sys.argv) != 2:
        print("Usage: python odoo_integration_service.py <vault_path>")
        sys.exit(1)

    vault_path = sys.argv[1]
    odoo_service = OdooService(vault_path)

    try:
        odoo_service.run_service()
    except KeyboardInterrupt:
        print("Odoo Integration Service interrupted.")

if __name__ == "__main__":
    main()
