import kbr.db_utils as db

class DB(object):

    def connect(self, url:str) -> None:
        self._db = db.DB( url )

    def disconnect(self) -> None:

        if self._db is not None:
            self._db.close()

    def station_add(self, station_id:int, name:str, lat:float, lon:float, capacity:int) -> int:

        return self._db.add_unique('station', {'station_id':station_id, 'name':name, 'lat': lat, 'lon': lon, 'capacity':capacity}, key='name')

    def station_get(self, id:str, station_id:int):
        return self._db.get_single('station', id=id, station_id=station_id)

    def stations(self, **values) -> str:
        return self._db.get('station', **values)

    def station_update(self, station_id:int, name:str, lat:float, lon:float, capacity:int) -> int:
        return self._db.update('station', {'station_id':station_id, 'name':name, 'lat': lat, 'lon': lon, 'capacity':capacity}, conditions=['id'])

    def status_add(self, station_id:int, bikes_available:int, docks_available:int, timestamp:int ) -> int:
        return self._db.add('status', {'station_id': station_id, 'bikes_available': bikes_available, 'docks_available': docks_available, 'timestamp': timestamp})

    def stations(self, **values) -> str:
        return self._db.get('status', **values)

    def trip_add(self, start_station_id:int, end_station_id:int, start_time:int, end_time:int ) -> int:
        return self._db.add('trip', {'start_station_id':start_station_id, 'end_station_id':end_station_id, 'start_time': start_time, 'end_time':end_time})

    def tripss(self, **values) -> str:
        return self._db.get('trip', **values)
