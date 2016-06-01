---- cabinclass values
insert into cabinclass values(1,'first class');
insert into cabinclass values(2,'business');
insert into cabinclass values(3,'economy');
insert into cabinclass values(4,'preminum economy');

---- city values
insert into city values(nextval('city_id'),'sydney', 'SYD');
insert into city values(nextval('city_id'),'melbourne', 'MEL');
insert into city values(nextval('city_id'),'beijing','BJS');
insert into city values(nextval('city_id'),'shanghai','SHA');
insert into city values(nextval('city_id'),'guangzhou','');
insert into city values(nextval('city_id'),'shenzhen','');


---- trip values
insert into trip values(1,'oneway');
insert into trip values(2,'roundtrip');

---- airport values
insert into airport values('SYD-ALL', get_city_id_by_name('sydney'));
insert into airport values('MEL-ALL', get_city_id_by_name('melbourne'));

---- airline values
insert into airline values(nextval('airline_id'),1,3);
insert into airline values(nextval('airline_id'),1,4);
insert into airline values(nextval('airline_id'),1,5);
insert into airline values(nextval('airline_id'),1,6);
insert into airline values(nextval('airline_id'),2,3);
insert into airline values(nextval('airline_id'),2,4);
insert into airline values(nextval('airline_id'),2,5);



select * from create_one_way_arilines(current_date+1,90);

select * from create_roundtrip_arilines(current_date+1,90,180);
