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

# -*- coding: utf-8 -*-

import sys
import os
from datetime import datetime

from PyQt5.QtWidgets import QMainWindow, QApplication, QFileDialog, QMessageBox
from PyQt5.QtCore import QDate

# from PyQt5.QtWidgets import *
from Ui_fpy_monitor import Ui_MainWindow

# sftp server library
from sftp_transfer_paramiko import sftp_rsa_access

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

        # push button
        self.pushButton.clicked.connect(self.fpy_data_fetch)
        self.pushButton_2.clicked.connect(self.aws_logs_fetch)

        # 连接信号（点击日期时触发）
        self.start_date = ""
        self.end_date = ""
        self.days_elapsed = 0
        self.calendarWidget.clicked.connect(self.calendarWidget1_on_date_selected)
        self.calendarWidget_2.clicked.connect(self.calendarWidget2_on_date_selected)

        # 指定的日期列表
        self.specific_string_list = []

        # 创建一个 SFTP 对象来来设定初始参数
        # foxlink
        self.foxlink_sftp_rsa_access = sftp_rsa_access(
            "s-bd4d248215874269b.server.transfer.ap-southeast-1.amazonaws.com",
            22,
            "./id_foxlink",
            "foxlink",
        )

        # scud
        self.scud_sftp_rsa_access = sftp_rsa_access(
            "s-bd4d248215874269b.server.transfer.ap-southeast-1.amazonaws.com",
            22,
            "./id_scud",
            "batterycm2",
        )

        # aws folder path
        self.aws_logs_folder_path = aws_logs_folder_path()

        # 匹配到的文件加入此列表
        self.matched_files_list = []

    def calendarWidget1_on_date_selected(self, date: QDate):
        # 获取年月日
        # year = date.year()
        # month = date.month()
        # day = date.day()

        # 输出日期
        # date_str = date.toString("yyyy-MM-dd")
        date1_str = date.toString("yyyyMMdd")
        self.start_date = date1_str
        print("Calendar1选中的日期:", date1_str)

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
        self.days_elapsed = self.days_between(self.start_date, self.end_date)

    def days_between(self, date1, date2, fmt="%Y%m%d"):
        d1 = datetime.strptime(date1, fmt)
        d2 = datetime.strptime(date2, fmt)
        print("total days:", abs((d2 - d1).days) + 1)
        return abs((d2 - d1).days + 1)

    def find_specific_files_list_from_aws_foxlink_via_calendar_selection(
        self, target_aws_folder_path: str, specific_string_list: list
    ):
        self.matched_files_list = []

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
        print(f"当前绝对路径是: {current_abs_path}")
        self.foxlink_sftp_rsa_access.rlogger.logger.info(
            f"current_abs_path: {current_abs_path}"
        )

        # astro
        target_path = f"{current_abs_path.rstrip('/')}{target_aws_folder_path}"

        # maple
        # target_path = f"{current_abs_path.rstrip('/')}{scud_maple_csv_logs_aws_file_path}"

        print(f"target_path: {target_path}")
        sftp_rsa_access.rlogger.logger.info(f"target_path: {target_path}")

        try:
            # 使用 listdir 而不是 listdir_attr, 从服务器读取文件列表（共约 10 万+ 项）
            # monolith
            all_filenames = sftp_rsa_access.sftpserver_listdir(
                current_abs_path + "/" + target_aws_folder_path
            )

            # maple
            # all_filenames = sftp_rsa_access.sftpserver_listdir(
            #     current_abs_path + "/" + scud_maple_csv_logs_aws_file_path
            # )

            total_count = len(all_filenames)
            print("Total number of files: %d" % total_count)
            sftp_rsa_access.rlogger.logger.info(
                "Total number of files: %d" % total_count
            )

            # 直接在内存中过滤文件名
            for filename in all_filenames:
                for specific_string_in_file_name in specific_string_list:
                    if specific_string_in_file_name in filename:
                        self.matched_files_list.append(filename)

            print(f"匹配完成。找到 {len(self.matched_files_list)} 个符合要求的文件。")
            sftp_rsa_access.rlogger.logger.info(
                f"匹配完成。找到 {len(self.matched_files_list)} 个符合要求的文件。"
            )

        except Exception as e:
            print(f"发生错误: {e}")
            sftp_rsa_access.rlogger.logger.info(f"发生错误: {e}")
        finally:
            sftp_rsa_access.sftpclient.close()
            sftp_rsa_access.transport.close()

    def fpy_data_fetch(self):
        # todo1: 选择日期范围所有文件的文件名添加进list
        # todo2: 每个文件名中提取出SN及pass fail状态，并添加进list
        # todo3: 统计不重复SN的个数
        pass

    def get_specific_files_from_aws_foxlink(
        self, target_aws_folder_path: str, specific_string_list: list
    ):
        self.matched_files_list = []

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
        print(f"当前绝对路径是: {current_abs_path}")
        self.foxlink_sftp_rsa_access.rlogger.logger.info(
            f"current_abs_path: {current_abs_path}"
        )

        # astro
        target_path = f"{current_abs_path.rstrip('/')}{target_aws_folder_path}"

        # maple
        # target_path = f"{current_abs_path.rstrip('/')}{scud_maple_csv_logs_aws_file_path}"

        print(f"target_path: {target_path}")
        sftp_rsa_access.rlogger.logger.info(f"target_path: {target_path}")

        try:
            # 使用 listdir 而不是 listdir_attr, 从服务器读取文件列表（共约 10 万+ 项）
            # monolith
            all_filenames = sftp_rsa_access.sftpserver_listdir(
                current_abs_path + "/" + target_aws_folder_path
            )

            # maple
            # all_filenames = sftp_rsa_access.sftpserver_listdir(
            #     current_abs_path + "/" + scud_maple_csv_logs_aws_file_path
            # )

            total_count = len(all_filenames)
            print("Total number of files: %d" % total_count)
            sftp_rsa_access.rlogger.logger.info(
                "Total number of files: %d" % total_count
            )

            # 直接在内存中过滤文件名
            for filename in all_filenames:
                for specific_string_in_file_name in specific_string_list:
                    if specific_string_in_file_name in filename:
                        self.matched_files_list.append(filename)

            print(f"匹配完成。找到 {len(self.matched_files_list)} 个符合要求的文件。")
            sftp_rsa_access.rlogger.logger.info(
                f"匹配完成。找到 {len(self.matched_files_list)} 个符合要求的文件。"
            )

            # 开始下载
            if not os.path.exists(self.lineEdit.text()):
                os.makedirs(self.lineEdit.text())

            for filename in self.matched_files_list:
                remote_file = os.path.join(target_path, filename)
                local_file = os.path.join(self.lineEdit.text(), filename)

                print(f"正在下载: {filename} ...")
                sftp_rsa_access.rlogger.logger.info(f"正在下载: {filename} ...")
                sftp_rsa_access.sftpclient.get(remote_file, local_file)

            print(f"\n所有匹配文件已下载至: {os.path.abspath(self.lineEdit.text())}")
            sftp_rsa_access.rlogger.logger.info(
                f"\n所有匹配文件已下载至: {os.path.abspath(self.lineEdit.text())}"
            )

        except Exception as e:
            print(f"发生错误: {e}")
            sftp_rsa_access.rlogger.logger.info(f"发生错误: {e}")
        finally:
            sftp_rsa_access.sftpclient.close()
            sftp_rsa_access.transport.close()

    def aws_logs_fetch(self):
        # todo1: 弹窗提示选择目标下载路径
        # todo2: 更新本地目标下载路径
        # todo3: 进行文件下载
        self.get_specific_files_from_aws_foxlink()

        pass


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = MainForm()
    win.show()
    sys.exit(app.exec())
