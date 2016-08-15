---- cabinclass values
insert into cabinclass values(1,'first class');
insert into cabinclass values(2,'business');
insert into cabinclass values(3,'economy');
insert into cabinclass values(4,'preminum economy');

---- city values
insert into city values(1,'sydney', 'SYD','Sydney, NSW, Australia (SYD-All Airports)');
insert into city values(2,'melbourne', 'MEL','Melbourne (MEL-All Airports)');
insert into city values(3,'brisbane','BNE','Brisbane, QLD, Australia (BNE)');
insert into city values(4,'perth','PER','Perth, WA, Australia (PER)');
insert into city values(5,'beijing','BJS','Beijing, China (BJS-All Airports)');
insert into city values(6,'shanghai','SHA','Shanghai, China (SHA-All Airports)');
insert into city values(7,'guangzhou','CAN','Guangzhou, China (CAN-Baiyun Intl.)');
insert into city values(8,'shenzhen','SZX','Shenzhen, China (SZX-Shenzhen)');
insert into city values(9,'hongkong','HKG','Hong Kong, Hong Kong (HKG-Hong Kong Intl.)');


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


--select * from create_one_way_airlines(current_date+1);

--select * from create_roundtrip_airlines(current_date+1,90);
