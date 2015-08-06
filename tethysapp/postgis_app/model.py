from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import sessionmaker
from geoalchemy2 import Geometry

from .utilities import get_persistent_store_engine

engine = get_persistent_store_engine('flooded_addresses')
SessionMaker = sessionmaker(bind=engine)

Base = declarative_base()


class AddressPoint(Base):
	"""
	SQLAlchemy table definition for storing address points.
	"""
	__tablename__ = 'address_points'

	# Columns
	id = Column(Integer, primary_key=True)
	full_address = Column(String)
	city = Column(String)
	state = Column(String)
	zip_code = Column(String)
	geometry = Column(Geometry('POINT'))

	def __init__(self, x, y, full_address, city, state, zip_code):
		"""
		Constructor
		"""
		self.full_address = full_address
		self.city = city
		self.state = state
		self.zip_code = zip_code
		# Define geometry in Well Known Text format with SRID
		self.geometry = 'SRID=4326;POINT({0} {1})'.format(x, y)

class FloodExtent(Base):
	"""
	SQLAlchemy table definition for storing flood extent polygons.
	"""
	__tablename__ = 'flood_extents'

	# Columns
	id = Column(Integer, primary_key=True)
	geometry = Column(Geometry('POLYGON'))
	map_id = Column(Integer)

	def __init__(self, wkt, map_id):
		"""
		Constructor
		"""
		# Add Spatial Reference ID
		self.geometry = 'SRID=4326;{0}'.format(wkt)
		self.map_id = map_id