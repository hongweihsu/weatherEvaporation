import requests
import numpy as np
import pandas as pd
import datetime
from model import *
import math
import csv
import re


def refET(tDew=[8, 14, 11], tMin=[15, 18, 14], tMax=[19, 24, 21], rhMin=[40, 45, 50], rhMax=[67, 73, 88],
          rhMean=[60, 70, 80], rs=[25, 22, 23], u10=[30, 24, 11], date=[1, 1, 2018], z=50, lat=-38,
          actualVapourPressure='dewTemp'):
    # Parameters
    Landa = 2.45  # MJ/Kg
    Cp = 1.013 * 10 ** -3  # MJ/(Kg.C)
    Eps = 0.622  # Ratio molecular water vapour per dry air
    Sigma = 4.903 * 10 ** -9  # Stefan-Boltzman constant (MJ/K4/m2/day)
    D = date[0]  # day (1~30)
    M = date[1]  # Month (number 1-12)
    Y = date[2]  # Year
    Phi = math.radians(lat)  # Latitude in radians
    G = 0  # Soil heat flux (Kj/m2/day)
    Gsc = 0.082  # Solar constant (MJ/m2/min)
    alfa = 0.23  # albedo of reference grass
    u10 = [j / 3.6 for j in u10]  # K/hr to m/s

    # General calculations
    tAve = [(j + k) / 2 for j, k in zip(tMin, tMax)]

    u2 = [(j * 4.87 / math.log(67.8 * 10 - 5.42)) for j in
          u10]  # estimating wind speed 2m above ground from 10m above ground

    # Calculating actual vapour pressure
    if actualVapourPressure == 'dewTemp':
        ea = e(tDew)
    elif actualVapourPressure == 'relativeHumidity':
        eaTMin = e(tMin)
        eaTMax = e(tMax)
        ea = [(i * k / 100 + j * l / 100) / 2 for i, j, l, k in zip(eaTMin, eaTMax, rhMin, rhMax)]
    elif actualVapourPressure == 'meanRelativeHumidity':
        eaTMin = e(tMin)
        eaTMax = e(tMax)
        ea = [(l) / 2 / 100 * (i + j) / 2 for i, j, l in zip(eaTMin, eaTMax, rhMean)]

    eTMax = e(tMax)
    eTMin = e(tMin)
    es = [(k + j) / 2 for j, k in zip(eTMin, eTMax)]

    p = 101.3 * ((293 - 0.0065 * z) / 293) ** 5.26
    gamma = Cp * p / Eps / Landa
    satVapPresSlope = [4098 * (0.6108 * math.exp(17.27 * j / (j + 237.3))) / (j + 237.3) ** 2 for j in tAve]

    # Calculating Julian Day Number (JDN)
    J = math.floor(275 * M / 9 - 30 + D) - 2

    # Considering leap year effects
    if M < 3:
        J = J + 2
    elif isLeapYear(Y) and M > 2:
        J += 1

    dr = 1 + 0.033 * math.cos(2 * math.pi / 365 * J)
    delta = 0.409 * math.sin(2 * math.pi / 365 * J - 1.39)
    ws = math.acos(-math.tan(Phi) * math.tan(delta))
    ra = 24 * 60 / math.pi * Gsc * dr * (
            ws * math.sin(Phi) * math.sin(delta) + math.cos(Phi) * math.cos(delta) * math.sin(ws))

    rso = (0.75 + 2 * 10 ** -5 * z) * ra  # or rso= (0.25+0.5)*ra

    rsRatio = [j / rso for j in rs]

    rsRatio = [1 if j > 1 else j for j in rsRatio]
    rns = [(1 - alfa) * j for j in rs]
    rnl = [Sigma / 2 * ((j + 273.16) ** 4 + (k + 273.16) ** 4) * (0.34 - 0.14 * l ** 0.5) * (1.35 * m - 0.35) for
           j, k, l, m in zip(tMin, tMax, ea, rsRatio)]
    rn = [j - k for j, k in zip(rns, rnl)]

    et = [(0.408 * sat * (r - G) + gamma * 900 / (ta + 273) * u * (ess - eaa)) / (sat + gamma * (1 + 0.34 * u)) for
          sat, r, ta, u, ess, eaa in zip(satVapPresSlope, rn, tAve, u2, es, ea)]

    return et


# ============= e Method ==============#
def e(t):
    eValues = [0.6108 * math.exp(17.27 * j / (j + 237.3)) for j in t]
    return eValues


def isLeapYear(Y):
    return Y % 4 == 0 and (Y % 100 != 0 or Y % 400 == 0)


class Predictor:
    def __init__(self, days, total_timestamp, bucket_depth, kc, database, layer_numbers, interval, current_hour,
                 soil_profile_dict, lat, lon):
        self.days = days
        self.total_timestamp = total_timestamp
        self.bucket_depth = bucket_depth
        self.kc = kc
        self.db = database
        self.layer_numbers = layer_numbers
        self.interval = interval
        self.last_update_time = current_hour
        self.n_timestamp = self.get_n_timestamp()
        self.soil_profile_dict = soil_profile_dict
        self.lat = lat
        self.lon = lon
        self.weather_data = self.fetch_weather()
        self.main_layers = []
        self.moist_predict = np.zeros([0, 0])  # soil moisture array (mm)
        self.historical_prediction = {}

    def get_n_timestamp(self):
        # self.update_n_timestamp()  # legacy
        n_timestamp = int(self.total_timestamp // self.interval)
        return n_timestamp

    # legacy
    def update_n_timestamp(self):
        current_hour = datetime.datetime.now().hour
        # current_hour = 13  # testing

        if current_hour <= self.last_update_time or self.n_timestamp is None:
            self.n_timestamp = int((self.total_timestamp - current_hour) // self.interval)
            self.historical_prediction = {}  # reset for new day
            self.moist_predict = np.zeros([self.layer_numbers, self.n_timestamp + 1])
            # self.historical_prediction_I10 = {}  # reset for new day
            # During the day
        else:
            self.n_timestamp -= 1
        self.last_update_time = current_hour

    def get_weather_api(self):
        # Get location
        # considering use sensor id and username 
        start_date = datetime.date.today()
        end_date = datetime.date.today() + datetime.timedelta(
            days=self.days + 1)  # for calculate min/Max temperature, need one more day
        url = "https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/{},{}/{}/{}?unitGroup=uk&key=XUDRTBS7Q3NSYEEB7BUUDBAB2".format(
            self.lat, self.lon, start_date, end_date)

        return url

    def fetch_weather(self):
        # print('Fetching weather...')
        url = self.get_weather_api()
        weather_data = requests.get(url=url).json()
        columns = (self.days + 1) * 24
        time = []
        temp = np.zeros(columns)
        tDew = np.zeros(columns)
        rhMean = np.zeros(columns)
        rs = np.zeros(columns)
        u10 = np.zeros(columns)
        I = np.zeros(columns)
        P = np.zeros(columns)

        # print('len w data days', len(weather_data['days']))
        # print('len w data days', weather_data['days'])
        min_temps = []
        max_temps = []
        for i in range(len(weather_data['days'])):
            day_min_temperature = 100
            day_max_temperature = -100
            hour_data = weather_data['days'][i]['hours']
            for j in range(len(hour_data)):
                temperature = hour_data[j]['temp']
                if temperature < day_min_temperature:
                    day_min_temperature = temperature
                if temperature > day_max_temperature:
                    day_max_temperature = temperature
            min_temps.append(day_min_temperature)
            max_temps.append(day_max_temperature)

        min_temps_interpolate = []
        max_temps_interpolate = []
        for i in range(1, len(weather_data['days'])):
            min_gap = (min_temps[i] - min_temps[i - 1]) / 24
            max_gap = (max_temps[i] - max_temps[i - 1]) / 24
            for j in range(24):
                min_temps_interpolate.append(min_temps[i - 1] + (j * min_gap))
                max_temps_interpolate.append(max_temps[i - 1] + (j * max_gap))

        # print('minTI', min_temps_interpolate)
        # print('maxTI', max_temps_interpolate)

        for i in range(self.days + 1):
            hour_data = weather_data['days'][i]['hours']
            # print('h len', len(hour_data))
            if len(hour_data) != 24:
                # print('in if', i, hour_data)
                temp2 = []
                fixed_hour_data = []
                for k in range(len(hour_data)):
                    if hour_data[k]['datetime'] not in temp2:
                        fixed_hour_data.append(hour_data[k])
                        temp2.append(hour_data[k]['datetime'])
                hour_data = fixed_hour_data
            date = weather_data['days'][i]['datetime']
            # print('date',type(date),date)
            # print('h_date',type(hour_data[0]['datetime']),hour_data[0]['datetime'])

            for j in range(len(hour_data)):  # j = 0~23
                time.append(date + ' ' + hour_data[j]['datetime'])
                temp[j + i * 24] = hour_data[j]['temp']
                tDew[j + i * 24] = hour_data[j]['dew']
                rhMean[j + i * 24] = hour_data[j]['humidity']
                if hour_data[j]['solarradiation']:
                    rs[j + i * 24] = hour_data[j]['solarradiation'] * 0.0864
                if hour_data[j]['precip']:
                    P[j + i * 24] = hour_data[j]['precip']
                u10[j + i * 24] = hour_data[j]['windspeed'] * 1.609344
                # if i == self.days:
                #     break

        start_time = datetime.datetime.now().astimezone()
        end_time = start_time + datetime.timedelta(days=self.days)
        print('start_end:', start_time, " ", end_time)
        target_time = []
        range_index = []
        prev_d = None
        prev_index = None
        prev_data = False
        for index, t in enumerate(time):
            t_temp = [int(tt) for tt in re.split('-| |:', t)]
            d = datetime.datetime(t_temp[0], t_temp[1], t_temp[2], t_temp[3], t_temp[4], t_temp[5], tzinfo=start_time.tzinfo)
            if start_time < d < end_time:
                # print('d ',d)
                if not prev_data:
                    range_index.append(prev_index)
                    target_time.append(prev_d.strftime("%a %b %d %Y %H:%M:%S %z"))
                    prev_data = True
                range_index.append(index)
                target_time.append(d.strftime("%a %b %d %Y %H:%M:%S %z"))
            elif d < start_time:
                prev_d = d
                prev_index = index

        print('rIndex', len(range_index), range_index)

        index = pd.to_datetime(target_time, format="%a %b %d %Y %H:%M:%S %z")
        # print('index:', len(index), type(index), index)
        data = {'Temp': temp[range_index[0]: range_index[-1] + 1], "Dew": tDew[range_index[0]: range_index[-1] + 1],
                "Rhmean": rhMean[range_index[0]: range_index[-1] + 1],
                "Radiation": rs[range_index[0]: range_index[-1] + 1],
                "Windspeed": u10[range_index[0]: range_index[-1] + 1],
                "Precipitation": P[range_index[0]: range_index[-1] + 1],
                "Irrigation": I[range_index[0]: range_index[-1] + 1], "name": target_time,
                "TempMin": min_temps_interpolate[range_index[0]: range_index[-1] + 1],
                "TempMax": max_temps_interpolate[range_index[0]: range_index[-1] + 1]}

        weatherData = pd.DataFrame(index=index, data=data)

        # print('wData')
        # print(weatherData.to_string())
        return weatherData

    def generate_initial_moisture(self, sensor_data, isRedisData=None, ):
        initial_values = []

        if isRedisData is True:
            sensor_data = [float(x) * 0.01 for x in sensor_data]

        print('param in sensor_data:', sensor_data)
        if len(sensor_data) > 0:
            try:
                if isinstance(sensor_data, dict):
                    for i in range(self.layer_numbers):
                        if i < 7:
                            initial_values.append(sensor_data['cap50'])
                        if 7 <= i < 13:
                            if sensor_data['cap100'] is not None:
                                initial_values.append(sensor_data['cap100'])
                            else:
                                initial_values.append(sensor_data['cap50'])
                        if i >= 13:
                            if sensor_data['cap150'] is not None:
                                initial_values.append(sensor_data['cap150'])
                            elif sensor_data['cap100'] is not None:
                                initial_values.append(sensor_data['cap100'])
                            else:
                                initial_values.append(sensor_data['cap50'])
                elif isinstance(sensor_data, list):
                    for i in range(self.layer_numbers):
                        if i < 7:
                            initial_values.append(sensor_data[4])
                        if 7 <= i < 13:
                            if sensor_data[9] is not None:
                                initial_values.append(sensor_data[9])
                            else:
                                initial_values.append(sensor_data[4])
                        if i >= 13:
                            if sensor_data[14] is not None:
                                initial_values.append(sensor_data[14])
                            elif sensor_data[9] is not None:
                                initial_values.append(sensor_data[9])
                            else:
                                initial_values.append(sensor_data[4])
                else:
                    raise Exception
            except Exception as e:
                print('Err in generate init moisture', e)
        # print('init', initial_values)
        return initial_values

    def get_all_layers(self, init_moisture):

        all_layers = []
        if len(init_moisture) > 0:
            try:
                self.create_layers(init_moisture, self.soil_profile_dict)
                checkLayerDepth(self.main_layers, self.bucket_depth)  # use try catch?
                all_layers = layerDescritization(self.main_layers, self.bucket_depth)  # all layers (buckets)
            except Exception as e:
                print("---Error in get all layers:", e)

        return all_layers

    def create_layers(self, initial_moist, soil_profile_data):
        self.main_layers = []
        n_lst = [1.5] + [1.01] * 19
        uptakes = [0, 0.01, 0.015, 0.04] + [0.02] * 16
        l = 0.5
        # print('---soil_profile_data',soil_profile_data)
        # w_point_50, f_capacity_50, saturation_50, w_point_100, f_capacity_100, saturation_100, w_point_150, f_capacity_150, saturation_150 = wp_fc_s
        for i in range(self.layer_numbers):
            if i < 5:
                self.main_layers.append(
                    SoilLayer(FC=soil_profile_data['f_capacity_50'],
                              WP=soil_profile_data['w_point_50'],
                              teta=initial_moist[i],
                              n=n_lst[i], L=l,
                              sat=soil_profile_data['saturation_50'],
                              depth=100, uptake=uptakes[i]))
            elif 5 <= i < 10:
                self.main_layers.append(
                    SoilLayer(FC=soil_profile_data['f_capacity_100'],
                              WP=soil_profile_data['w_point_100'],
                              teta=initial_moist[i], n=n_lst[i], L=l,
                              sat=soil_profile_data['saturation_100'],
                              depth=100, uptake=uptakes[i]))
            else:
                self.main_layers.append(
                    SoilLayer(FC=soil_profile_data['f_capacity_150'],
                              WP=soil_profile_data['w_point_150'],
                              teta=initial_moist[i], n=n_lst[i], L=l,
                              sat=soil_profile_data['saturation_150'],
                              depth=100, uptake=uptakes[i]))

    def calculate_et(self):

        today = datetime.date.today()

        # legacy
        # current_hour = datetime.datetime.now().hour
        # current_hour = 13
        # Evapo_transpiration mm/t
        # et = refET(tDew=self.weather_data['Dew'][current_hour:],
        #            tMin=self.weather_data['TempMin'][current_hour:],
        #            tMax=self.weather_data['TempMax'][current_hour:],
        #            rs=self.weather_data['Radiation'][current_hour:],
        #            u10=self.weather_data['Windspeed'][current_hour:],
        #            date=[today.day, today.month, today.year])

        et = refET(tDew=self.weather_data['Dew'],
                   tMin=self.weather_data['TempMin'],
                   tMax=self.weather_data['TempMax'],
                   rs=self.weather_data['Radiation'],
                   u10=self.weather_data['Windspeed'],
                   date=[today.day, today.month, today.year])
        # print('et', et)
        # transferring daily ET to hourly ET
        et = [i / 24 for i in et]
        if self.interval == 1:
            return et
        # sum up hourly ET to interval ET
        else:
            interval_et = self.convert_to_interval(et)
            return interval_et

    def convert_to_interval(self, values):
        interval_values = []
        interval_sum = values[0]
        for i in range(1, len(values)):
            if i % self.interval != 0:
                interval_sum += values[i]
            else:
                interval_values.append(interval_sum)
                interval_sum = values[i]
            if i == (len(values) - 1) and len(values) % self.interval == 0:
                interval_values.append(interval_sum)
        return interval_values

    def predict(self, all_layers, et, current_hour, sensor_id, completeID):
        # current_hour = 13  # testing
        if len(all_layers) > 0:
            try:
                self.moist_predict = np.zeros([len(all_layers), self.get_n_timestamp() + 1])
                d = np.zeros([len(all_layers), self.n_timestamp + 1])  # drainage
                a = np.zeros(len(all_layers))  # alfa, crop root water extraction ratio
                ks = np.zeros(len(all_layers))  # crop water stress factor
                profileFC = np.zeros(len(all_layers))
                profileWP = np.zeros(len(all_layers))
                drCo = 0.3
                for i, layer in enumerate(all_layers):  # adding soil moisture initial conditions (FC or WP or other)
                    # print(i,layer.s)
                    layer.updateS(layer.teta * layer.depth, 'mm')
                    self.moist_predict[i, 0] = layer.s
                    profileFC[i] = layer.FC
                    profileWP[i] = layer.WP

                # building root depth shape function
                da = 20
                c = -1.2
                dmax = 120  # parameters
                alfa = rootShapeFunction(da, c, dmax)  # shape function coefficients for Maize
                # print('len all layers:', len(all_layers))
                for i, layer in enumerate(all_layers):
                    if i * layer.depth >= dmax * 10:
                        a[i] = 0
                    else:
                        if i == 0:
                            z1 = 0.001
                        else:
                            z1 = i * layer.depth / 10
                        z2 = (i + 1) * layer.depth / 10
                        a[i] = alfa(z2) - alfa(z1)

                # ==================== Soil water balance=========================

                ro = 0.5  # Depletion factor

                # legacy
                # P_hour = self.weather_data['Precipitation'][current_hour:]
                # I_hour = self.weather_data['Irrigation'][current_hour:]

                P_hour = self.weather_data['Precipitation']
                I_hour = self.weather_data['Irrigation']
                P = self.convert_to_interval(P_hour)
                I = self.convert_to_interval(I_hour)

                print('lensss-', len(I), len(P), len(a), len(ks), len(et))
                for t in range(self.n_timestamp):  # t = 0~35
                    for i, layer in enumerate(all_layers):  # i = 0~19

                        ks[i] = cropStress(layer, ro)  # calculating crop water stress at this layer
                        if i == 0:
                            self.moist_predict[i, t + 1] = layer.s + I[t] + P[t] - a[i] * ks[i] * self.kc * et[
                                t] + layer.uptake

                        else:
                            self.moist_predict[i, t + 1] = layer.s + d[i - 1, t] - a[i] * ks[i] * self.kc * et[
                                t] + layer.uptake
                        # calculating drainage to the next layer
                        dummyLayer = SoilLayer(FC=layer.FC, WP=layer.WP,
                                               teta=self.moist_predict[i, t + 1] / layer.depth,
                                               n=layer.n,
                                               L=layer.L, sat=layer.sat, depth=layer.depth)
                        d[i, t] = hydraulicConductivity(dummyLayer, self.interval)

                        if self.moist_predict[i, t + 1] >= layer.sat * layer.depth:
                            d[i, t] = d[i, t] + (self.moist_predict[i, t + 1] - layer.sat * layer.depth) * drCo
                        elif self.moist_predict[i, t + 1] < layer.sat * layer.depth and I[t] + P[t] > 0 and i == 0:
                            d[i, t] = d[i, t] + (I[t] + P[t]) * drCo
                        elif self.moist_predict[i, t + 1] < layer.sat * layer.depth and I[t] + P[t] > 0 and i > 0:
                            d[i, t] = d[i, t] + d[i - 1, t] * drCo

                        # updating moisture at next timestep by subtracting calculated drainage
                        layer.updateS(self.moist_predict[i, t + 1] - d[i, t], unit='mm')  # updating layer moisture
                        all_layers[i] = layer

                        if self.moist_predict[i, t + 1] > layer.sat * layer.depth:
                            self.moist_predict[i, t + 1] = layer.sat * layer.depth
                        # break
                    # break
                print('Predict completed', sensor_id)
                print('Contents of prediction:')
                print('len prediction', len(self.moist_predict), len(self.moist_predict[0]))
                print(self.moist_predict)
                completeID.append(sensor_id)
                return self.moist_predict
            except Exception as e:
                print("---ERROR in predict:", e)

    # legacy
    # def update_moisture(self):
    #     print('---update_moisture---')
    #
    #     # update_init_moisture
    #     def adjust_prediction(sensor_values, moist_predict):
    #         predictions = []  # all layers at current hour
    #         for i in range(self.layer_numbers):
    #             predictions.append(moist_predict[i, 1] / 100)
    #
    #         ratio_50 = None
    #         ratio_100 = None
    #         ratio_150 = None
    #         # assume always have cap50 value
    #         if self.layer_numbers < 3:
    #             ratio_50 = sensor_values['cap50'] / predictions[self.layer_numbers - 1]  # if does not reach 30 cm
    #             print("Prediction above closest to 20-30 cm: ", predictions[self.layer_numbers - 1])
    #         else:
    #             ratio_50 = sensor_values['cap50'] / predictions[4]  # assume cap50 measured at 50 cm
    #             # print("Prediction 20-30 cm: ", predictions[2])
    #             # print("Prediction 40-50 cm: ", predictions[4])
    #             # print("Prediction 90-100 cm: ", predictions[9])
    #
    #         if sensor_values['cap100'] is not None:
    #             if 7 < self.layer_numbers < 10:
    #                 ratio_100 = sensor_values['cap100'] / predictions[
    #                     self.layer_numbers - 1]  # if does not reach 100 cm
    #                 print("Prediction above closest to 90-100 cm: ", predictions[self.layer_numbers - 1])
    #             elif self.layer_numbers >= 10:
    #                 ratio_100 = sensor_values['cap100'] / predictions[9]  # assume cap100 measured at 100 cm
    #                 print("Prediction 90-100 cm: ", predictions[9])
    #
    #         if sensor_values['cap150'] is not None:
    #             if 13 < self.layer_numbers < 15:
    #                 ratio_150 = sensor_values['cap150'] / predictions[
    #                     self.layer_numbers - 1]  # if does not reach 150 cm
    #                 print("Prediction above closest to 140-150 cm: ", predictions[self.layer_numbers - 1])
    #             elif self.layer_numbers >= 15:
    #                 ratio_150 = sensor_values['cap150'] / predictions[14]  # assume cap150 measured at 150 cm
    #                 print("Prediction 140-150 cm: ", predictions[14])
    #
    #         print("Ratio 50: ", ratio_50)
    #         if ratio_100 is not None:
    #             print("Ratio 100: ", ratio_100)
    #         if ratio_150 is not None:
    #             print("Ratio 150: ", ratio_150)
    #
    #         adjust_predict = []
    #         for i in range(len(predictions)):
    #             if i < 7:  # 0-70 cm
    #                 new_prediction = predictions[i] * ratio_50
    #             elif 7 <= i < 13:  # 70-130 cm
    #                 if ratio_100 is not None:
    #                     new_prediction = predictions[i] * ratio_100
    #                 else:
    #                     new_prediction = predictions[i] * ratio_50
    #                     # print(str(i)+" use ratio_50")
    #             else:  # > 130 cm
    #                 if ratio_150 is not None:
    #                     new_prediction = predictions[i] * ratio_150
    #                 elif ratio_100 is not None:
    #                     new_prediction = predictions[i] * ratio_100
    #                     # print(str(i)+" use ratio_100")
    #                 else:
    #                     new_prediction = predictions[i] * ratio_50
    #                     # print(str(i)+" use ratio_50")
    #             adjust_predict.append(new_prediction)
    #         return adjust_predict
    #
    #     # Get sensor data
    #     current_hour = datetime.datetime.now().hour
    #     # current_hour = 13  # testing
    #     # self.update_n_timestamp()
    #
    #     wp_fc_s = self.db.get_wp_fc_s()
    #     self.setSoilProfile(wp_fc_s)
    #
    #     sensor_data = self.db.get_sensor_data()  # sensor version
    #     corrected_init_moist = adjust_prediction(sensor_data, self.moist_predict)  # 需要前一次預測的第index 1筆資料做修正
    #
    #     all_layers = self.get_all_layers(corrected_init_moist)  # no need
    #     et = self.calculate_et()  # no need
    #     self.predict(all_layers, et, current_hour)  # 改寫了之前全部的預測 no need
    #     # adjusted_prediction = adjust_prediction(sensor_data, self.moist_predict)
    #     # all_layers = self.get_all_layers(adjusted_prediction)
    #
    #     # 插入爬蟲拿資料？
    #     # print('Scraping....')
    #     # scraper_data = self.scraper.get_scraper_data()  # agr vic version
    #     # print('---updated scrape data: ', scraper_data)
    #     print('Adjusting...')
    #
    #     # new_init_moist = adjust_prediction(scraper_data, self.moist_predict)  # 需要前一次預測的第index 1筆資料做修正
    #     # print('---new_init_moist', new_init_moist)
    #     # print('---new_init_moist_50', new_init_moist[4])
    #     # print('---new_init_moist_100', new_init_moist[9])
    #     # init_moisture2 = self.generate_initial_moisture(scraper_data)
    #
    #     # Update predictions
    #     print('Predicting...')
    #
    #     # self.predict_I10(all_layers, et, current_hour)  # 改寫了之前全部的預測
    #     # self.predict_I50(all_layers, et, current_hour)  # 改寫了之前全部的預測
    #     # self.predict_I100(all_layers, et, current_hour)  # 改寫了之前全部的預測
    #     print("Update Predictions Complete")
    #     # print("New predictions")
    #     # for index, prediction in enumerate(self.moist_predict):
    #     #     print('This is layer ', index + 1)
    #     #     print(prediction)

    def get_all_layers_soil_type(self, soil_profile_data):
        type_dict = {}
        for i in range(1, self.layer_numbers + 1):
            if i <= 5:
                type_dict['layer ' + str(i)] = soil_profile_data['soil_type_25']
            elif 5 < i <= 10:
                type_dict['layer ' + str(i)] = soil_profile_data['soil_type_75']
            else:
                type_dict['layer ' + str(i)] = soil_profile_data['soil_type_125']
        return type_dict

    def setSoilProfile(self, wp_fc_s_data):
        i = 0
        for key in list(self.soil_profile_dict.keys()):
            self.soil_profile_dict[key] = wp_fc_s_data[i]
            i += 1

    def get_time(self):
        time_now = datetime.datetime.now().strftime('%Y-%m-%d %H')
        # print('Time: ', time_now)
        return time_now

    def output_data(self):
        def write_to_CSV(historical_prediction):
            path = 'historical_prediction_data/' + datetime.datetime.now().strftime('%Y-%m-%d') + '.csv'
            with open(path, 'a+', encoding='UTF8', newline='') as f:
                writer = csv.writer(f)
                prev_prediction = list(historical_prediction.items())[-1]
                writer.writerow([prev_prediction[0]])
                for each_layer_prediction in prev_prediction[1]:
                    writer.writerow(each_layer_prediction)
                f.close()
            print('data out put completed')

        time_label = self.get_time()
        # self.historical_time_label.append(time_label)
        temp = []
        for index, prediction in enumerate(self.moist_predict):
            temp.append([index + 1] + [round(n, 3) for n in list(prediction)])
        self.historical_prediction[time_label] = temp
        # print('HIST', self.historical_prediction)
        write_to_CSV(self.historical_prediction)

    def adjust_prediction(self, sensor_values, moist_predict):
        # predictions = []  # all layers at current hour
        predictions = [float(x) * 0.01 for x in moist_predict]  # all layers at current hour

        # for i in range(self.layer_numbers):
        #     predictions.append(moist_predict[i, 1] / 100)

        ratio_50 = None
        ratio_100 = None
        ratio_150 = None
        # assume always have cap50 value
        if self.layer_numbers < 3:
            if predictions[self.layer_numbers - 1] != 0:
                ratio_50 = sensor_values['cap50'] / predictions[self.layer_numbers - 1]  # if does not reach 30 cm
                print("Prediction above closest to 20-30 cm: ", predictions[self.layer_numbers - 1])
            else:
                ratio_50 = 1
        else:
            if predictions[4] != 0:
                ratio_50 = sensor_values['cap50'] / predictions[4]  # assume cap50 measured at 50 cm
            else:
                ratio_50 = 1
            # print("Prediction 20-30 cm: ", predictions[2])
            # print("Prediction 40-50 cm: ", predictions[4])
            # print("Prediction 90-100 cm: ", predictions[9])

        if sensor_values['cap100'] is not None:
            if 7 < self.layer_numbers < 10:
                if predictions[self.layer_numbers - 1] != 0:
                    ratio_100 = sensor_values['cap100'] / predictions[self.layer_numbers - 1]  # if does not reach 100 cm
                    print("Prediction above closest to 90-100 cm: ", predictions[self.layer_numbers - 1])
                else:
                    ratio_100 = 1
            elif self.layer_numbers >= 10:
                if predictions[9] != 0:
                    ratio_100 = sensor_values['cap100'] / predictions[9]  # assume cap100 measured at 100 cm
                    print("Prediction 90-100 cm: ", predictions[9])
                else:
                    ratio_100 = 1

        if sensor_values['cap150'] is not None:
            if 13 < self.layer_numbers < 15:
                if predictions[self.layer_numbers - 1]:
                    ratio_150 = sensor_values['cap150'] / predictions[self.layer_numbers - 1]  # if does not reach 150 cm
                    print("Prediction above closest to 140-150 cm: ", predictions[self.layer_numbers - 1])
                else:
                    ratio_150 = 1
            elif self.layer_numbers >= 15:
                if predictions[14] != 0:
                    ratio_150 = sensor_values['cap150'] / predictions[14]  # assume cap150 measured at 150 cm
                    print("Prediction 140-150 cm: ", predictions[14])
                else:
                    ratio_150 = 1

        print("Ratio 50: ", ratio_50)
        if ratio_100 is not None:
            print("Ratio 100: ", ratio_100)
        if ratio_150 is not None:
            print("Ratio 150: ", ratio_150)

        corrected_sensor_data = []
        for i in range(len(predictions)):
            if predictions[i] != 0:
                if i < 7:  # 0-70 cm
                    new_data = predictions[i] * ratio_50
                elif 7 <= i < 13:  # 70-130 cm
                    if ratio_100 is not None:
                        new_data = predictions[i] * ratio_100
                    else:
                        new_data = predictions[i] * ratio_50
                        # print(str(i)+" use ratio_50")
                else:  # > 130 cm
                    if ratio_150 is not None:
                        new_data = predictions[i] * ratio_150
                    elif ratio_100 is not None:
                        new_data = predictions[i] * ratio_100
                        # print(str(i)+" use ratio_100")
                    else:
                        new_data = predictions[i] * ratio_50
                        # print(str(i)+" use ratio_50")
            else:
                if i < 7:
                    new_data = sensor_values['cap50']
                elif 7 < i < 13:
                    new_data = sensor_values['cap100']
                else:
                    new_data = sensor_values['cap150']

            corrected_sensor_data.append(new_data)

        # convert to % value  -> 要在這換？？
        # corrected_sensor_data = [x * 100 for x in corrected_sensor_data]

        return corrected_sensor_data
