---- DROP Previous one
drop table if exists cabinclass cascade;
drop table if exists city cascade;
drop table if exists airline_company cascade;
drop table if exists airline cascade;
drop table if exists flight cascade;
drop table if exists flight_pricecascade;
drop table if exists trip cascade;
drop table if exists flight_price cascade;
drop table if exists airport cascade;
drop table if exists t1 cascade;
drop table if exists t2 cascade;
drop table if exists flight_price_query_task;

DROP SEQUENCE IF EXISTS airline_id;
DROP SEQUENCE IF EXISTS airline_company_id;
DROP SEQUENCE IF EXISTS flight_id;
DROP SEQUENCE IF EXISTS city_id;

DROP FUNCTION create_one_way_arilines(range int4);
DROP FUNCTION create_roundtrip_arilines(range int4,stay_days_range int4);
DROP FUNCTION create_airlines_schedule(period int4);

----
---- CREATE SEQUENCE
----
CREATE SEQUENCE airline_id START 1;
CREATE SEQUENCE airline_company_id START 1;
CREATE SEQUENCE flight_id START 1;
CREATE SEQUENCE city_id START 1;


------------------------------------------------
---- CREATE TABLES
------------------------------------------------

---- cabinclass, including the cabin class such as business or economy class
CREATE TABLE cabinclass(
id int4 primary key,
name varchar);

---- city
CREATE TABLE city(
id int4 primary key,
name varchar,
short_name varchar);

---- airport
CREATE TABLE airport(
name varchar,
city_id int4 references city(id));

---- airline_company
CREATE TABLE airline_company(
id int4 primary key,
name varchar);


---- trip,  
--- 1 : 'oneway'
--- 2 : 'roundtrip'
CREATE TABLE trip(
id int4 primary key,
name varchar);

---airline includes all kinds of airline which indicates the line from one city to another
CREATE TABLE airline(
id int4 primary key,
from_city int4,
to_city int4);

---- flight indicate a specific airline including the departure date, return date, staydays, trip, cabinclass and so on
CREATE TABLE flight (
id int4 primary key,
airline_id int4 references airline(id),
trip int4 default 1, ---1: oneway ; 2: roundtrip 
start_date date,
stay_days int4,
adults int4,
children int4,
children_age int2[],
cabinclass int4 default 3,  ---references cabinclass table
create_date date);

---- flight_price
CREATE TABLE flight_price(
flight_id int4, --- references flight(id)
price money,
company_id int4, ---references airline_company(id)
search_date date --- date to get it
);

---- This table is used by the workers to record the task is finshed or not.
---- Also the task manager can see which task are waiting to be done.
CREATE TABLE flight_price_query_task(
flight_id int4,  --- references flight(id)
status int4, ---- 0: not finished. 1: finished
execute_date date   ---- date to execute the task
);


---- 
---- CREATE FUNCTIONS
---- 

---- Function: airport values
CREATE OR REPLACE FUNCTION get_city_id_by_name(name varchar) returns int4 AS
$$
SELECT id from city where name=$1;
$$ LANGUAGE SQL;

CREATE OR REPLACE FUNCTION get_city_name(id int4) returns varchar AS
$$
SELECT name from city where id=$1;
$$ LANGUAGE SQL;

---- Function:  Input trip id and return trip name
CREATE OR REPLACE FUNCTION get_trip_name(id int4) returns varchar AS
$$
SELECT name from trip where id = $1
$$ LANGUAGE SQL;

CREATE OR REPLACE FUNCTION get_cabinclass_name(id int4) returns varchar AS
$$
SELECT name from cabinclass where id=$1;
$$ LANGUAGE SQL;

---- Function to get airline company name by id
CREATE OR REPLACE FUNCTION get_company_name(id int4) returns varchar AS
$$
    SELECT name from airline_company where id = $1
$$ LANGUAGE SQL;

---- Function to get the id
CREATE OR REPLACE FUNCTION get_airline_company_id_by_name(n varchar) returns int4 AS
$$
DECLARE
    company_id int4;
BEGIN
    SELECT id into company_id from airline_company where name=n;
    IF NOT FOUND THEN
        INSERT INTO airline_company VALUES(nextval('airline_company_id'),n);
    END IF;
    SELECT id into company_id from airline_company where name=n;
    return company_id;
END;
$$ LANGUAGE PLPGSQL;

CREATE OR REPLACE FUNCTION create_today_task() returns int8 AS
$$
    DELETE FROM flight_price_query_task where execute_date<=current_date;
    insert into flight_price_query_task select id,0,current_date from flight where start_date>current_date;
    SELECT count(*) from flight_price_query_task where execute_date=current_date;
$$ LANGUAGE SQL;


---- Function: create_one_way_airlines_schedule
-- range indicates what is the last start_date
CREATE OR REPLACE FUNCTION create_one_way_airlines(start_date date) returns int8 AS
$$
DECLARE
    airline_id int4;
    stay_days int4;
    num int4;
BEGIN
    num := 0;
    for airline_id in SELECT id from airline 
    LOOP --- loop airline_id
        RAISE NOTICE 'airline_id[%],trip[oneway],start_date[%]', airline_id,start_date;
        INSERT INTO flight VALUES (
        nextval('flight_id'),
        airline_id,
        1,  ---oneway
        start_date,
        0,
        1,
        0,
        '{}',
        3,  ---economy
        current_date);
        num = num+1;
    END LOOP;
    RETURN num;
END;
$$LANGUAGE PLPGSQL;

---- Function: create_roundtrip_arilines
-- range is the start_date range. 
-- stay_days_range is for the range of stay_days from 1 to this value;
CREATE OR REPLACE FUNCTION create_roundtrip_airlines(start_date date,stay_days_range int4) returns int8 AS
$$
DECLARE
    airline_id int4;
    stay_days int4;
    num int4;
BEGIN
    num := 0;
    for airline_id in SELECT id from airline 
    LOOP --- loop airline_id
        stay_days :=1;
        LOOP --- loop stay days
            RAISE NOTICE 'airline_id[%],trip[roundtrip],start_date[%],stay_days[%]', airline_id,start_date,stay_days;
            INSERT INTO flight VALUES (
            nextval('flight_id'),
            airline_id,
            2,  ---roundtrip
            start_date,
            stay_days,
            1,
            0,
            '{}',
            3,  ---economy
            current_date);
            num = num+1;
            stay_days = stay_days+1;
            IF stay_days > stay_days_range THEN
                EXIT;
            END IF;
        END LOOP;
    END LOOP;
    RETURN num;
END;
$$LANGUAGE PLPGSQL;


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

---- View: Input city id and return airport name
DROP VIEW IF EXISTS flight_view;
CREATE OR REPLACE VIEW flight_view AS 
SELECT 
    flight.id, 
    get_city_name(airline.from_city) as from,
    get_city_name(airline.to_city) as to,
    get_trip_name(trip) as trip,
    start_date,
    start_date+stay_days as return_date,
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
    search_date as date
FROM flight_price;

CREATE OR REPLACE VIEW flight_detail_price_view AS
SELECT 
    flight_view.from,
    flight_view.to,
    trip,
    start_date,
    return_date,
    stay_days,
    adults,
    class,
    price,
    company,
    date as search_date 
FROM flight_view JOIN flight_price_view ON id=flight_id;
