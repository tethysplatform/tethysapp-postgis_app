import os
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import sessionmaker
from geoalchemy2 import Geometry

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


def init_flooded_addresses_db(engine, first_time):
	"""
	Initialize the flooded addresses database.
	"""
	# STEP 1: Create database tables
	Base.metadata.create_all(engine)

	# STEP 2: Add data to the database
	if first_time:
		# Find path of parent directory relative to this file
		postgis_app_dir = os.path.dirname(__file__)

		# Define the path to the address points CSV dataset
		address_points_path = os.path.join(
			postgis_app_dir, 'workspaces', 'app_workspace', 'data', 'provo_address_points.csv'
		)

		# Read the CSV dataset into a list of lines
		with open(address_points_path, 'r') as f:
			address_points_lines = f.read().splitlines()

		# Remove the first line, which has the column headers in it
		address_points_lines.pop(0)

		# Create a session object in preparation for interacting with the database
		Session = sessionmaker(bind=engine)
		session = Session()

		# Create a new AddressPoint object for each line in the file
		for line in address_points_lines:
			row = line.split(',')

			address_point = AddressPoint(
				x=row[0],
				y=row[1],
				full_address=row[4],
				city=row[15],
				state=row[18],
				zip_code=row[16]
			)

			# Add the address points to the session to be added to the database
			session.add(address_point)

		# Define path to flood extent file (tab delimited)
		flood_extents_path = os.path.join(postgis_app_dir, 'workspaces', 'app_workspace', 'data', 'flood_extents.txt')

		# Read the file into a list of lines
		flood_extents_lines = []

		with open(flood_extents_path, 'r') as f:
			flood_extents_lines = f.read().splitlines()

		# Remove the first row, which has the column headings in it
		flood_extents_lines.pop(0)

		# Create a FloodExtent object for each line in the file
		for line in flood_extents_lines:
			row = line.split('\t')

			flood_extent = FloodExtent(
				wkt=row[0].strip('"'),
				map_id=row[2]
			)

			# Add the flood extent to the session to be added to the database
			session.add(flood_extent)

		# Commit to save all the address points and flood extents to the database
		session.commit()

		# Close the connection to prevent issues
		session.close()
