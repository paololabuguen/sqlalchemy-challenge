# Import the dependencies.
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify
import datetime as dt
import numpy as np

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
hawaii_meas = Base.classes.measurement
hawaii_stat = Base.classes.station

#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################
@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation         (Returns list of precipitation data of the last year)<br/>"
        f"/api/v1.0/stations              (Returns list of stations)<br/>"
        f"/api/v1.0/tobs                  (Returns dates and temp observations for the most active station)<br/>"
        f"/api/v1.0/start_date/           ((yyyy-mm-dd format) Returns a list of the min temperature, max temperature and average temperature from the start date specified)<br/>"
        f"/api/v1.0/start_date/end_date/  ((yyyy-mm-dd format)Returns a list of the min temperature, max temperature and average temperature from the start date to the end date specified)"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    """Returns list of precipitation data of the last year in the database"""

    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Query the last year of precipitation in the data
    year_ago = dt.datetime(2017, 8, 23) - dt.timedelta(days=366)

    # Query the last year of precipitation in the data
    prec_query = session.query(hawaii_meas.date, hawaii_meas.prcp).filter(hawaii_meas.date >= year_ago)
    precipitation = []
    
    session.close()
    # Create dictionary to convery into a json of the precipitation data
    for date, prcp in prec_query:
        prec_dict = {}
        prec_dict[date] = prcp
        precipitation.append(prec_dict)

    return jsonify(precipitation)


@app.route("/api/v1.0/stations")
def stations():
    """Returns list of stations in the database"""

    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Query all the stations
    stat_query = session.query(func.distinct(hawaii_meas.station)).all()
    
    session.close()

    # Create a list of all the stations
    stations = list(np.ravel(stat_query))

    return jsonify(stations)


@app.route("/api/v1.0/tobs")
def tobs():
    """Returns dates and temp observations for the most active station"""
    
    # Create our session (link) from Python to the DB
    session = Session(engine)

    year_ago = dt.datetime(2017, 8, 23) - dt.timedelta(days=366)

    # Find the distinct stations and their activity
    distinct_stat = session.query(func.distinct(hawaii_meas.station), func.count(hawaii_meas.station)).\
        group_by(hawaii_meas.station).all()
    
    # Find the most active station from the list of distinct stations
    most_active = ''
    max_row = 0
    for row in distinct_stat:
        if row[1] > max_row:
            max_row = row[1]
            most_active = row[0]

    # Query for the date and temperature observed for the most active station
    temperature_query = session.query(hawaii_meas.date, hawaii_meas.tobs).filter(hawaii_meas.date >= year_ago).filter(hawaii_meas.station == most_active)

    session.close()

    # Create a list to convert to json for the temp observed for the most active station

    temp_observation = [f'Temperature data in the last year for {most_active}']
    
    for date, tobs in temperature_query:
        tobs_dict = {}
        tobs_dict[date] = tobs
        temp_observation.append(tobs_dict)
    
    return jsonify(temp_observation)


@app.route("/api/v1.0/<start_date>")
def start_date(start_date):
    """Returns a list of the min temperature, max temperature and average temperature later than the start date specified"""

    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Query the min, max, and avg temp from the start date to the most recent date
    start_date_query = session.query(func.min(hawaii_meas.tobs), func.max(hawaii_meas.tobs), func.avg(hawaii_meas.tobs)).\
        filter(hawaii_meas.date >= start_date).all()
    
    session.close()

    # Create a list to make into a json of the min, max and avg temp from the start date to the most recent date
    temp_observation = [f'Temperature data since {start_date}']
    
    temp_dict = {'Min Temp': start_date_query[0][0], 'Max Temp': start_date_query[0][1], 'Avg Temp': start_date_query[0][2]}

    temp_observation.append(temp_dict)

    return jsonify(temp_observation)

@app.route("/api/v1.0/<start_date>/<end_date>")
def date_range(start_date, end_date):
    """Returns a list of the min temperature, max temperature and average temperature later than the start date specified"""

    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Query the min, max, and avg temp from the start date and the end date
    date_query = session.query(func.min(hawaii_meas.tobs), func.max(hawaii_meas.tobs), func.avg(hawaii_meas.tobs)).\
        filter(hawaii_meas.date >= start_date).filter(hawaii_meas.date <= end_date).all()
    
    session.close()

    # Create a list to make into a json of the min, max and avg temp from the start date to the end date
    temp_observation = [f'Temperature data from {start_date} to {end_date}']
    
    temp_dict = {'Min Temp': date_query[0][0], 'Max Temp': date_query[0][1], 'Avg Temp': date_query[0][2]}

    temp_observation.append(temp_dict)

    return jsonify(temp_observation)

if __name__ == '__main__':
    app.run(debug=True)