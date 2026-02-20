# !usr/bin/env python
# -*- coding:utf-8 -*-

import csv
import datetime
import pandas as pd
import time
import uuid

# import chardet


def get_rows_quantity(csv_file):
    df = pd.read_csv(csv_file, header=None)
    # print(df.shape[0])
    return df.shape[0]


def get_columns_quantity(csv_file):
    df = pd.read_csv(csv_file, header=None)
    # print(df.shape[1])
    return df.shape[1]


def pd_read_csv_head(csv_path):
    df = pd.read_csv(csv_path, header=None, keep_default_na=False)
    # print(list(df.columns.values))
    return list(df.columns.values)


def pd_read_csv_column(csv_path, column_num):
    df = pd.read_csv(csv_path, header=None, keep_default_na=False)
    # print(df.iloc[:, column_num])
    return list(df.iloc[:, column_num])


def pd_read_csv_column_with_default_header_setting(csv_path, column_num):
    df = pd.read_csv(csv_path, keep_default_na=False)
    # print(df.iloc[:, column_num])
    return list(df.iloc[:, column_num])


def pd_read_csv_column_by_name(csv_path, column_name):
    df = pd.read_csv(csv_path, header=None, keep_default_na=False)
    # print(df[column_name])
    return df[column_name]


def pd_read_csv_column_by_name_header_set(csv_path, column_name):
    df = pd.read_csv(csv_path, keep_default_na=False)
    # print(df[column_name])
    # print(list(df[column_name]))
    return list(df[column_name])


def pd_read_csv_row(csv_path, row_num):
    df = pd.read_csv(csv_path, header=None, keep_default_na=False)
    # print(type(df.iloc[row_num, :]))
    # print(list(df.iloc[row_num, :]))
    return list(df.iloc[row_num, :])


def pd_read_csv_cell(csv_path, row_num, column_num):
    df = pd.read_csv(csv_path, header=None, keep_default_na=False)
    # print(type(df.iloc[row_num, column_num]))
    # print(df.iloc[row_num, column_num])
    return df.iloc[row_num, column_num]


def sort_csv(file_name, sort_name, ascending_seq, inplace_state, export_file_name):
    csv_df = pd.read_csv(file_name)
    csv_df.sort_values(
        sort_name, axis=0, ascending=[ascending_seq], inplace=inplace_state
    )
    csv_df.to_csv(export_file_name, index=False)


def sort_csv_by_multi_name(
    file_name,
    sort_name1,
    sort_name2,
    ascending_seq1,
    ascending_seq2,
    inplace_state,
    export_file_name,
):
    csv_df = pd.read_csv(file_name)
    csv_df.sort_values(
        by=[sort_name1, sort_name2],
        axis=0,
        ascending=[ascending_seq1, ascending_seq2],
        inplace=inplace_state,
    )
    csv_df.to_csv(export_file_name, index=False)


def creat_csv(csv_file_to_be_created, csv_header):
    # print(csv_file_to_be_created)
    with open(csv_file_to_be_created, "w", encoding="utf8", newline="") as f_bft:
        csv_write = csv.writer(f_bft)
        csv_write.writerow(csv_header)


def read_csv_one_row(csv_path, row_num):
    rows_list = []
    with open(csv_path, "r") as csv_file:
        reader = csv.reader(csv_file)
        for row in reader:
            if row:
                rows_list.append(row)
    # print(rows_list[row_num])
    return rows_list[row_num]


def read_csv_all_rows(csv_path):
    rows_list = []
    with open(csv_path, "r") as csv_file:
        reader = csv.reader(csv_file)
        for row in reader:
            rows_list.append(row)
    # print(rows_list)
    return rows_list


def read_csv_one_column(csv_path, column_num):
    rows_list = []
    column_list = []
    with open(csv_path, "r") as csv_file:
        reader = csv.reader(csv_file)
        for row in reader:
            rows_list.append(row)

    if len(rows_list):
        for i in range(len(rows_list)):
            column_list.append(rows_list[i][column_num])
        return column_list
    else:
        print("row - empty")


# read specific cell data
def read_csv_cell(csv_path, row_num, column_num):
    specific_row = read_csv_one_row(csv_path, row_num)
    return specific_row[column_num]


# write data to specific .csv file
def write_row_to_csv(row_data, csv_path):
    with open(
        csv_path, "a", encoding="utf8", newline=""
    ) as f:  # newline='': delete empty line
        writer = csv.writer(f)
        writer.writerow(row_data)


# calculate testing cycle time 20230313123924
def calculate_cycle_time(start_time, end_time):
    start_time_split_with_space = start_time.split(" ")
    start_time_split_before_space = start_time_split_with_space[0]
    start_time_split_after_space = start_time_split_with_space[1]

    start_time_year_month_day = start_time_split_before_space.split("-")
    # print(start_time_year_month_day)
    start_time_hour_minute_second = start_time_split_after_space.split(":")
    # print(start_time_hour_minute_second)

    start_time_year = int(start_time_year_month_day[0])
    start_time_month = int(start_time_year_month_day[1])
    start_time_day = int(start_time_year_month_day[2])
    start_time_hour = int(start_time_hour_minute_second[0])
    start_time_minute = int(start_time_hour_minute_second[1])
    start_time_second = int(start_time_hour_minute_second[2])

    end_time_split_with_space = end_time.split(" ")
    end_time_split_before_space = end_time_split_with_space[0]
    end_time_split_after_space = end_time_split_with_space[1]

    end_time_year_month_day = end_time_split_before_space.split("-")
    end_time_hour_minute_second = end_time_split_after_space.split(":")
    end_time_year = int(end_time_year_month_day[0])
    end_time_month = int(end_time_year_month_day[1])
    end_time_day = int(end_time_year_month_day[2])
    end_time_hour = int(end_time_hour_minute_second[0])
    end_time_minute = int(end_time_hour_minute_second[1])
    end_time_second = int(end_time_hour_minute_second[2])

    t_start = datetime.datetime(
        start_time_year,
        start_time_month,
        start_time_day,
        start_time_hour,
        start_time_minute,
        start_time_second,
    )
    t_start_total_sec = (t_start - datetime.datetime(1970, 1, 1)).total_seconds()

    t_end = datetime.datetime(
        end_time_year,
        end_time_month,
        end_time_day,
        end_time_hour,
        end_time_minute,
        end_time_second,
    )
    t_end_total_sec = (t_end - datetime.datetime(1970, 1, 1)).total_seconds()

    # print(t_end_total_sec - t_start_total_sec)

    return t_end_total_sec - t_start_total_sec


def get_repeat_element_index_list(src_list, str_repeat):
    count = src_list.count(str_repeat)
    index_list = []
    index = -1

    for i in range(0, count):
        index = src_list.index(str_repeat, index + 1)
        index_list.append(index)

    print(index_list)


def generate_time_stamp():
    # tick_time = time.time()
    # loc_time = time.localtime()
    # asc_time = time.asctime()
    time_stamp = time.strftime("%Y%m%d_%H%M%S", time.localtime())

    return time_stamp


def generate_uuid1():
    return uuid.uuid1()


def combine_csv_log_files(
    csv_log_files_path, csv_log_files_list, csv_file_after_combined
):
    data = pd.DataFrame()
    for file_path in csv_log_files_list:
        df = pd.read_csv(file_path, encoding="utf-8-sig")
        data = pd.concat([data, df])

    # 重新设置索引 从0开始
    data.reset_index(drop=True, inplace=True)
    # 将合并的data存储
    data.to_csv(
        csv_log_files_path + csv_file_after_combined, index=False, encoding="utf-8-sig"
    )


# def get_csv_excel_file_encoding(file_path):
#     with open(file_path, "rb") as f:
#         result = chardet.detect(f.read())
#         encoding_method = result["encoding"]
#         print("[%s]encoding_method is %s" % (file_path, encoding_method))

#     return encoding_method


def pd_drop_duplicated_rows(csv_file_path):
    df = pd.read_csv(csv_file_path)
    df.drop_duplicates(keep="first", inplace=True)
    df.to_csv(csv_file_path, encoding="utf8", index=False)


# def pd_drop_duplicated_rows_with_same_column(csv_file_path, column1, column2):
#     df = pd.read_csv(csv_file_path)
#     new_df = df.drop_duplicates(subset=[column1:column2], keep='first', inplace=True)
#     new_df.to_csv(csv_file_path, encoding='utf-8')


def combine_utf8_csv_log_files(
    csv_log_files_path, csv_log_files_list, csv_file_after_combined
):
    data = pd.DataFrame()
    for csv_log_file in csv_log_files_list:
        df = pd.read_csv(csv_log_file, encoding="utf-8")
        data = pd.concat([data, df])

    # 重新设置索引 从0开始
    data.reset_index(drop=True, inplace=True)
    # 将合并的data存储
    data.to_csv(
        csv_log_files_path + csv_file_after_combined, index=False, encoding="utf-8"
    )


def combine_utf8_sig_csv_log_files(
    csv_log_files_path, csv_log_files_list, csv_file_after_combined
):
    data = pd.DataFrame()
    for csv_log_file in csv_log_files_list:
        df = pd.read_csv(csv_log_file, encoding="utf-8-sig")
        data = pd.concat([data, df])

    # 重新设置索引 从0开始
    data.reset_index(drop=True, inplace=True)
    # 将合并的data存储
    data.to_csv(
        csv_log_files_path + csv_file_after_combined, index=False, encoding="utf-8"
    )


def combine_gb2312_csv_log_files(
    csv_log_files_path, csv_log_files_list, csv_file_after_combined
):
    # with open(
    #     csv_log_files_path + csv_file_after_combined, 'w', encoding="utf-8"
    # ) as outfile:
    #     # 遍历每个CSV文件
    #     for i, file in enumerate(csv_log_files_list):
    #         # 使用 chunksize 逐块读取文件，避免内存不足
    #         for chunk in pd.read_csv(file, chunksize=100000, encoding="gb2312"):
    #             # 如果是第一个文件，写入列名，否则跳过列名
    #             if i == 0 and chunk.index.start == 0:
    #                 chunk.to_csv(outfile, index=False, mode='a', encoding="utf-8")
    #             else:
    #                 chunk.to_csv(
    #                     outfile, index=False, header=False, mode='a', encoding="utf-8"
    #                 )

    data = pd.DataFrame()
    for csv_log_file in csv_log_files_list:
        df = pd.read_csv(csv_log_file, encoding="gb2312")
        data = pd.concat([data, df])

    # 重新设置索引 从0开始
    data.reset_index(drop=True, inplace=True)
    # 将合并的data存储
    data.to_csv(
        csv_log_files_path + csv_file_after_combined, index=False, encoding="utf-8"
    )


def combine_utf8_csv_log_files(
    csv_log_files_path, csv_log_files_list, csv_file_after_combined
):
    data = pd.DataFrame()
    for csv_log_file in csv_log_files_list:
        df = pd.read_csv(csv_log_file, encoding="utf-8")
        data = pd.concat([data, df])

    # 重新设置索引 从0开始
    data.reset_index(drop=True, inplace=True)
    # 将合并的data存储
    data.to_csv(
        csv_log_files_path + csv_file_after_combined, index=False, encoding="utf-8"
    )
