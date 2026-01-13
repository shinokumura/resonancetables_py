
from sqlalchemy import MetaData, Table, Column, Integer, Float, String, ForeignKey, UniqueConstraint
from config import engine

metadata = MetaData()


nuclides = Table(
    "nuclides",
    metadata,
    Column("nuclide_id", Integer, primary_key=True),
    Column("Z", Integer, nullable=False),
    Column("A", Integer, nullable=False),
    Column("Iso", String, nullable=False),      # e.g.: Na, Hf
    Column("nuclide", String, nullable=False),   # e.g.: Na023, Hf178n
    Column("metastable", Integer, default=0),   # 0:ground, 1:m1, 2:m2...
    UniqueConstraint("Z", "A", "metastable", name="uq_nuclide"),
)

sources = Table(
    'sources', metadata,
    Column('id', Integer, primary_key=True),
    Column('source_name', String, unique=True, nullable=False)
)

reaction_types = Table(
    'reaction_types', metadata,
    Column('id', Integer, primary_key=True),
    Column('name', String, unique=True, nullable=False) # 'ng', 'nf', 'na-m' ...
)

categories = Table(
    'categories', metadata,
    Column('id', Integer, primary_key=True),
    Column('name', String, unique=True, nullable=False) # 'resonance', 'thermal', 'macs'
)

data_table = Table(
    'data_table', metadata,
    Column('id', Integer, primary_key=True),
    Column('nuclide_id', Integer, ForeignKey('nuclides.nuclide_id')),
    Column('source_id', Integer, ForeignKey('sources.id')),
    Column('category_id', Integer, ForeignKey('categories.id')),
    Column('reaction_id', Integer, ForeignKey('reaction_types.id')),
    
    Column('quantity_type', String), 
    
    Column('liso', Integer),
    Column('value', Float),
    Column('dvalue', Float),
    Column('ratio', Float),
)


metadata.create_all(engine)