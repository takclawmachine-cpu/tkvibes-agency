"""
TKVibes — Assign Module Tests
"""
import pytest
from unittest.mock import patch
from src.models import Lead


class TestAssignCountryAssignments:
    def test_assign_by_country_india(self):
        from src.assign import assign_employees
        leads = [
            Lead(business_name="Delhi Clinic", lead_key="d1", country="India", city="Delhi"),
        ]
        cfg = {"crm": {"country_assignments": {"India": "Jashmit Bhalla"}, "api_url": "", "api_key": "", "employees": []}}
        assign_employees(leads, cfg)
        assert leads[0].assigned_employee == "Jashmit Bhalla"

    def test_assign_by_country_canada(self):
        from src.assign import assign_employees
        leads = [Lead(business_name="Toronto Clinic", lead_key="t1", country="Canada", city="Toronto")]
        cfg = {"crm": {"country_assignments": {"Canada": "Tishya Kane"}, "api_url": "", "api_key": "", "employees": []}}
        assign_employees(leads, cfg)
        assert leads[0].assigned_employee == "Tishya Kane"

    def test_mixed_countries(self):
        from src.assign import assign_employees
        leads = [
            Lead(business_name="Delhi Clinic", lead_key="d1", country="India", city="Delhi"),
            Lead(business_name="Toronto Clinic", lead_key="t1", country="Canada", city="Toronto"),
        ]
        cfg = {"crm": {"country_assignments": {"India": "Jashmit Bhalla", "Canada": "Tishya Kane"}, "api_url": "", "api_key": "", "employees": []}}
        assign_employees(leads, cfg)
        assert leads[0].assigned_employee == "Jashmit Bhalla"
        assert leads[1].assigned_employee == "Tishya Kane"

    def test_unassigned_country(self):
        from src.assign import assign_employees
        leads = [Lead(business_name="Dubai Clinic", lead_key="u1", country="UAE", city="Dubai")]
        cfg = {"crm": {"country_assignments": {"India": "Jashmit Bhalla"}, "api_url": "", "api_key": "", "employees": []}}
        assign_employees(leads, cfg)
        assert leads[0].assigned_employee == ""

    def test_no_country_assignments_config(self):
        from src.assign import assign_employees
        leads = [Lead(business_name="Delhi Clinic", lead_key="d1", country="India", city="Delhi")]
        cfg = {"crm": {"country_assignments": {}, "api_url": "", "api_key": "", "employees": []}}
        assign_employees(leads, cfg)
        assert leads[0].assigned_employee == ""

    def test_empty_crm_config(self):
        from src.assign import assign_employees
        leads = [Lead(business_name="Test", lead_key="t1", country="India", city="Delhi")]
        cfg = {"crm": {}}
        assign_employees(leads, cfg)
        assert leads[0].assigned_employee == ""

    @patch("src.assign.fetch_mapping_from_crm")
    def test_crm_api_country_match(self, mock_fetch):
        mock_fetch.return_value = [{"name": "Emp1", "countries": ["India"], "regions": []}]
        from src.assign import assign_employees
        leads = [Lead(business_name="Test", lead_key="t1", country="India", city="Delhi")]
        cfg = {"crm": {"country_assignments": {}, "api_url": "https://tkvibes.in/crm", "api_key": "test", "employees": []}}
        assign_employees(leads, cfg)
        assert leads[0].assigned_employee == "Emp1"

    @patch("src.assign.fetch_mapping_from_crm")
    def test_crm_api_no_match(self, mock_fetch):
        mock_fetch.return_value = [{"name": "Emp1", "countries": ["Canada"], "regions": []}]
        from src.assign import assign_employees
        leads = [Lead(business_name="Test", lead_key="t1", country="India", city="Delhi")]
        cfg = {"crm": {"country_assignments": {}, "api_url": "https://tkvibes.in/crm", "api_key": "test", "employees": []}}
        assign_employees(leads, cfg)
        assert leads[0].assigned_employee == ""

    @patch("src.assign.fetch_mapping_from_crm")
    def test_country_config_wins_over_crm_api(self, mock_fetch):
        mock_fetch.return_value = [{"name": "CRM Emp", "countries": ["India"], "regions": []}]
        from src.assign import assign_employees
        leads = [Lead(business_name="Test", lead_key="t1", country="India", city="Delhi")]
        cfg = {"crm": {"country_assignments": {"India": "Config Emp"}, "api_url": "https://tkvibes.in/crm", "api_key": "test", "employees": []}}
        assign_employees(leads, cfg)
        assert leads[0].assigned_employee == "Config Emp"

    def test_none_country(self):
        from src.assign import assign_employees
        leads = [Lead(business_name="Test", lead_key="t1", country=None, city="Delhi")]
        cfg = {"crm": {"country_assignments": {}, "api_url": "", "api_key": "", "employees": []}}
        assign_employees(leads, cfg)
        assert leads[0].assigned_employee == ""