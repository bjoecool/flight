

DROP FUNCTION create_one_way_arilines(range int4);
DROP FUNCTION create_roundtrip_arilines(range int4,stay_days_range int4);

DROP FUNCTION create_one_way_airlines(start_date date);
DROP FUNCTION create_roundtrip_airlines(start_date date,stay_days_range int4);



---- 
---- CREATE FUNCTIONS
---- 

---- Function: get city id by name
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

