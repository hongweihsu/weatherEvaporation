import psycopg2
import json
import datetime

HOST = "aquaterradb.cpcnttzwogzc.ap-southeast-2.rds.amazonaws.com"
PORT = 5432
DATABASE = "sdb_aquaterra"
USER = "aquaTerra"
PASSWORD = "Aquaterra88"

class PostgreDB:
    def __init__(self, host=HOST, port=PORT, database=DATABASE, user=USER, password=PASSWORD):
        self.host = host
        self.port = port
        self.database = database
        self.user = user
        self.__password = password
        self.noFormula = []
        self.noData = []
        self.complexValue = []

    def __connect(self):
        conn = psycopg2.connect(
            host=self.host,
            port=self.port,
            database=self.database,
            user=self.user,
            password=self.__password
        )
        return conn

    def get_location(self, veg_type):
        query = f""" SELECT ST_AsGeoJSON(geom) as points
                        FROM zones
                        WHERE zonename = '{veg_type}' """
        conn = self.__connect()
        cur = conn.cursor()
        cur.execute(query)
        geo_results = cur.fetchall()[0]  # SQL object #type and 5 coordinates
        points = json.loads(geo_results[0])  # 3D array 2*5*1
        lat = points['coordinates'][0][1][1]
        lng = points['coordinates'][0][1][0]
        cur.close()
        conn.close()

        return lat, lng

    def get_sensor_data(self, sensor_id):
        sensor_values = []
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        start_time = datetime.datetime.now() - datetime.timedelta(hours=2)
        start_time = start_time.strftime("%Y-%m-%d %H:%M")
        conn = self.__connect()
        cur = conn.cursor()
        query = f"""
            SELECT cap50, cap100, cap150 FROM
                (SELECT (time + INTERVAL '11' HOUR) AS aest, * 
                 FROM moisturedata
                 WHERE sensor_id = '{sensor_id}') AS inital_value
            WHERE aest > '{start_time}' AND aest < '{current_time}'
            ORDER BY aest
            LIMIT 1"""
        query2 = f"""
                    SELECT parameter
                    FROM sensor_formula
                    WHERE sensor_id = '{sensor_id}'"""

        raw_results = ()
        try:
            cur.execute(query)
            raw_results = cur.fetchall()[0]
        except Exception as e:
            # raw_results = [1000, 1000, 1000]
            self.noData.append(sensor_id)
            print("---ERROR: No available sensor Data")

        try:
            cur.execute(query2)
            param = cur.fetchall()[0][0]
            x1 = float(param.split(',')[0])
            x2 = float(param.split(',')[1])
            sensor_values = {}
            try:
                for i in range(len(raw_results)):
                    adt = raw_results[i]
                    if adt is None:
                        value = None
                    else:
                        value = x1 * (adt ** x2 / 100)
                    sensor_values['cap' + str((i + 1) * 50)] = value
                print("Sensor measurements: ", sensor_values)
            except Exception as e:
                print("---ERROR: has formula but no Data")
        except IndexError as e:
            self.noFormula.append(sensor_id)
            print("---ERROR: No sensor formula")

        try:
            if len(sensor_values) > 0:
                for v in list(sensor_values.values()):
                    if type(v) is complex:
                        raise TypeError
        except TypeError as e:
            self.complexValue.append(sensor_id)
            print('---Sensor data err, complex number')

        cur.close()
        conn.close()
        return sensor_values

    def get_wp_fc_s(self):
        # Set WP, FC, S
        conn = self.__connect()
        cur = conn.cursor()
        veg_type = 'Rice' # This was tomato before, why hardcode type
        query = f"""
            SELECT wpoint_50, fcapacity_50, saturation_50, wpoint_100, fcapacity_100, 
                   saturation_100, wpoint_150, fcapacity_150, saturation_150, soiltype_25, soiltype_75, soiltype_125
            FROM zones
            WHERE zonename = '{veg_type}' """
        cur.execute(query)
        zone_results = cur.fetchall()
        results = zone_results[0]  # 9 integers
        cur.close()
        conn.close()

        temp = []
        for result in results:
            if type(result) is int:
                temp.append(result / 100)
            else:
                temp.append(result)
        results = temp

        return results

    def get_all_sensors(self):  # return all sensors' id
        conn = self.__connect()
        cur = conn.cursor()
        query = f""" SELECT sensor_id, ST_AsGeoJSON(geom) as points FROM sensors"""
        cur.execute(query)
        results = cur.fetchall()
        data = []
        for x in results:
            result = {}
            result["id"] = str(x[0])
            coor = json.loads(x[1])['coordinates']
            if coor[1] > 90 or coor[1] < -90:
                result["lon"], result["lat"] = coor[1],coor[0]
            else:
                result["lon"], result["lat"] = coor[0], coor[1]
            data.append(result)
        cur.close()
        conn.close()
        return data
