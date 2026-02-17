# !usr/bin/env python
# -*- coding:utf-8 -*-

"""
Description  :
Version      : 1.0
Author       : simon.yuan
Date         : 2026-02-17 22:53:49
LastEditors  : simon.yuan
LastEditTime : 2026-02-18 00:20:51
FilePath     : \\lyft_fpy_monitor\\aws_logs_path.py
"""


class aws_logs_folder_path(object):
    def __init__(
        self,
    ) -> None:
        """
        monolith AWS logs path
        """
        # monolith csv logs
        self.monolith_csv_logs_aws_file_path = (
            "/Monolith /PVT/MES-Data-v0.1/Parametric-v0.2/Upload/"
        )

        # monolith txt logs
        # pcba
        self.monolith_txt_main_logs_aws_file_path = (
            "/Monolith /PVT/txt-files/monolith-main-bft/"
        )

        # cassette
        self.monolith_txt_cassette_logs_aws_file_path = (
            "/Monolith /PVT/txt-files/monolith-cassette-ft/"
        )

        # receiver
        self.monolith_txt_receiver_logs_aws_file_path = (
            "/Monolith /PVT/txt-files/monolith-receiver-ft/"
        )

        # bollard
        self.monolith_txt_bollard_logs_aws_file_path = (
            "/Monolith /PVT/txt-files/monolith-bollard-ft/"
        )

        """
        astro bike AWS logs path
        """
        # astro csv logs
        self.astro_fatp_csv_logs_aws_file_path = "/Astro/Parametric-v0.1/Upload/"

        # astro 931 txt logs
        self.astro_fatp931_txt_logs_aws_file_path = (
            "/Astro/Logs/vcu_fwre-flash-931/vcu_fwre-flash-931/"
        )

        # astro 932 txt logs
        self.astro_fatp932_txt_logs_aws_file_path = (
            "/Astro/Logs/selfdiagonstic-932/selfdiagonstic-932/"
        )

        # astro 933 txt logs
        self.astro_fatp933_txt_logs_aws_file_path = (
            "/Astro/Logs/fatp-ft-933/fatp-ft-933/"
        )

        # astro 934 txt logs
        self.astro_fatp934_txt_logs_aws_file_path = (
            "/Astro/Logs/test-ride-934/test-ride-934/"
        )

        # astro 935 txt logs
        self.astro_fatp935_txt_logs_aws_file_path = (
            "/Astro/Logs/fatp-provision-935/fatp-provision-935/"
        )

        """
        maple BMS AWS logs path
        """
        # maple csv logs
        self.scud_maple_csv_logs_aws_file_path = (
            "/Maple/MES-Data-v0.1/Parametric-v0.1/Upload/MP/"
        )

        """
        simon local storage path
        """
        self.simon_destination_folder_path = (
            "/Users/yuanyong/Desktop/astro_dock_charge/"
        )
