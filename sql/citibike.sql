CREATE TABLE station (
  id UUID NOT NULL DEFAULT  uuid_generate_v4 () PRIMARY KEY,
  station_id integer NOT NULL,
  name varchar( 80 ) NOT NULL,
  lat float,
  lon float,
  capacity int
);

CREATE TABLE status (
   id UUID NOT NULL DEFAULT  uuid_generate_v4 () PRIMARY KEY,
   station_id UUID NOT NULL references station( id ),
   bikes_available integer default  0,
   docks_available integer default  0,
   timestamp integer
);

CREATE TABLE trip (
   id UUID NOT NULL DEFAULT  uuid_generate_v4 () PRIMARY KEY,
   start_station_id  UUID NOT NULL references station( id ),
   end_station_id    UUID NOT NULL references station( id ),
   start_time integer,
   end_time integer
);


CREATE TABLE weather (
   id UUID NOT NULL DEFAULT  uuid_generate_v4 () PRIMARY KEY,
   day_stamp integer NOT NULL,
   mean_temp float,
   precipitation float,
   mean_humidity float,
   mean_wind_speed float
);
