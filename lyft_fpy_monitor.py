#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@File    :   lyft_fpy_monitor.py
@Time    :   2026/02/17 21:58:56
@Author  :   SimonYuan
@Version :   1.0
@Site    :   https://tresordie.github.io/
@Desc    :   None
"""

import sys
import os
from csv_operate import *
from datetime import datetime

from PyQt5.QtWidgets import QMainWindow, QApplication, QFileDialog, QMessageBox
from PyQt5.QtCore import QDate

# from PyQt5.QtWidgets import *
from Ui_fpy_monitor import Ui_MainWindow

# sftp server library
from sftp_transfer_paramiko import sftp_rsa_access
from collections import defaultdict

# aws server log folder
from aws_logs_path import aws_logs_folder_path


class MainForm(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super(MainForm, self).__init__()
        self.setupUi(self)
        self.setWindowTitle("Lyft FPY Monitor")

        # Project combo box
        self.comboBox.enabled = True
        self.comboBox.addItems(
            [
                "MonolithPCBA",
                "MonolithCassette",
                "MonolithReceiver",
                "MonolithBollard",
                "Astro931",
                "Astro932",
                "Astro933",
                "HCTPCBA",
                "HCTFATP",
                "Metro931",
                "Metro932",
                "Metro933",
            ]
        )

        # lineEdit显示选择的local文件路径，用于存储aws下载的路径文件
        self.lineEdit.setText("")

        # text browser content
        self.textBrowser_content = ""

        # push button
        self.pushButton.clicked.connect(self.fpy_data_fetch)

        # 连接信号（点击日期时触发）
        self.start_date = ""
        self.end_date = ""
        self.days_elapsed = 0
        self.calendarWidget.clicked.connect(self.calendarWidget1_on_date_selected)
        self.calendarWidget_2.clicked.connect(self.calendarWidget2_on_date_selected)

        # 良率计算的数据存储
        self.total_products = 0
        self.first_pass_count = 0
        self.final_fail_count = 0
        self.retest_count = 0

        self.fpy = 0.0
        self.failure_rate = 0.0
        self.retest_rate = 0.0

        # 指定的日期列表
        self.specific_string_list = []

        # scud
        # self.scud_sftp_rsa_access = sftp_rsa_access(
        #     "s-bd4d248215874269b.server.transfer.ap-southeast-1.amazonaws.com",
        #     22,
        #     "./id_scud",
        #     "batterycm2",
        # )

        # aws folder path
        self.aws_logs_folder_path = aws_logs_folder_path()
        # 连接AWS时会默认进入到一个路径，需要增加项目路径到达指定project folder path
        self.target_path = ""

        # location to store downloaded log files
        self.local_logs_folder_path = ""

        # 匹配到的文件加入此列表
        # csv log files list
        self.matched_csv_files_list = []
        self.matched_failure_csv_files_list = []

        # txt log files list
        self.matched_txt_files_list = []
        self.matched_failure_txt_files_list = []

    def clean_window(self):
        self.textBrowser_content = ""
        self.textBrowser.setText(self.textBrowser_content)
        self.textBrowser.moveCursor(self.textBrowser.textCursor().End)
        QApplication.processEvents()

    def set_textBrowser_content(self):
        self.textBrowser.setText(self.textBrowser_content)
        self.textBrowser.moveCursor(self.textBrowser.textCursor().End)
        QApplication.processEvents()

    def calendarWidget1_on_date_selected(self, date: QDate):
        # 获取年月日
        # year = date.year()
        # month = date.month()
        # day = date.day()

        # 输出日期
        # date_str = date.toString("yyyy-MM-dd")
        self.clean_window()

        date1_str = date.toString("yyyyMMdd")
        self.start_date = date1_str
        print("Calendar1选中的日期:", date1_str)
        self.textBrowser_content += "Calendar1选中的日期:" + date1_str + "\n"
        self.set_textBrowser_content()

    def calendarWidget2_on_date_selected(self, date: QDate):
        # 获取年月日
        # year = date.year()
        # month = date.month()
        # day = date.day()

        # 输出日期
        # date_str = date.toString("yyyy-MM-dd")
        date2_str = date.toString("yyyyMMdd")
        self.end_date = date2_str
        print("Calendar2选中的日期:", date2_str)
        self.textBrowser_content += "Calendar2选中的日期:" + date2_str + "\n"
        self.set_textBrowser_content()

        self.days_elapsed = self.days_between(self.start_date, self.end_date)
        self.specific_string_list = []

        for i in range(self.days_elapsed):
            self.specific_string_list.append(str(int(self.start_date) + i))

    def days_between(self, date1, date2, fmt="%Y%m%d"):
        d1 = datetime.strptime(date1, fmt)
        d2 = datetime.strptime(date2, fmt)
        print("total days:", abs((d2 - d1).days) + 1)
        self.textBrowser_content += "total days:" + str(abs((d2 - d1).days) + 1) + "\n"
        self.set_textBrowser_content()
        return abs((d2 - d1).days + 1)

    def find_specific_csv_files_list_from_aws_foxlink_via_calendar_selection(
        self, target_aws_folder_path: str, specific_string_list: list
    ):
        # 先找到csv logs的文件名进行统计
        self.matched_csv_files_list = []
        self.matched_failure_csv_files_list = []
        self.local_logs_folder_path = QFileDialog.getExistingDirectory(
            self,
            "Select Folder",
            "./",
        )

        # 如果选择了文件，更新标签显示文件路径
        if self.local_logs_folder_path:
            print("选择的本地log存储路径为:", self.local_logs_folder_path)
            self.lineEdit.setText(self.local_logs_folder_path)
            self.textBrowser_content += (
                "选择的本地log存储路径为:" + self.local_logs_folder_path + "\n"
            )
            self.set_textBrowser_content()

        # 创建一个 SFTP 对象来来设定初始参数
        # foxlink
        self.foxlink_sftp_rsa_access = sftp_rsa_access(
            "s-bd4d248215874269b.server.transfer.ap-southeast-1.amazonaws.com",
            22,
            "../aws_rsa_key/id_foxlink",
            "foxlink",
        )
        # 连接 SFTP 服务器，下载Foxlink相关文件
        self.foxlink_sftp_rsa_access.connect_sftpserver_with_private_key()

        # 进入到 SFTP 服务器的指定文件路径并确认
        """ 不能依赖于getcwd()以及chdir()函数
        如果 sftp.normalize('.') 返回了正确的路径，但紧接着调用 sftp.getcwd() 依然返回 None, 这通常是因为你使用的 Paramiko 版本 或 服务器 SFTP 服务端实现（如某些受限的 Docker 容器或老旧的 OpenSSH）不支持内部状态同步。
        实际上，在 paramiko 的开发实践中, getcwd() 并不是一个可靠的函数。它只是一个客户端本地的变量，并不代表服务器的真实状态。
        解决方案：摒弃 getcwd()，改用绝对路径变量
        为了确保程序 100% 稳定，我们应该手动维护一个路径变量，而不是依赖 sftp.getcwd()
        """
        current_abs_path = self.foxlink_sftp_rsa_access.sftpclient.normalize(".")
        print(f"当前AWS Server绝对路径是: {current_abs_path}")
        self.textBrowser_content += f"当前绝对路径是: {current_abs_path}" + "\n"
        self.set_textBrowser_content()
        self.foxlink_sftp_rsa_access.rlogger.logger.info(
            f"current_abs_path: {current_abs_path}"
        )

        self.target_path = ""
        self.target_path = f"{current_abs_path.rstrip('/')}{target_aws_folder_path}"

        print(f"target_aws_folder_path: {self.target_path}")
        self.textBrowser_content += f"target_aws_folder_path: {self.target_path}" + "\n"
        self.set_textBrowser_content()
        self.foxlink_sftp_rsa_access.rlogger.logger.info(
            f"target_aws_folder_path: {self.target_path}"
        )

        try:
            # 使用 listdir 而不是 listdir_attr, 从服务器读取文件列表（共约 10 万+ 项）
            # monolith
            all_filenames = self.foxlink_sftp_rsa_access.sftpserver_listdir(
                current_abs_path + "/" + target_aws_folder_path
            )

            total_count = len(all_filenames)
            print("Total number of files: %d" % total_count)
            self.textBrowser_content += "Total number of files: %d" % total_count + "\n"
            self.set_textBrowser_content()
            self.foxlink_sftp_rsa_access.rlogger.logger.info(
                "Total number of files: %d" % total_count
            )

            # 直接在内存中过滤文件名
            # scan all file name in aws csv logs folder
            for filename in all_filenames:
                # 包含指定日期在filename里面
                for specific_string_in_file_name in specific_string_list:
                    if self.comboBox.currentText() == "MonolithPCBA":
                        if (
                            specific_string_in_file_name in filename
                            and "monolith_main_bft" in filename
                        ):
                            self.matched_csv_files_list.append(filename)
                    elif self.comboBox.currentText() == "MonolithCassette":
                        if (
                            specific_string_in_file_name in filename
                            and "monolith_cassette_ft" in filename
                        ):
                            self.matched_csv_files_list.append(filename)
                    elif self.comboBox.currentText() == "MonolithReceiver":
                        if (
                            specific_string_in_file_name in filename
                            and "monolith_receiver_ft" in filename
                        ):
                            self.matched_csv_files_list.append(filename)
                    elif self.comboBox.currentText() == "MonolithBollard":
                        if (
                            specific_string_in_file_name in filename
                            and "monolith_bollard_ft" in filename
                        ):
                            self.matched_csv_files_list.append(filename)
                    elif self.comboBox.currentText() == "Astro931":
                        if specific_string_in_file_name in filename and (
                            "Astro_FATP_FLASH_931_NYC" in filename
                            or "Astro_FATP_FLASH_931" in filename
                        ):
                            self.matched_csv_files_list.append(filename)
                    elif self.comboBox.currentText() == "Astro932":
                        if (
                            specific_string_in_file_name in filename
                            and "Astro_FATP_SELF_DIAG_932" in filename
                        ):
                            self.matched_csv_files_list.append(filename)
                    elif self.comboBox.currentText() == "Astro933":
                        if specific_string_in_file_name in filename and (
                            "Astro_FATP_FT_933" in filename
                            or "Astro_FATP_FT_933_NYC" in filename
                        ):
                            self.matched_csv_files_list.append(filename)
                    else:
                        pass

            print(
                f"匹配完成。找到 {len(self.matched_csv_files_list)} 个符合要求的文件。"
            )
            self.textBrowser_content += (
                f"匹配完成。找到 {len(self.matched_csv_files_list)} 个符合要求的文件。"
                + "\n"
            )
            self.set_textBrowser_content()
            self.foxlink_sftp_rsa_access.rlogger.logger.info(
                f"匹配完成。找到 {len(self.matched_csv_files_list)} 个符合要求的文件。"
            )

            # 开始下载 csv logs
            if not os.path.exists(self.lineEdit.text()):
                os.makedirs(self.lineEdit.text())

            for filename in self.matched_csv_files_list:
                remote_file = os.path.join(self.target_path, filename)
                local_file = os.path.join(self.lineEdit.text(), filename)

                if "FAIL" in filename:
                    # 收集测试不良的csv log文件名，用于后续txt log下载
                    self.matched_failure_csv_files_list.append(filename)
                    print(f"正在下载测试不良的csv log文件: {filename} ...")
                    self.textBrowser_content += (
                        f"正在下载测试不良的csv log文件: {filename} ..." + "\n"
                    )
                    self.set_textBrowser_content()
                    self.foxlink_sftp_rsa_access.rlogger.logger.info(
                        f"正在下载测试不良的csv log文件: {filename} ..."
                    )
                    self.foxlink_sftp_rsa_access.sftpclient.get(remote_file, local_file)

            print(
                f"\n所有匹配csv log文件已下载至: {os.path.abspath(self.lineEdit.text())}"
            )
            self.textBrowser_content += (
                f"\n所有匹配csv log文件已下载至: {os.path.abspath(self.lineEdit.text())}"
                + "\n"
            )
            self.set_textBrowser_content()
            self.foxlink_sftp_rsa_access.rlogger.logger.info(
                f"\n所有匹配csv log文件已下载至: {os.path.abspath(self.lineEdit.text())}"
            )

        except Exception as e:
            print(f"发生错误: {e}")
            self.foxlink_sftp_rsa_access.rlogger.logger.info(f"发生错误: {e}")
            self.textBrowser_content += f"发生错误: {e}" + "\n"
            self.set_textBrowser_content()
        finally:
            self.foxlink_sftp_rsa_access.sftpclient.close()
            self.foxlink_sftp_rsa_access.transport.close()

    def find_specific_txt_files_list_from_aws_foxlink_via_calendar_selection(
        self, target_aws_folder_path: str
    ):
        # 如果选择了文件，更新标签显示文件路径
        if self.matched_failure_csv_files_list and self.local_logs_folder_path:
            # 创建一个 SFTP 对象来来设定初始参数
            # foxlink
            self.foxlink_sftp_rsa_access = sftp_rsa_access(
                "s-bd4d248215874269b.server.transfer.ap-southeast-1.amazonaws.com",
                22,
                "../aws_rsa_key/id_foxlink",
                "foxlink",
            )
            # 连接 SFTP 服务器，下载Foxlink相关文件
            self.foxlink_sftp_rsa_access.connect_sftpserver_with_private_key()

            # 进入到 SFTP 服务器的指定文件路径并确认
            """ 不能依赖于getcwd()以及chdir()函数
            如果 sftp.normalize('.') 返回了正确的路径，但紧接着调用 sftp.getcwd() 依然返回 None, 这通常是因为你使用的 Paramiko 版本 或 服务器 SFTP 服务端实现（如某些受限的 Docker 容器或老旧的 OpenSSH）不支持内部状态同步。
            实际上，在 paramiko 的开发实践中, getcwd() 并不是一个可靠的函数。它只是一个客户端本地的变量，并不代表服务器的真实状态。
            解决方案：摒弃 getcwd()，改用绝对路径变量
            为了确保程序 100% 稳定，我们应该手动维护一个路径变量，而不是依赖 sftp.getcwd()
            """
            current_abs_path = self.foxlink_sftp_rsa_access.sftpclient.normalize(".")
            print(f"当前AWS Server绝对路径是: {current_abs_path}")
            self.textBrowser_content += f"当前绝对路径是: {current_abs_path}" + "\n"
            self.set_textBrowser_content()
            self.foxlink_sftp_rsa_access.rlogger.logger.info(
                f"current_abs_path: {current_abs_path}"
            )

            self.target_path = ""
            self.target_path = f"{current_abs_path.rstrip('/')}{target_aws_folder_path}"

            print(f"target_aws_folder_path: {self.target_path}")
            self.textBrowser_content += (
                f"target_aws_folder_path: {self.target_path}" + "\n"
            )
            self.set_textBrowser_content()
            self.foxlink_sftp_rsa_access.rlogger.logger.info(
                f"target_aws_folder_path: {self.target_path}"
            )

            try:
                # 使用 listdir 而不是 listdir_attr, 从服务器读取文件列表（共约 10 万+ 项）
                # monolith
                all_filenames = self.foxlink_sftp_rsa_access.sftpserver_listdir(
                    current_abs_path + "/" + target_aws_folder_path
                )

                total_count = len(all_filenames)
                print("Total number of files: %d" % total_count)
                self.textBrowser_content += (
                    "Total number of files: %d" % total_count + "\n"
                )
                self.set_textBrowser_content()
                self.foxlink_sftp_rsa_access.rlogger.logger.info(
                    "Total number of files: %d" % total_count
                )

                # 找到不良SN，从AWS下载不良SN的txt log文件
                for filename in all_filenames:
                    for failure_csv_filename in self.matched_failure_csv_files_list:
                        failure_csv_filename_keywords_list = failure_csv_filename.split(
                            "_"
                        )
                        if failure_csv_filename_keywords_list[2] in filename:
                            self.matched_failure_txt_files_list.append(filename)

                print(
                    f"不良的文本文件测试记录匹配完成。找到 {len(self.matched_failure_txt_files_list)} 个符合要求的文件。"
                )
                self.textBrowser_content += (
                    f"不良的文本文件测试记录匹配完成。找到 {len(self.matched_failure_txt_files_list)} 个符合要求的文件。"
                    + "\n"
                )
                self.set_textBrowser_content()
                self.foxlink_sftp_rsa_access.rlogger.logger.info(
                    f"不良的文本文件测试记录匹配完成。找到 {len(self.matched_failure_txt_files_list)} 个符合要求的文件。"
                )

                # 开始下载 csv logs
                if not os.path.exists(self.lineEdit.text()):
                    os.makedirs(self.lineEdit.text())

                for filename in self.matched_failure_txt_files_list:
                    remote_file = os.path.join(self.target_path, filename)
                    local_file = os.path.join(self.lineEdit.text(), filename)

                    print(f"正在下载不良的文本文件测试记录: {filename} ...")
                    self.textBrowser_content += (
                        f"正在下载不良的文本文件测试记录: {filename} ..." + "\n"
                    )
                    self.set_textBrowser_content()
                    self.foxlink_sftp_rsa_access.rlogger.logger.info(
                        f"正在下载不良的文本文件测试记录: {filename} ..."
                    )
                    self.foxlink_sftp_rsa_access.sftpclient.get(remote_file, local_file)

                print(
                    f"\n不良的文本文件测试记录已下载至: {os.path.abspath(self.lineEdit.text())}"
                )
                self.textBrowser_content += (
                    f"\n不良的文本文件测试记录已下载至: {os.path.abspath(self.lineEdit.text())}"
                    + "\n"
                )
                self.set_textBrowser_content()
                self.foxlink_sftp_rsa_access.rlogger.logger.info(
                    f"\n不良的文本文件测试记录已下载至: {os.path.abspath(self.lineEdit.text())}"
                )

                self.matched_failure_txt_files_list = []

                # 统计Top5 failure
                # 创建一个字典来存储不良记录  FailureSymptom: [ filename1, filename2... ]
                failure_symptom_dict = defaultdict(list)
                for filename in self.matched_failure_csv_files_list:
                    failure_csv_filepath = (
                        os.path.abspath(self.lineEdit.text()) + "/" + filename
                    )
                    print(failure_csv_filepath)
                    # pass_fail_status中FAIL的row index
                    # pass_fail_status需要区分大小写
                    header_row = pd_read_csv_row(failure_csv_filepath, 0)
                    if "pass_fail_status" in header_row:
                        pass_fail_status_column = pd_read_csv_column_by_name_header_set(
                            failure_csv_filepath, "pass_fail_status"
                        )

                    else:
                        pass_fail_status_column = pd_read_csv_column_by_name_header_set(
                            failure_csv_filepath, "PASS_FAIL_STATUS"
                        )

                    # 通过FAIL的row index找到对应的test_name
                    if "FAIL" in pass_fail_status_column:
                        # 不良项对应的index
                        index_failure_item = pass_fail_status_column.index("FAIL")
                    else:
                        print(f"测试不良csv log文件{filename}没有FAIL记录")
                        self.textBrowser_content += (
                            f"测试不良csv log文件{filename}没有FAIL记录" + "\n"
                        )
                        self.set_textBrowser_content()
                        self.foxlink_sftp_rsa_access.rlogger.logger.info(
                            f"测试不良csv log文件{filename}没有FAIL记录"
                        )

                    if "test_name" in header_row:
                        failure_symptom = pd_read_csv_column_by_name_header_set(
                            failure_csv_filepath, "test_name"
                        )[index_failure_item]
                    else:
                        failure_symptom = pd_read_csv_column_by_name_header_set(
                            failure_csv_filepath, "TEST_NAME"
                        )[index_failure_item]
                    print(f"failure_symptom: {failure_symptom}")
                    failure_symptom_dict[failure_symptom].append(filename)

                sorted_failure_symptom_dict = sorted(
                    failure_symptom_dict.items(),
                    key=lambda item: len(item[1]),
                    reverse=True,
                )
                len_sorted_failure_symptom_dict = len(sorted_failure_symptom_dict)

                for i in range(len_sorted_failure_symptom_dict):
                    print(
                        f"Top {i + 1} 不良项: {sorted_failure_symptom_dict[i][0]}  出现次数: {len(sorted_failure_symptom_dict[i][1])}"
                    )
                    self.textBrowser_content += (
                        f"Top {i + 1} 不良项: {sorted_failure_symptom_dict[i][0]}  出现次数: {len(sorted_failure_symptom_dict[i][1])}"
                        + "\n"
                    )
                    self.set_textBrowser_content()
                    self.foxlink_sftp_rsa_access.rlogger.logger.info(
                        f"Top {i + 1} 不良项: {sorted_failure_symptom_dict[i][0]}  出现次数: {len(sorted_failure_symptom_dict[i][1])}"
                        + "\n"
                    )

            except Exception as e:
                print(f"不良的文本文件测试记录下载发生错误: {e}")
                self.foxlink_sftp_rsa_access.rlogger.logger.info(
                    f"不良的文本文件测试记录下载发生错误: {e}"
                )
                self.textBrowser_content += (
                    f"不良的文本文件测试记录下载发生错误: {e}" + "\n"
                )
                self.set_textBrowser_content()
            finally:
                self.foxlink_sftp_rsa_access.sftpclient.close()
                self.foxlink_sftp_rsa_access.transport.close()

    def calculate_metrics(self, file_name_list: list):
        # 用字典存储每个 SN 的所有测试结果： { sn: [ (time, result), ... ] }
        sn_history = defaultdict(list)

        for file_name in file_name_list:
            parts = file_name.split("_")
            timestamp = parts[0]
            result = parts[1]
            sn = parts[2]
            sn_history[sn].append((timestamp, result))

        self.total_products = len(sn_history)
        self.first_pass_count = 0
        self.final_fail_count = 0
        self.retest_count = 0
        self.fpy = 0
        self.failure_rate = 0
        self.retest_rate = 0

        for sn, records in sn_history.items():
            # 按时间排序，确保我们找到的是“第一次”和“最后一次”
            records.sort(key=lambda x: x[0])

            first_result = records[0][1]
            final_result = records[-1][1]

            # 统计一次良率：第一次就是 PASS
            if first_result == "PASS":
                self.first_pass_count += 1

            # 统计最终不良率：最后一次测完还是 FAIL
            if final_result == "FAIL":
                self.final_fail_count += 1

            # 统计重测率：只要测试记录多于 1 条就算重测
            if len(records) > 1:
                self.retest_count += 1

        # 计算百分比
        if self.total_products:
            self.fpy = (self.first_pass_count / self.total_products) * 100
            self.failure_rate = (self.final_fail_count / self.total_products) * 100
            self.retest_rate = (self.retest_count / self.total_products) * 100
        else:
            self.fpy = 0
            self.failure_rate = 0
            self.retest_rate = 0

        # 打印结果
        print(f"--- 统计报告 ---")  # noqa: F541
        print(f"投入总产品数 (Total SNs): {self.total_products}")
        print(f"一次通过数 (FPY Count): {self.first_pass_count}")
        print(f"最终失败数 (Final Fail): {self.final_fail_count}")
        print(f"重测产品数 (Retest Count): {self.retest_count}")
        print("-" * 20)
        print(f"一次良率 (FPY): {self.fpy:.2f}%")
        print(f"最终不良率 (Failure Rate): {self.failure_rate:.2f}%")
        print(f"重测率 (Retest Rate): {self.retest_rate:.2f}%")

        self.textBrowser_content += f"--- 统计报告 ---" + "\n"  # noqa: F541
        self.textBrowser_content += (
            f"投入总产品数 (Total SNs): {self.total_products}" + "\n"
        )
        self.textBrowser_content += (
            f"一次通过数 (FPY Count): {self.first_pass_count}" + "\n"
        )
        self.textBrowser_content += (
            f"最终失败数 (Final Fail): {self.final_fail_count}" + "\n"
        )
        self.textBrowser_content += (
            f"重测产品数 (Retest Count): {self.retest_count}" + "\n"
        )
        self.textBrowser_content += "-" * 20 + "\n"
        self.textBrowser_content += f"一次良率 (FPY): {self.fpy:.2f}%" + "\n"
        self.textBrowser_content += (
            f"最终不良率 (Failure Rate): {self.failure_rate:.2f}%" + "\n"
        )
        self.textBrowser_content += (
            f"重测率 (Retest Rate): {self.retest_rate:.2f}%" + "\n"
        )
        self.set_textBrowser_content()

        self.label_3.setText(f"{self.total_products}")
        self.label_5.setText(f"{self.fpy:.2f}%")
        self.label_6.setText(f"{self.retest_rate:.2f}%")
        self.label_8.setText(f"{self.failure_rate:.2f}%")

        self.label_32.setText(f"{self.first_pass_count}")
        self.label_29.setText(f"{self.retest_count}")
        self.label_30.setText(f"{self.final_fail_count}")

    def fpy_data_fetch(self):
        """_summary_
        specific_string_list: 用户选定的日期范围内的日期字符串列表
        """
        if self.comboBox.currentText() == "MonolithPCBA":
            self.find_specific_csv_files_list_from_aws_foxlink_via_calendar_selection(
                self.aws_logs_folder_path.monolith_csv_logs_aws_file_path,
                self.specific_string_list,
            )
            # print(f"MonolithPCBA matched files list: {self.matched_csv_files_list}")
            # self.textBrowser_content += (
            #     f"MonolithPCBA matched files list: {self.matched_csv_files_list}" + "\n"
            # )
            # self.set_textBrowser_content()
            self.calculate_metrics(self.matched_csv_files_list)
            self.find_specific_txt_files_list_from_aws_foxlink_via_calendar_selection(
                self.aws_logs_folder_path.monolith_txt_main_logs_aws_file_path,
            )
        elif self.comboBox.currentText() == "MonolithCassette":
            self.find_specific_csv_files_list_from_aws_foxlink_via_calendar_selection(
                self.aws_logs_folder_path.monolith_csv_logs_aws_file_path,
                self.specific_string_list,
            )
            self.calculate_metrics(self.matched_csv_files_list)
            self.find_specific_txt_files_list_from_aws_foxlink_via_calendar_selection(
                self.aws_logs_folder_path.monolith_txt_cassette_logs_aws_file_path,
            )
        elif self.comboBox.currentText() == "MonolithReceiver":
            self.find_specific_csv_files_list_from_aws_foxlink_via_calendar_selection(
                self.aws_logs_folder_path.monolith_csv_logs_aws_file_path,
                self.specific_string_list,
            )
            self.calculate_metrics(self.matched_csv_files_list)
            self.find_specific_txt_files_list_from_aws_foxlink_via_calendar_selection(
                self.aws_logs_folder_path.monolith_txt_receiver_logs_aws_file_path,
            )
        elif self.comboBox.currentText() == "MonolithBollard":
            self.find_specific_csv_files_list_from_aws_foxlink_via_calendar_selection(
                self.aws_logs_folder_path.monolith_csv_logs_aws_file_path,
                self.specific_string_list,
            )
            self.calculate_metrics(self.matched_csv_files_list)
            self.find_specific_txt_files_list_from_aws_foxlink_via_calendar_selection(
                self.aws_logs_folder_path.monolith_txt_bollard_logs_aws_file_path,
            )
        elif self.comboBox.currentText() == "Astro931":
            self.find_specific_csv_files_list_from_aws_foxlink_via_calendar_selection(
                self.aws_logs_folder_path.astro_fatp_csv_logs_aws_file_path,
                self.specific_string_list,
            )
            self.calculate_metrics(self.matched_csv_files_list)
            self.find_specific_txt_files_list_from_aws_foxlink_via_calendar_selection(
                self.aws_logs_folder_path.astro_fatp931_txt_logs_aws_file_path,
            )
        elif self.comboBox.currentText() == "Astro932":
            self.find_specific_csv_files_list_from_aws_foxlink_via_calendar_selection(
                self.aws_logs_folder_path.astro_fatp_csv_logs_aws_file_path,
                self.specific_string_list,
            )
            self.calculate_metrics(self.matched_csv_files_list)
            self.find_specific_txt_files_list_from_aws_foxlink_via_calendar_selection(
                self.aws_logs_folder_path.astro_fatp932_txt_logs_aws_file_path,
            )
        elif self.comboBox.currentText() == "Astro933":
            self.find_specific_csv_files_list_from_aws_foxlink_via_calendar_selection(
                self.aws_logs_folder_path.astro_fatp_csv_logs_aws_file_path,
                self.specific_string_list,
            )
            self.calculate_metrics(self.matched_csv_files_list)
            self.find_specific_txt_files_list_from_aws_foxlink_via_calendar_selection(
                self.aws_logs_folder_path.astro_fatp933_txt_logs_aws_file_path,
            )
        elif self.comboBox.currentText() == "Metro931":
            self.find_specific_csv_files_list_from_aws_foxlink_via_calendar_selection(
                self.aws_logs_folder_path.metro_fatp_csv_logs_aws_file_path,
                self.specific_string_list,
            )
            self.calculate_metrics(self.matched_csv_files_list)
            self.find_specific_txt_files_list_from_aws_foxlink_via_calendar_selection(
                self.aws_logs_folder_path.metro_fatp931_txt_logs_aws_file_path,
            )
        elif self.comboBox.currentText() == "Metro932":
            self.find_specific_csv_files_list_from_aws_foxlink_via_calendar_selection(
                self.aws_logs_folder_path.metro_fatp_csv_logs_aws_file_path,
                self.specific_string_list,
            )
            self.calculate_metrics(self.matched_csv_files_list)
            self.find_specific_txt_files_list_from_aws_foxlink_via_calendar_selection(
                self.aws_logs_folder_path.metro_fatp932_txt_logs_aws_file_path,
            )
        elif self.comboBox.currentText() == "Metro933":
            self.find_specific_csv_files_list_from_aws_foxlink_via_calendar_selection(
                self.aws_logs_folder_path.metro_fatp_csv_logs_aws_file_path,
                self.specific_string_list,
            )
            self.calculate_metrics(self.matched_csv_files_list)
            self.find_specific_txt_files_list_from_aws_foxlink_via_calendar_selection(
                self.aws_logs_folder_path.metro_fatp933_txt_logs_aws_file_path,
            )


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = MainForm()
    win.show()
    sys.exit(app.exec())
