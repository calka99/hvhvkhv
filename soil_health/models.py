"""Soil app model exports.

SoilReading is owned by farm_overview because it is part of a farm's shared
overview data. This alias keeps the soil app import path available without
creating a duplicate database table.
"""

from farm_overview.models import SoilReading

__all__ = ['SoilReading']
