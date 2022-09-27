import csv
import matplotlib.pyplot as plt
import datetime

hist_path = []
hist_path_I10 = []
hist_path_I50 = []
hist_path_I100 = []


def update_file_path():
    path = 'historical_prediction_data/' + datetime.datetime.now().strftime('%Y-%m-%d') + '.csv'
    if path not in hist_path:
        hist_path.append(path)
    print('histPath', hist_path)
    return hist_path


def update_file_path_I10():
    path = 'historical_prediction_data/' + datetime.datetime.now().strftime('%Y-%m-%d') + '_I10.csv'
    if path not in hist_path_I10:
        hist_path_I10.append(path)
    print('histPath_I10', hist_path_I10)
    return hist_path_I10


def update_file_path_I50():
    path = 'historical_prediction_data/' + datetime.datetime.now().strftime('%Y-%m-%d') + '_I50.csv'
    if path not in hist_path_I50:
        hist_path_I50.append(path)
    print('histPath_I50', hist_path_I50)
    return hist_path_I50


def update_file_path_I100():
    path = 'historical_prediction_data/' + datetime.datetime.now().strftime('%Y-%m-%d') + '_I100.csv'
    if path not in hist_path_I100:
        hist_path_I100.append(path)
    print('histPath_I100', hist_path_I100)
    return hist_path_I100


def read_data():
    labels = []
    data_30 = []
    data_50 = []
    data_70 = []
    data_100 = []
    all_file_path = update_file_path()
    for path in all_file_path:
        with open(path, 'r') as f:
            reader = csv.reader(f)
            for row in reader:
                if len(row) == 1:
                    label = row[0].replace('2022-04', 'Apr')
                    label = label.replace('2022-05', 'May')
                    labels.append(label)
                if len(row) != 1 and row[0] == '3':
                    data_30.append([float(data) for data in row[1:]])
                if len(row) != 1 and row[0] == '5':
                    data_50.append([float(data) for data in row[1:]])
                if len(row) != 1 and row[0] == '7':
                    data_70.append([float(data) for data in row[1:]])
                if len(row) != 1 and row[0] == '10':
                    data_100.append([float(data) for data in row[1:]])
            f.close()

    return labels, data_30, data_50, data_70, data_100


def read_data_I10():
    labels = []
    data_30 = []
    data_50 = []
    data_70 = []
    data_100 = []
    all_file_path = update_file_path_I10()
    for path in all_file_path:
        with open(path, 'r') as f:
            reader = csv.reader(f)
            for row in reader:
                if len(row) == 1:
                    label = row[0].replace('2022-04', 'Apr')
                    label = label.replace('2022-05', 'May')
                    labels.append(label)
                if len(row) != 1 and row[0] == '3':
                    data_30.append([float(data) for data in row[1:]])
                if len(row) != 1 and row[0] == '5':
                    data_50.append([float(data) for data in row[1:]])
                if len(row) != 1 and row[0] == '7':
                    data_70.append([float(data) for data in row[1:]])
                if len(row) != 1 and row[0] == '10':
                    data_100.append([float(data) for data in row[1:]])
            f.close()

    return labels, data_30, data_50, data_70, data_100


def read_data_I50():
    labels = []
    data_30 = []
    data_50 = []
    data_70 = []
    data_100 = []
    all_file_path = update_file_path_I50()
    for path in all_file_path:
        with open(path, 'r') as f:
            reader = csv.reader(f)
            for row in reader:
                if len(row) == 1:
                    label = row[0].replace('2022-04', 'Apr')
                    label = label.replace('2022-05', 'May')
                    labels.append(label)
                if len(row) != 1 and row[0] == '3':
                    data_30.append([float(data) for data in row[1:]])
                if len(row) != 1 and row[0] == '5':
                    data_50.append([float(data) for data in row[1:]])
                if len(row) != 1 and row[0] == '7':
                    data_70.append([float(data) for data in row[1:]])
                if len(row) != 1 and row[0] == '10':
                    data_100.append([float(data) for data in row[1:]])
            f.close()

    return labels, data_30, data_50, data_70, data_100


def read_data_I100():
    labels = []
    data_30 = []
    data_50 = []
    data_70 = []
    data_100 = []
    all_file_path = update_file_path_I100()
    for path in all_file_path:
        with open(path, 'r') as f:
            reader = csv.reader(f)
            for row in reader:
                if len(row) == 1:
                    label = row[0].replace('2022-04', 'Apr')
                    label = label.replace('2022-05', 'May')
                    labels.append(label)
                if len(row) != 1 and row[0] == '3':
                    data_30.append([float(data) for data in row[1:]])
                if len(row) != 1 and row[0] == '5':
                    data_50.append([float(data) for data in row[1:]])
                if len(row) != 1 and row[0] == '7':
                    data_70.append([float(data) for data in row[1:]])
                if len(row) != 1 and row[0] == '10':
                    data_100.append([float(data) for data in row[1:]])
            f.close()

    return labels, data_30, data_50, data_70, data_100


def read_ag_vic_data():
    vic_data_30 = []
    vic_data_50 = []
    vic_data_70 = []
    vic_data_100 = []
    with open('data_collection/Ouyen.csv', 'r') as f:
        reader = csv.reader(f)
        for row in reader:
            if row[0] != 'Datetime':
                vic_data_30.append(int(row[1].replace('%', '')) * 0.3)
                vic_data_50.append(int(row[3].replace('%', '')) * 0.3)
                vic_data_70.append(int(row[5].replace('%', '')) * 0.3)
                vic_data_100.append(int(row[-1].replace('%', '')) * 0.3)
        f.close()
    return vic_data_30, vic_data_50, vic_data_70, vic_data_100


def get_labels(num, date):
    labels = [date]
    date = str(date).split()
    hour = int(date[1])
    date = date[0].split('-')
    year = int(date[0])
    month = int(date[1])
    day = int(date[2])
    # print(month, day, hour)

    for i in range(num):
        hour += 1
        if hour == 24:
            hour = 0
            day += 1
            if day == 31 and month in [2, 4, 6, 9, 11]:
                day = 1
                month += 1
            elif day == 32 and month in [1, 3, 5, 7, 8, 10, 12]:
                day = 1
                month += 1
                if month == 13:
                    month = 1
                    year += 1
        if month == 1:
            month_str = 'Jan'
        elif month == 2:
            month_str = 'Feb'
        elif month == 3:
            month_str = 'Mar'
        elif month == 4:
            month_str = 'Apr'
        elif month == 5:
            month_str = 'May'
        elif month == 6:
            month_str = 'Jun'
        elif month == 7:
            month_str = 'Jul'
        elif month == 8:
            month_str = 'Aug'
        elif month == 9:
            month_str = 'Sep'
        elif month == 10:
            month_str = 'Oct'
        elif month == 11:
            month_str = 'Nov'
        elif month == 12:
            month_str = 'Dec'

        date = str(year) + '-' + month_str + '-' + str(day) + ' ' + str(hour)
        labels.append(date)

    return labels


def draw(test_labels):
    vic_data = read_ag_vic_data()  # vic_data_30, vic_data_50, vic_data_70, vic_data_100
    data = read_data()  # labels, data_30, data_50, data_70, data_100
    labels, data_30, data_50, data_70, data_100 = data
    data_num = len(labels)
    data_num = 25
    # print('data NUM', data_num)
    labels = test_labels  # 最開始到最後，非動態

    draw_data = [data_30, data_50, data_70, data_100]
    for layer_index, layer_data in enumerate(draw_data):
        title, save_name, ag_vic_label = '', '', ''
        if layer_index == 0:
            title = 'Layer 20-30 cm'
            save_name = './prediction_series_30cm'
            ag_vic_label = 'ag_VIC_30cm'
        elif layer_index == 1:
            title = 'Layer 40-50 cm'
            save_name = './prediction_series_50cm'
            ag_vic_label = 'ag_VIC_50cm'
        elif layer_index == 2:
            title = 'Layer 60-70 cm'
            save_name = './prediction_series_70cm'
            ag_vic_label = 'ag_VIC_100cm'
        elif layer_index == 3:
            title = 'Layer 90-100 cm'
            save_name = './prediction_series_100cm'
            ag_vic_label = 'ag_VIC_100cm'

        plt.figure(figsize=(data_num, 5))
        plt.plot(vic_data[layer_index][:data_num], label=ag_vic_label)  # vic data 一開始應該不夠長

        fig_data = []
        for index, data in enumerate(layer_data):
            data = [None] * index + data
            fig_data.append(data)
        # print('fig data len', len(fig_data))
        # print(fig_data)

        for i in range(len(fig_data)):
            # print('i', i)
            plt.plot(fig_data[i][:data_num], label=labels[i])

        # s_30 = [30, 30, 29.69102238, 29.76867613, 29.83373014, 30, 29.59648825, 29.65717483, 29.70479967, 29.75366213,
        #         29.81170566, 29.85453189,
        #         29.89814803, 30, 29.55991303]

        # sat = 0.3
        # sensor_30 = [100] * data_num
        # sensor_30 = [data * sat for data in sensor_30]

        # plt.plot(sensor_30[:data_num], label='30cm measurement')
        # labels = ['2022-04-06 00:00:00', '2022-04-06 01:00:00', '2022-04-06 02:00:00', '2022-04-06 03:00:00',
        #           '2022-04-06 04:00:00', '2022-04-06 05:00:00', '2022-04-06 06:00:00', '2022-04-06 07:00:00',
        #           '2022-04-06 08:00:00', '2022-04-06 09:00:00', '2022-04-06 10:00:00', '2022-04-06 11:00:00',
        #           '2022-04-06 12:00:00', '2022-04-06 13:00:00', '2022-04-06 14:00:00']
        plt.xticks([0, data_num // 2, data_num - 1], [labels[0], labels[data_num // 2], labels[data_num - 1]])
        plt.ylim([18, 34])
        plt.title(title)
        plt.legend()
        plt.savefig(save_name)
    plt.close()
    print('Drawing completed')


def draw_I10(test_labels):
    vic_data = read_ag_vic_data()  # vic_data_30, vic_data_50, vic_data_70, vic_data_100
    data = read_data_I10()  # labels, data_30, data_50, data_70, data_100
    labels, data_30, data_50, data_70, data_100 = data
    data_num = len(labels)
    data_num = 25
    # print('data NUM', data_num)
    labels = test_labels  # 最開始到最後，非動態

    draw_data = [data_30, data_50, data_70, data_100]
    for layer_index, layer_data in enumerate(draw_data):
        title, save_name, ag_vic_label = '', '', ''
        if layer_index == 0:
            title = 'Layer 20-30 cm'
            save_name = './prediction_series_30cm_I10'
            ag_vic_label = 'ag_VIC_30cm'
        elif layer_index == 1:
            title = 'Layer 40-50 cm'
            save_name = './prediction_series_50cm_I10'
            ag_vic_label = 'ag_VIC_50cm'
        elif layer_index == 2:
            title = 'Layer 60-70 cm'
            save_name = './prediction_series_70cm_I10'
            ag_vic_label = 'ag_VIC_100cm'
        elif layer_index == 3:
            title = 'Layer 90-100 cm'
            save_name = './prediction_series_100cm_I10'
            ag_vic_label = 'ag_VIC_100cm'

        plt.figure(figsize=(data_num, 5))
        plt.plot(vic_data[layer_index][:data_num], label=ag_vic_label)  # vic data 一開始應該不夠長

        fig_data = []
        for index, data in enumerate(layer_data):
            data = [None] * index + data
            fig_data.append(data)
        # print('fig data len', len(fig_data))
        # print(fig_data)

        for i in range(len(fig_data)):
            # print('i', i)
            plt.plot(fig_data[i][:data_num], label=labels[i])

        # s_30 = [30, 30, 29.69102238, 29.76867613, 29.83373014, 30, 29.59648825, 29.65717483, 29.70479967, 29.75366213,
        #         29.81170566, 29.85453189,
        #         29.89814803, 30, 29.55991303]

        # sat = 0.3
        # sensor_30 = [100] * data_num
        # sensor_30 = [data * sat for data in sensor_30]

        # plt.plot(sensor_30[:data_num], label='30cm measurement')
        # labels = ['2022-04-06 00:00:00', '2022-04-06 01:00:00', '2022-04-06 02:00:00', '2022-04-06 03:00:00',
        #           '2022-04-06 04:00:00', '2022-04-06 05:00:00', '2022-04-06 06:00:00', '2022-04-06 07:00:00',
        #           '2022-04-06 08:00:00', '2022-04-06 09:00:00', '2022-04-06 10:00:00', '2022-04-06 11:00:00',
        #           '2022-04-06 12:00:00', '2022-04-06 13:00:00', '2022-04-06 14:00:00']
        plt.xticks([0, data_num // 2, data_num - 1], [labels[0], labels[data_num // 2], labels[data_num - 1]])
        plt.ylim([13, 52])
        plt.title(title)
        plt.legend()
        plt.savefig(save_name)
    plt.close()
    print('I10 Drawing completed')


def draw_I50(test_labels):
    vic_data = read_ag_vic_data()  # vic_data_30, vic_data_50, vic_data_70, vic_data_100
    data = read_data_I50()  # labels, data_30, data_50, data_70, data_100
    labels, data_30, data_50, data_70, data_100 = data
    data_num = len(labels)
    data_num = 25
    # print('data NUM', data_num)
    labels = test_labels  # 最開始到最後，非動態

    draw_data = [data_30, data_50, data_70, data_100]
    for layer_index, layer_data in enumerate(draw_data):
        title, save_name, ag_vic_label = '', '', ''
        if layer_index == 0:
            title = 'Layer 20-30 cm'
            save_name = './prediction_series_30cm_I50'
            ag_vic_label = 'ag_VIC_30cm'
        elif layer_index == 1:
            title = 'Layer 40-50 cm'
            save_name = './prediction_series_50cm_I50'
            ag_vic_label = 'ag_VIC_50cm'
        elif layer_index == 2:
            title = 'Layer 60-70 cm'
            save_name = './prediction_series_70cm_I50'
            ag_vic_label = 'ag_VIC_100cm'
        elif layer_index == 3:
            title = 'Layer 90-100 cm'
            save_name = './prediction_series_100cm_I50'
            ag_vic_label = 'ag_VIC_100cm'

        plt.figure(figsize=(data_num, 5))
        plt.plot(vic_data[layer_index][:data_num], label=ag_vic_label)  # vic data 一開始應該不夠長

        fig_data = []
        for index, data in enumerate(layer_data):
            data = [None] * index + data
            fig_data.append(data)
        # print('fig data len', len(fig_data))
        # print(fig_data)

        for i in range(len(fig_data)):
            # print('i', i)
            plt.plot(fig_data[i][:data_num], label=labels[i])

        # s_30 = [30, 30, 29.69102238, 29.76867613, 29.83373014, 30, 29.59648825, 29.65717483, 29.70479967, 29.75366213,
        #         29.81170566, 29.85453189,
        #         29.89814803, 30, 29.55991303]

        # sat = 0.3
        # sensor_30 = [100] * data_num
        # sensor_30 = [data * sat for data in sensor_30]

        # plt.plot(sensor_30[:data_num], label='30cm measurement')
        # labels = ['2022-04-06 00:00:00', '2022-04-06 01:00:00', '2022-04-06 02:00:00', '2022-04-06 03:00:00',
        #           '2022-04-06 04:00:00', '2022-04-06 05:00:00', '2022-04-06 06:00:00', '2022-04-06 07:00:00',
        #           '2022-04-06 08:00:00', '2022-04-06 09:00:00', '2022-04-06 10:00:00', '2022-04-06 11:00:00',
        #           '2022-04-06 12:00:00', '2022-04-06 13:00:00', '2022-04-06 14:00:00']
        plt.xticks([0, data_num // 2, data_num - 1], [labels[0], labels[data_num // 2], labels[data_num - 1]])
        plt.ylim([13, 52])
        plt.title(title)
        plt.legend()
        plt.savefig(save_name)
    plt.close()
    print('I50 Drawing completed')


def draw_I100(test_labels):
    vic_data = read_ag_vic_data()  # vic_data_30, vic_data_50, vic_data_70, vic_data_100
    data = read_data_I100()  # labels, data_30, data_50, data_70, data_100
    labels, data_30, data_50, data_70, data_100 = data
    data_num = len(labels)
    data_num = 25
    # print('data NUM', data_num)
    labels = test_labels  # 最開始到最後，非動態

    draw_data = [data_30, data_50, data_70, data_100]
    for layer_index, layer_data in enumerate(draw_data):
        title, save_name, ag_vic_label = '', '', ''
        if layer_index == 0:
            title = 'Layer 20-30 cm'
            save_name = './prediction_series_30cm_I100'
            ag_vic_label = 'ag_VIC_30cm'
        elif layer_index == 1:
            title = 'Layer 40-50 cm'
            save_name = './prediction_series_50cm_I100'
            ag_vic_label = 'ag_VIC_50cm'
        elif layer_index == 2:
            title = 'Layer 60-70 cm'
            save_name = './prediction_series_70cm_I100'
            ag_vic_label = 'ag_VIC_100cm'
        elif layer_index == 3:
            title = 'Layer 90-100 cm'
            save_name = './prediction_series_100cm_I100'
            ag_vic_label = 'ag_VIC_100cm'

        plt.figure(figsize=(data_num, 5))
        plt.plot(vic_data[layer_index][:data_num], label=ag_vic_label)  # vic data 一開始應該不夠長

        fig_data = []
        for index, data in enumerate(layer_data):
            data = [None] * index + data
            fig_data.append(data)
        # print('fig data len', len(fig_data))
        # print(fig_data)

        for i in range(len(fig_data)):
            # print('i', i)
            plt.plot(fig_data[i][:data_num], label=labels[i])

        # s_30 = [30, 30, 29.69102238, 29.76867613, 29.83373014, 30, 29.59648825, 29.65717483, 29.70479967, 29.75366213,
        #         29.81170566, 29.85453189,
        #         29.89814803, 30, 29.55991303]

        # sat = 0.3
        # sensor_30 = [100] * data_num
        # sensor_30 = [data * sat for data in sensor_30]

        # plt.plot(sensor_30[:data_num], label='30cm measurement')
        # labels = ['2022-04-06 00:00:00', '2022-04-06 01:00:00', '2022-04-06 02:00:00', '2022-04-06 03:00:00',
        #           '2022-04-06 04:00:00', '2022-04-06 05:00:00', '2022-04-06 06:00:00', '2022-04-06 07:00:00',
        #           '2022-04-06 08:00:00', '2022-04-06 09:00:00', '2022-04-06 10:00:00', '2022-04-06 11:00:00',
        #           '2022-04-06 12:00:00', '2022-04-06 13:00:00', '2022-04-06 14:00:00']
        plt.xticks([0, data_num // 2, data_num - 1], [labels[0], labels[data_num // 2], labels[data_num - 1]])
        plt.ylim([13, 117])
        plt.title(title)
        plt.legend()
        plt.savefig(save_name)
    plt.close()
    print('I100 Drawing completed')
