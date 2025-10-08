#This code defines the database schema for the Breast Cancer dataset using SQLAlchemy. It includes the Prediction model, which represents the table in the database, and the initialization of the database engine and session.



from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Initialize the database
engine = create_engine("sqlite:///breast_cancer.db")
Base = declarative_base()

# Define the database schema for Prediction
class Prediction(Base):
    __tablename__ = 'predictions'
    id = Column(Integer, primary_key=True)
    radius_mean = Column(Float)
    texture_mean = Column(Float)
    perimeter_mean = Column(Float)
    area_mean = Column(Float)
    smoothness_mean = Column(Float)
    compactness_mean = Column(Float)
    concavity_mean = Column(Float)
    concave_points_mean = Column(Float)
    symmetry_mean = Column(Float)
    fractal_dimension_mean = Column(Float)
    prediction = Column(String)
    probability_benign = Column(Float)
    probability_malignant = Column(Float)

# Define the database schema for PatientData
class PatientData(Base):
    __tablename__ = 'patients'
    id = Column(Integer, primary_key=True)
    patient_name = Column(String)
    patient_id = Column(Integer)
    prediction = Column(String)
    probability_benign = Column(Float)
    probability_malignant = Column(Float)

# Create the tables
Base.metadata.create_all(engine)

# Create a session
Session = sessionmaker(bind=engine)

def init_db():
    """Initialize the database and create tables."""
    Base.metadata.create_all(engine)

def get_session():
    """Get a new session to interact with the database."""
    return Session()
