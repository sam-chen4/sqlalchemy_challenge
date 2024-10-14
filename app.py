# Import the dependencies.
from flask import Flask, jsonify
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy import create_engine, func
import datetime as dt

#################################################
# Database Setup
#################################################
# Path to the SQLite database
database_path = 'sqlite:///Resources/hawaii.sqlite'

# Create an engine to connect to the database
engine = create_engine(database_path)

# Reflect an existing database into a new model
Base = automap_base()

# Reflect the tables
Base.prepare(engine, reflect=True)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
SessionLocal = sessionmaker(bind=engine)
session = SessionLocal()

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################
@app.route('/')
def welcome():
    return (
        f"Welcome to the Climate API!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end><br/>"
    )

@app.route('/api/v1.0/precipitation')
def precipitation():
    # Calculate the date one year from the last date in the dataset
    most_recent_date = session.query(func.max(Measurement.date)).scalar()
    one_year_ago = dt.datetime.strptime(most_recent_date, '%Y-%m-%d') - dt.timedelta(days=365)
    
    # Query for the last 12 months of precipitation data
    results = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= one_year_ago).all()
    
    # Convert query results to a dictionary
    precipitation_data = {date: prcp for date, prcp in results}
    
    return jsonify(precipitation_data)

@app.route('/api/v1.0/stations')
def stations():
    # Query for all stations
    results = session.query(Station.station).all()
    
    # Convert query results to a list
    stations = [station[0] for station in results]
    
    return jsonify(stations)

@app.route('/api/v1.0/tobs')
def tobs():
    # Get the most active station ID
    most_active_station_id = session.query(Measurement.station, func.count(
        Measurement.station)).group_by(Measurement.station).order_by(func.count(Measurement.station).desc()).first()[0]
    
    # Calculate the date one year from the last date in the dataset
    most_recent_date = session.query(func.max(Measurement.date)).scalar()
    one_year_ago = dt.datetime.strptime(most_recent_date, '%Y-%m-%d') - dt.timedelta(days=365)
    
    # Query for the last 12 months of temperature observations for the most active station
    results = session.query(Measurement.date, Measurement.tobs).filter(
        Measurement.station == most_active_station_id, Measurement.date >= one_year_ago).all()
    
    # Convert query results to a list
    tobs_data = {date: tobs for date, tobs in results}
    
    return jsonify(tobs_data)

@app.route('/api/v1.0/<start>')
@app.route('/api/v1.0/<start>/<end>')
def temperature_range(start, end=None):
    # Create a session
    session = SessionLocal()
    
    # Query for min, avg, max temperature for the given start date (and end date if provided)
    if not end:
        results = session.query(func.min(Measurement.tobs), func.avg(
            Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date >= start).all()
    else:
        results = session.query(func.min(Measurement.tobs), func.avg(
            Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date >= start).filter(Measurement.date <= end).all()
    
    # Convert query results to a dictionary
    temp_data = {
        "TMIN": results[0][0],
        "TAVG": results[0][1],
        "TMAX": results[0][2]
    }
    
    return jsonify(temp_data)

if __name__ == '__main__':
    app.run(debug=True)