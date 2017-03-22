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
insert into city values(10,'Chengdu','CTU','Chengdu, China (CTU-Shuangliu Intl.)');
insert into city values(11,'Chongqing','CKG','Chongqing, China (CKG-Jiangbei Intl.)');
insert into city values(12,'Wuhan','WUH','Wuhan, China (WUH-Tianhe Intl.)');
insert into city values(13,'Hangzhou','HGH','Hangzhou, China (HGH-Xiaoshan Intl.)');
insert into city values(14,'Taipei','TPE','Taipei, Taiwan (TPE-All Airports)');
insert into city values(15,'Bangkok','BKK','Bangkok, Thailand (BKK-All Airports)');
insert into city values(16,'Chiang Mai','CNX','Chiang Mai, Thailand (CNX-Chiang Mai Intl.)');
insert into city values(17,'Phuket','HKT','Phuket, Thailand (HKT-Phuket Intl.)');
insert into city values(18,'Seoul','SEL','Seoul, South Korea (SEL-All Airports)');
insert into city values(19,'Busan','PUS','Busan, South Korea (PUS-Gimhae)');
insert into city values(20,'Tokyo','TYO','Tokyo, Japan (TYO-All Airports)');
insert into city values(21,'Osaka','OSA','Osaka, Japan (OSA-All Airports)');
insert into city values(22,'Nagoya','NGO','Nagoya, Japan (NGO-All Airports)');
insert into city values(23,'Singapore','SIN','Singapore, Singapore (SIN-All Airports)');
insert into city values(24,'Kuala Lumpur','KUL','Kuala Lumpur, Malaysia (KUL-All Airports)');
insert into city values(25,'Ho Chi Minh City','SGN','Ho Chi Minh City, Vietnam (SGN-Tan Son Nhat Intl.)');
insert into city values(26,'Manila','MNL','Manila, Philippines (MNL-Ninoy Aquino Intl.)');
insert into city values(27,'Jakarta','JKT','Jakarta, Indonesia (JKT-All Airports)');
insert into city values(28,'Vancouver','YVR','Vancouver, BC, Canada (YVR-All Airports)');
insert into city values(29,'New York','NYC','New York, NY, United States (NYC-All Airports)');
insert into city values(30,'Los Angeles','QLA','Los Angeles, CA, United States (QLA-All Airports)');
insert into city values(31,'San Francisco','SFO','San Francisco, CA, United States (SFO-San Francisco Intl.)');
insert into city values(32,'Honolulu','HNL','Honolulu, HI, United States (HNL-Honolulu Intl.)');
insert into city values(33,'London','LON','London, England, UK (LON-All Airports)');
insert into city values(34,'Frankfurt','FRA','Frankfurt, Germany (FRA-All Airports)');
insert into city values(35,'Paris','PAR','Paris, France (PAR-All Airports)');
insert into city values(36,'Rome','ROM','Rome, Italy (ROM-All Airports)');
insert into city values(37,'Venice','VCE','Venice, Italy (VCE-All Airports)');
insert into city values(38,'Florence','FLR','Florence, Italy (FLR-Peretola)');
insert into city values(39,'Milan','MIL','Milan, Italy (MIL-All Airports)');
insert into city values(40,'Auckland','AKL','Auckland, New Zealand (AKL-Auckland Intl.)');

---- from_city values
insert into from_city values(5);
insert into from_city values(6);
insert into from_city values(7);
insert into from_city values(8);
insert into from_city values(9);

---- not do it now

insert into from_city values(10);
insert into from_city values(11);
insert into from_city values(12);
insert into from_city values(13);
insert into from_city values(14);

---- to_city values
insert into to_city values(1);
insert into to_city values(2);
insert into to_city values(3);
insert into to_city values(4);


---- not do it now
insert into to_city values(9);
insert into to_city values(14);
insert into to_city values(15);
insert into to_city values(16);
insert into to_city values(17);
insert into to_city values(18);
insert into to_city values(19);
insert into to_city values(20);
insert into to_city values(21);
insert into to_city values(22);
insert into to_city values(23);
insert into to_city values(24);
insert into to_city values(25);
insert into to_city values(26);
insert into to_city values(27);
insert into to_city values(28);
insert into to_city values(29);
insert into to_city values(30);
insert into to_city values(31);
insert into to_city values(32);
insert into to_city values(33);
insert into to_city values(34);
insert into to_city values(35);
insert into to_city values(36);
insert into to_city values(37);
insert into to_city values(38);
insert into to_city values(39);
insert into to_city values(40);

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

update route set machine='machine1' where from_city_id >=5 and from_city_id<10 and to_city_id<10;
update route set machine='machine1' where to_city_id >=5 and to_city_id<10 and from_city_id<10;
