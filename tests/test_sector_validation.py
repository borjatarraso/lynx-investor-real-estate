"""Tests for the sector validation gate."""

import pytest
from lynx_realestate.core.analyzer import _validate_sector, SectorMismatchError
from lynx_realestate.models import CompanyProfile


class TestSectorValidation:
    """Sector validation blocks non-real-estate companies."""

    def _profile(self, ticker="T", sector=None, industry=None, desc=None):
        return CompanyProfile(
            ticker=ticker, name=f"{ticker} Corp",
            sector=sector, industry=industry, description=desc,
        )

    # --- Should ALLOW ---
    def test_real_estate_sector(self):
        _validate_sector(self._profile(sector="Real Estate", industry="REIT—Residential"))

    def test_real_estate_reits_sector(self):
        _validate_sector(self._profile(sector="Real Estate\u2014REITs", industry="Residential REITs"))

    def test_residential_reit(self):
        _validate_sector(self._profile(sector="Real Estate", industry="REIT—Residential"))

    def test_office_reit(self):
        _validate_sector(self._profile(sector="Real Estate", industry="REIT—Office"))

    def test_industrial_reit(self):
        _validate_sector(self._profile(sector="Real Estate", industry="REIT—Industrial"))

    def test_retail_reit(self):
        _validate_sector(self._profile(sector="Real Estate", industry="REIT—Retail"))

    def test_hotel_reit(self):
        _validate_sector(self._profile(sector="Real Estate", industry="REIT—Hotel & Motel"))

    def test_healthcare_reit(self):
        _validate_sector(self._profile(sector="Real Estate", industry="REIT—Healthcare Facilities"))

    def test_specialty_reit(self):
        _validate_sector(self._profile(sector="Real Estate", industry="REIT—Specialty"))

    def test_diversified_reit(self):
        _validate_sector(self._profile(sector="Real Estate", industry="REIT—Diversified"))

    def test_mortgage_reit(self):
        _validate_sector(self._profile(sector="Real Estate", industry="REIT—Mortgage"))

    def test_real_estate_services(self):
        _validate_sector(self._profile(sector="Real Estate", industry="Real Estate Services"))

    def test_real_estate_development(self):
        _validate_sector(self._profile(sector="Real Estate", industry="Real Estate—Development"))

    # Description-pattern gates
    def test_reit_in_description(self):
        _validate_sector(self._profile(
            sector="Other", industry="Other",
            desc="A diversified REIT focused on high-quality income properties.",
        ))

    def test_rental_income_in_description(self):
        _validate_sector(self._profile(
            sector="Other", industry="Other",
            desc="The company collects rental income from a portfolio of properties.",
        ))

    def test_occupancy_in_description(self):
        _validate_sector(self._profile(
            sector="Other", industry="Other",
            desc="Reports portfolio-wide occupancy rates above 95%.",
        ))

    def test_cap_rate_in_description(self):
        _validate_sector(self._profile(
            sector="Other", industry="Other",
            desc="Acquires assets at attractive cap rate spreads.",
        ))

    def test_ffo_in_description(self):
        _validate_sector(self._profile(
            sector="Other", industry="Other",
            desc="Reports FFO per share as its primary earnings metric.",
        ))

    def test_apartment_multifamily_in_desc(self):
        _validate_sector(self._profile(
            sector="Other", industry="Other",
            desc="Owns and operates multifamily apartment communities in Sunbelt markets.",
        ))

    def test_office_tower_in_desc(self):
        _validate_sector(self._profile(
            sector="Other", industry="Other",
            desc="Owns a Class A office tower in a major CBD.",
        ))

    def test_industrial_warehouse_in_desc(self):
        _validate_sector(self._profile(
            sector="Other", industry="Other",
            desc="Operates industrial warehouse and logistics properties near ports.",
        ))

    # --- Should BLOCK ---
    def test_technology_blocked(self):
        with pytest.raises(SectorMismatchError):
            _validate_sector(self._profile(sector="Technology", industry="Software—Application"))

    def test_energy_blocked(self):
        with pytest.raises(SectorMismatchError):
            _validate_sector(self._profile(sector="Energy", industry="Oil & Gas E&P"))

    def test_financial_blocked(self):
        with pytest.raises(SectorMismatchError):
            _validate_sector(self._profile(sector="Financial Services", industry="Banks"))

    def test_healthcare_pharma_blocked(self):
        with pytest.raises(SectorMismatchError):
            _validate_sector(self._profile(sector="Healthcare", industry="Drug Manufacturers"))

    def test_consumer_cyclical_blocked(self):
        with pytest.raises(SectorMismatchError):
            _validate_sector(self._profile(sector="Consumer Cyclical", industry="Auto Manufacturers"))

    def test_software_application_blocked(self):
        with pytest.raises(SectorMismatchError):
            _validate_sector(self._profile(sector="Technology", industry="Software—Application"))

    def test_all_none_blocked(self):
        with pytest.raises(SectorMismatchError):
            _validate_sector(self._profile())

    def test_empty_strings_blocked(self):
        with pytest.raises(SectorMismatchError):
            _validate_sector(self._profile(sector="", industry="", desc=""))

    def test_error_message_content(self):
        with pytest.raises(SectorMismatchError, match="outside the scope"):
            _validate_sector(self._profile(sector="Technology", industry="Software"))

    def test_generic_property_in_non_reit_desc_may_allow(self):
        """Description mentioning 'property' is intentionally permissive per the gate's patterns."""
        # The gate allows if \bproperty\b matches — this is by design.
        # Non-real-estate companies mentioning property should typically fail on sector first.
        # Check a clear non-REIT case without property/real-estate keywords is blocked:
        with pytest.raises(SectorMismatchError):
            _validate_sector(self._profile(
                sector="Consumer Defensive", industry="Packaged Foods",
                desc="Produces packaged snack foods distributed through supermarkets.",
            ))

    def test_error_suggests_another_agent(self):
        """Wrong-sector warning appends a 'use lynx-investor-*' line."""
        with pytest.raises(SectorMismatchError) as exc:
            _validate_sector(self._profile(
                sector="Healthcare", industry="Biotechnology"))
        message = str(exc.value)
        assert "Suggestion" in message
        assert "lynx-investor-healthcare" in message

    def test_error_never_suggests_self(self):
        """The suggestion never points back to this agent itself."""
        with pytest.raises(SectorMismatchError) as exc:
            _validate_sector(self._profile(
                sector="Technology", industry="Software"))
        message = str(exc.value)
        assert "use 'lynx-investor-real-estate'" not in message
