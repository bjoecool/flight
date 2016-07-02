---- 
---- CREATE VIEWS
---- 
DROP VIEW IF EXISTS airline_view;
CREATE OR REPLACE VIEW airline_view AS
SELECT
    id,
    get_city_name(from_city) as from_city,
    get_city_name(to_city) as to_city
FROM airline;

DROP VIEW IF EXISTS flight_view;
CREATE OR REPLACE VIEW flight_view AS 
SELECT 
    flight.id, 
    get_city_name(airline.from_city) as from,
    get_city_name(airline.to_city) as to,
    get_trip_name(trip) as trip,
    start_date,
    stay_days,
    adults,
    children,
    children_age as age,
    get_cabinclass_name(flight.cabinclass) as class,
    create_date
FROM flight,airline
WHERE flight.airline_id = airline.id;


DROP VIEW IF EXISTS flight_url_view;
CREATE OR REPLACE VIEW flight_url_view AS 
SELECT 
    flight.id, 
    get_city_url_name(airline.from_city) as from,
    get_city_url_name(airline.to_city) as to,
    get_trip_name(trip) as trip,
    start_date,
    stay_days,
    adults,
    children,
    children_age as age,
    get_cabinclass_name(flight.cabinclass) as class,
    create_date
FROM flight,airline
WHERE flight.airline_id = airline.id;


DROP VIEW IF EXISTS flight_price_view;
CREATE OR REPLACE VIEW flight_price_view AS
SELECT
    flight_id,
    price,
    get_company_name(company_id) as company,
    departure_time,
    arrival_time,
    span_days,
    duration,
    stop,
    stop_info,
    rate,
    search_date as date
FROM flight_price;

CREATE OR REPLACE VIEW flight_detail_price_view AS
SELECT 
    flight_view.from,
    flight_view.to,
    trip,
    start_date,
    stay_days,
    departure_time,
    arrival_time,
    span_days,
    duration,
    stop,
    stop_info,
    rate,
    adults,
    class,
    price,
    company,
    date as search_date 
FROM flight_view JOIN flight_price_view ON id=flight_id;
