import collections
import datetime
import math
import re
import redis
import logging
from redis.commands.json.path import Path

REDIS_HOST = 'aq-redis-cache.1ty6wn.ng.0001.apse2.cache.amazonaws.com'
PORT = 6379


class Redis(object):
    def __init__(self, host=REDIS_HOST, port=PORT, decode_responses=True):
        logging.basicConfig(level=logging.INFO)
        self.redis = redis.Redis(host=host, port=port, decode_responses=decode_responses)

    def flushDB(self):
        self.redis.flushdb()

    def store_past_data(self, sensor_id, newest_past_data):
        # run it before store prediction
        prev_past_data = None
        try:
            prev_past_data = self.redis.json().get('past' + sensor_id)
        except Exception as e:
            print("no data key past", sensor_id, "in redis")

        if prev_past_data is None:
            prev_past_data = {}
            for i in range(168):  # 14 days * 12 data/per day = 168 data in total
                prev_past_data[f"TIME_{i}"] = {}

        # for loop move each TIME_XX to TIME_XX-1
        # prediction['TIME_00] stored to prev{'TIME_167'}
        for i in range(len(prev_past_data)-1): # 0~(167-1)
            prev_past_data[f'TIME_{i}'] = prev_past_data[f'TIME_{i+1}']
        prev_past_data['TIME_167'] = newest_past_data

        # storing...
        self.redis.json().set('past'+sensor_id, Path.root_path(), prev_past_data)

        print('*** check past data storing result:')
        result = self.redis.json().get('past'+sensor_id)
        print(result)

    def store_prediction(self, sensor_id, prediction, weather_data, interval, current_time):
        if prediction is not None:
            try:
                data = {}
                # formatting
                names = [weather_data['name'][0]]
                temperature = [weather_data['Temp'][0]]
                for i in range(1, len(weather_data['Temp']), int(interval)):
                    names.append(weather_data['name'][i])  # time
                    temperature.append(weather_data['Temp'][i])
                # print('temperature', len(temperature), temperature)
                # print('names', len(names), names)

                print(len(prediction[0]))
                value = {}
                for i in range(len(prediction[0])):  # 36 slots
                    if i < 10:
                        field = f"TIME_0{i}"
                    else:
                        field = f"TIME_{i}"

                    value["name"] = names[i]
                    value["Temperature"] = temperature[i]

                    for j in range(len(prediction)):  # 20 layers
                        if math.isnan(prediction[j][i]):
                            value[f"Layer_{j}"] = "0"
                        else:
                            x = round(prediction[j][i], 3)
                            value[f"Layer_{j}"] = x

                    data[field] = value.copy()

                # before storing...
                exist_prediction = None
                try:
                    exist_prediction = self.redis.json().get(sensor_id)
                except Exception as e:
                    print('no exist prediction')

                if exist_prediction is not None:
                    newest_past = exist_prediction['TIME_00']
                    time_ele = re.split(':| ', newest_past['name'])
                    past_data_time = self.generate_datetime(time_ele)
                    diff = current_time - past_data_time

                    print('diff time b4 storing, diff:', diff, 'diff.s//3600:', diff.seconds // 3600)
                    # if past_data_time < current_time and diff.seconds // 3600 >= interval:
                    if past_data_time < current_time :
                        self.store_past_data(sensor_id, newest_past)

                # storing...
                self.redis.json().set(sensor_id, Path.root_path(), data)

                print('*** check storing result:')
                result = self.redis.json().get(sensor_id)
                print(result)

            except Exception as e:
                print("---ERROR in storing to redis:", e)

    def month_translate(self, month_word):
        month_int = 0
        if month_word == 'Jan':
            month_int = 1
        elif month_word == 'Feb':
            month_int = 2
        elif month_word == 'Mar':
            month_int = 3
        elif month_word == 'Apr':
            month_int = 4
        elif month_word == 'May':
            month_int = 5
        elif month_word == 'Jun':
            month_int = 6
        elif month_word == 'Jul':
            month_int = 7
        elif month_word == 'Aug':
            month_int = 8
        elif month_word == 'Sep':
            month_int = 9
        elif month_word == 'Oct':
            month_int = 10
        elif month_word == 'Nov':
            month_int = 11
        elif month_word == 'Dec':
            month_int = 12
        return month_int

    def generate_datetime(self, time_element):
        year = int(time_element[3])
        month = self.month_translate(time_element[1])
        day = int(time_element[2])
        hour, minute, second = int(time_element[4]), int(time_element[5]), int(time_element[6])
        last_time = datetime.datetime(year, month, day, hour, minute, second)
        return last_time

    def check_data(self, sensor_id, current_time, interval):

        def find_data(current_time, result):
            for index, data in enumerate(list(result.values())):
                time_ele = re.split(':| ', data['name'])
                data_time = self.generate_datetime(time_ele)
                diff = data_time - current_time
                print('d-d: ', diff, 'd-days', diff.days, 'd-hour', diff.seconds // 3600, 'd-sec', diff.seconds)
                if diff.days == 0 and diff.seconds // 3600 < interval:
                    closest_prediction = []
                    for i in range(len(data)-2):
                        closest_prediction.append(data[f"Layer_{i}"])
                    return closest_prediction

        result = self.redis.json().get(sensor_id)
        # order_result = collections.OrderedDict(sorted(result.items()))

        if result is not None:        
            last_prediction = result[f'TIME_{(len(result)-1)}']
            last_prediction_time = last_prediction['name']
            time_element = re.split(':| ', last_prediction_time)
            last_time = self.generate_datetime(time_element)

            if current_time <= last_time:
                print('has data in redis')
                redis_data = find_data(current_time, result)
                return redis_data
            else:
                print('data in redis is expire')
                return None
        else:
            print('no data in redis')
            return None
