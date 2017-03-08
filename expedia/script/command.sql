
flight_view_tb 

select flight_view_tb.from,flight_view_tb.to, trip,start_date, stay_days, adults, price,get_company_name(company_id),departure_time,arrival_time,span_days, duration,stop,stop_info,search_date 
from flight_price,flight_view_tb 
where flight_id = id
limit 10;


COPY (select * from flight_info order by search_date) TO '/db/flight.csv' csv HEADER;

select flight_view_tb.from,flight_view_tb.to, trip,start_date, stay_days, adults, price,get_company_name(company_id),departure_time,arrival_time,span_days, duration,stop,stop_info,search_date 
into flight_info
from flight_price,flight_view_tb 
where flight_id = id;

COPY (select flight_view_tb.from,flight_view_tb.to, trip,start_date, stay_days, adults, price,get_company_name(company_id),departure_time,arrival_time,span_days, duration,stop,stop_info,search_date 
from flight_price,flight_view_tb 
where flight_id = id
limit 10)
TO '/db/flight.csv'
csv HEADER;


flight_db=# \d flight_view_tb 
        Table "public.flight_view_tb"
   Column    |       Type        | Modifiers 
-------------+-------------------+-----------
 id          | integer           | 
 from        | character varying | 
 to          | character varying | 
 trip        | character varying | 
 start_date  | date              | 
 stay_days   | integer           | 
 adults      | integer           | 
 children    | integer           | 
 age         | smallint[]        | 
 class       | character varying | 
 create_date | date              | 


flight_db=# \d flight_price
             Table "public.flight_price"
     Column     |          Type          | Modifiers 
----------------+------------------------+-----------
 flight_id      | integer                | 
 price          | money                  | 
 company_id     | integer                | 
 departure_time | time without time zone | 
 arrival_time   | time without time zone | 
 span_days      | integer                | 
 duration       | text                   | 
 stop           | text                   | 
 stop_info      | text                   | 
 rate           | double precision       | 
 search_date    | date                   | 


flight_db=# \d flight
         Table "public.flight"
    Column    |    Type    | Modifiers 
--------------+------------+-----------
 id           | integer    | not null
 airline_id   | integer    | 
 trip         | integer    | default 1
 start_date   | date       | 
 stay_days    | integer    | 
 adults       | integer    | 
 children     | integer    | 
 children_age | smallint[] | 
 cabinclass   | integer    | default 3
 create_date  | date       | 


flight_db=# \d airline
     Table "public.airline"
  Column   |  Type   | Modifiers 
-----------+---------+-----------
 id        | integer | not null
 from_city | integer | 
 to_city   | integer | 


flight_db=# \d city
            Table "public.city"
   Column   |       Type        | Modifiers 
------------+-------------------+-----------
 id         | integer           | not null
 name       | character varying | 
 short_name | character varying | 
 url_name   | text   



