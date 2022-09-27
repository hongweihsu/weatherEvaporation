import datetime
import schedule
import time
import argparse
from postgreDB import PostgreDB
from predictor import Predictor
import sys
import numpy
from Redis import Redis


numpy.set_printoptions(threshold=sys.maxsize)
DAYS = 3  # number of forecast days
TOTAL_TIMESTAMP = DAYS * 24 + 1
BUCKET_DEPTH = 100  # Depth of each bucket in mm
KC = 1.2  # crop coefficient (Maize middle growth stage)
LOCALHOST = "127.0.0.1"
SENSOR_ID = 'AGA2408816389'
SOIL_MOISTURE_URL = 'https://extensionaus.com.au/soilmoisturemonitoring/'

# Parse arguments
parser = argparse.ArgumentParser(description="Generate moisture predictions at different depths")
# Interval - integer number of hours between two predictions/updates, should be between 1 and 23
parser.add_argument("--interval", type=int,
                    help="Time interval (hours) between two predictions: an integer within 1-23")
# Number of layers should be an integer between 1 and 20
parser.add_argument("--layers", type=int, help="Number of layers assuming one layer 10 cm: an integer within 1-20")
args = parser.parse_args()
args.interval = 2 if args.interval == None else args.interval
args.layers = 20 if args.layers == None else args.layers
print('The prediction interval is', args.interval, 'hour(s) with ', args.layers, 'layers')

if __name__ == '__main__':

    soil_profile = {'w_point_50': 0, 'f_capacity_50': 0, 'saturation_50': 0,
                    'w_point_100': 0, 'f_capacity_100': 0, 'saturation_100': 0,
                    'w_point_150': 0, 'f_capacity_150': 0, 'saturation_150': 0,
                    'soil_type_25': '', 'soil_type_75': '', 'soil_type_125': '', }

    # testing - this two lines will clear all data in RedisDB
    # redisDB = Redis()
    # redisDB.flushDB()

    def main_task():
        completeID = []
        current_hour = datetime.datetime.now().hour
        postgreDB = PostgreDB()
        all_sensors = postgreDB.get_all_sensors()
        redisDB = Redis(host=LOCALHOST)

        print('allID', all_sensors)
        print('allID_len', len(all_sensors))
        # is_first_run = True
        # has_redis_data = False
        for n, sensor in enumerate(all_sensors):
        #for n in range(1):
            # sensor_id = 'AFA00000DEMO9' # for testing
            print('--------------------', n, '--------', datetime.datetime.now())
            # sensor_id = "AFA00000DEMO1"  # testing
            print('for sensorID:', sensor)
            predictor = Predictor(DAYS, TOTAL_TIMESTAMP, BUCKET_DEPTH, KC, postgreDB, args.layers, args.interval,
                                  current_hour, soil_profile, lat=sensor['lat'], lon=sensor['lon'])
            closest_redis_data = redisDB.check_data(sensor['id'], datetime.datetime.now(), args.interval)
            print('closest data:', closest_redis_data)
            wp_fc_s = postgreDB.get_wp_fc_s()
            predictor.setSoilProfile(wp_fc_s)

            # sensor version
            try:
                sensor_data = postgreDB.get_sensor_data(sensor['id'])
                # print('s data:', sensor_data)
                # init_moisture = predictor.generate_initial_moisture(sensor_data)
                if len(sensor_data) > 0:
                    print('has sensor data')
                    if closest_redis_data is not None:
                        # do correction
                        print('has redis prediction, do correction')
                        init_moisture = predictor.adjust_prediction(sensor_data, closest_redis_data)  # correction
                    else:
                        print('only has sensor data, use sensor data directly')
                        init_moisture = predictor.generate_initial_moisture(sensor_data)  # use sensor data directly
                else:
                    print('no sensor data')
                    if closest_redis_data is not None:
                        # use redis data as measuring data to generate initial moisture
                        print('only has redis prediction, use it as sensor data')
                        print('closest data:', closest_redis_data)
                        init_moisture = predictor.generate_initial_moisture(closest_redis_data, True)
                        # pass
                    else:
                        print('No available data in PostgreDB and redisDB')
                        continue

                print('init m:', init_moisture)
                all_layers = predictor.get_all_layers(init_moisture)  # sensor version
                et = predictor.calculate_et()  # it need weather data
                # print(sensor_id, 'is predicting...')
                prediction = predictor.predict(all_layers, et, current_hour, sensor['id'], completeID)
                redisDB.store_prediction(sensor['id'], prediction, predictor.weather_data, args.interval, datetime.datetime.now())

            except Exception as e:
                print('---Other ERRORS:', e)
            finally:
                print()
                # break
        print('Completing time:', datetime.datetime.now())
        print(len(postgreDB.complexValue), 'complexValue:', postgreDB.complexValue)
        print(len(postgreDB.noFormula), 'noFormula:', postgreDB.noFormula)
        print(len(postgreDB.noData), 'noData:', postgreDB.noData)
        print(len(completeID), 'complete', completeID)


    main_task()
    schedule.every(args.interval).hours.at("00:05").do(main_task)

    while True:
        schedule.run_pending()
        time.sleep(1)
