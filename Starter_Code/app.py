# Import the dependencies.
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import pandas as pd

from flask import Flask, jsonify



#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(autoload_with=engine)

# Save reference to each table
measurement = Base.classes.measurement
station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)



#################################################
# Flask Routes
#################################################

@app.route('/')
def home():
     return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end>"
    )
    
@app.route('/api/precipitation')
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Query precipitation data for the last 12 months

    # Find the most recent date in the data set.
    recent_date = session.query(func.max(measurement.date)).scalar()
    recent_date = pd.to_datetime(recent_date)

    # Calculate the date one year from the last date in data set.
    one_year = recent_date - pd.DateOffset(days=365)
    one_year = one_year.strftime('%Y-%m-%d')

    # Perform a query to retrieve the data and precipitation scores
    precipitation_data = session.query(measurement.date, measurement.prcp).filter(measurement.date >= one_year).all()

    session.close()

    #create a dictionary
    precipitation_dictionary = {date: prcp for date, prcp in precipitation_data}

    return jsonify(precipitation_data)

@app.route('/api/stations')
def stations():
    session = Session(engine)
    #Return a JSON list of stations from the dataset
    stations = session.query(station.station).all
    session.close()

    station_list = [station[0] for station in stations]
    return jsonify(station_list)

@app.route('/api/v1.0/tobs')
def tobs():
    session = Session(engine)

    # Query the dates and temperature observations of the most-active station for the previous year of data
    most_active_station = session.query(measurement.station, func.count(measurement.station)).group_by(measurement.station).order_by(func.count(measurement.station).desc()).first()

    if most_active_station:
        most_active_station_id = most_active_station[0]

        latest_date = session.query(func.max(measurement.date)).filter(measurement.station == most_active_station_id).scalar()
        latest_date = pd.to_datetime(latest_date)
        one_year = latest_date - pd.DateOffset(days=365)
        one_year = one_year.strftime('%Y-%m-%d')

        temperature_data = session.query(measurement.date, measurement.tobs).filter(measurement.station == most_active_station_id, measurement.date >= one_year_ago_str).all()
        session.close()

        temperature_list = [{'date': date, 'temperature': tobs} for date, tobs in temperature_data]

        return jsonify(temperature_list)
