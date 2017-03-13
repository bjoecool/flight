---- DROP Previous one
drop table if exists cabinclass cascade;
drop table if exists city cascade;
drop table if exists airline_company cascade;
drop table if exists airline cascade;
drop table if exists flight cascade;
drop table if exists trip cascade;
drop table if exists flight_price cascade;
drop table if exists flight_price_query_task;

DROP SEQUENCE IF EXISTS airline_id;
DROP SEQUENCE IF EXISTS airline_company_id;
DROP SEQUENCE IF EXISTS flight_id;
DROP SEQUENCE IF EXISTS city_id;


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
short_name varchar,
url_name text);

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

---- This table is used by the workers to record the task is finshed or not.
---- Also the task manager can see which task are waiting to be done.
CREATE TABLE flight_price_query_task(
flight_id int4,  --- references flight(id)
status int4, ---- 0: not finished. 1: finished
execute_date date   ---- date to execute the task
);


---- flight_price
drop table if exists flight_price cascade;

CREATE TABLE flight_price(
flight_id int4, --- references flight(id)
price money,
company_id int4, ---references airline_company(id)
departure_time timestamp with time zone, 
arrival_time timestamp with time zone,
span_days int4,  
duration text,  ---flight duration
stop text,    --- stop times in the flight duration,default is 1 which means fligth to destination directly
stop_info text, --- detail stop information
rate float,
search_date date --- date to get it
);


CREATE TABLE flight_task_status(
total_tasks int,
success_tasks int,
total_records int,
workers int,
task_start_time timestamp with time zone,
task_finished_time timestamp with time zone,
execute_date date primary key
);


