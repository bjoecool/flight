---- cabinclass values
insert into cabinclass values(1,'first class');
insert into cabinclass values(2,'business');
insert into cabinclass values(3,'economy');
insert into cabinclass values(4,'preminum economy');

---- city values
insert into city values(1,'sydney', 'SYD');
insert into city values(2,'melbourne', 'MEL');
insert into city values(3,'brisbane','BNE');
insert into city values(4,'perth','PER');

insert into city values(5,'beijing','BJS');
insert into city values(6,'shanghai','SHA');
insert into city values(7,'guangzhou','CAN');
insert into city values(8,'shenzhen','SZX');
insert into city values(9,'hongkong','HKG');


---- trip values
insert into trip values(1,'oneway');
insert into trip values(2,'roundtrip');

---- airline values
insert into airline values(nextval('airline_id'),1,5);
insert into airline values(nextval('airline_id'),1,6);
insert into airline values(nextval('airline_id'),1,7);
insert into airline values(nextval('airline_id'),1,8);
insert into airline values(nextval('airline_id'),1,9);
insert into airline values(nextval('airline_id'),2,5);
insert into airline values(nextval('airline_id'),2,6);
insert into airline values(nextval('airline_id'),2,7);
insert into airline values(nextval('airline_id'),2,8);
insert into airline values(nextval('airline_id'),2,9);
insert into airline values(nextval('airline_id'),3,5);
insert into airline values(nextval('airline_id'),3,6);
insert into airline values(nextval('airline_id'),3,7);
insert into airline values(nextval('airline_id'),3,8);
insert into airline values(nextval('airline_id'),3,9);

insert into airline values(nextval('airline_id'),5,1);
insert into airline values(nextval('airline_id'),5,2);
insert into airline values(nextval('airline_id'),5,3);
insert into airline values(nextval('airline_id'),6,1);
insert into airline values(nextval('airline_id'),6,2);
insert into airline values(nextval('airline_id'),6,3);
insert into airline values(nextval('airline_id'),7,1);
insert into airline values(nextval('airline_id'),7,2);
insert into airline values(nextval('airline_id'),7,3);
insert into airline values(nextval('airline_id'),8,1);
insert into airline values(nextval('airline_id'),8,2);
insert into airline values(nextval('airline_id'),8,3);
insert into airline values(nextval('airline_id'),9,1);
insert into airline values(nextval('airline_id'),9,2);
insert into airline values(nextval('airline_id'),9,3);


select * from create_one_way_arilines(current_date+1,90);

select * from create_roundtrip_arilines(current_date+1,90,180);
