"""
Domains Package
===============

Contains all domain handlers for the Boijelux AI Agent.
"""

from .base import DomainBase
from .business import BusinessDomain
from .finance import FinanceDomain
from .healthcare import HealthcareDomain
from .education import EducationDomain
from .technology import TechnologyDomain
from .legal import LegalDomain
from .creative import CreativeDomain
from .real_estate import RealEstateDomain
from .manufacturing import ManufacturingDomain
from .agriculture import AgricultureDomain
from .retail import RetailDomain
from .transportation import TransportationDomain
from .energy import EnergyDomain
from .government import GovernmentDomain

__all__ = [
    'DomainBase',
    'BusinessDomain',
    'FinanceDomain',
    'HealthcareDomain',
    'EducationDomain',
    'TechnologyDomain',
    'LegalDomain',
    'CreativeDomain',
    'RealEstateDomain',
    'ManufacturingDomain',
    'AgricultureDomain',
    'RetailDomain',
    'TransportationDomain',
    'EnergyDomain',
    'GovernmentDomain'
]
