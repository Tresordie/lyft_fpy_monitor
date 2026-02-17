# -*- coding: utf-8 -*-
import os
import stat
import time

import paramiko

from logger import *  # noqa: F403


class sftp_rsa_access(object):
    def __init__(
        self,
        sftpserver_address: object,
        sftpserver_port: object,
        sftpclient_private_key_path: object,
        sftplogin_username: object,
        sftpclient_private_key_password: object = None,
        sftplogin_userpassword: object = None,
    ) -> None:
        """

        :rtype: None
        """
        self.sftpserver_address = sftpserver_address
        self.sftpserver_port = sftpserver_port

        self.sftpclient_private_key_path = sftpclient_private_key_path
        self.sftpclient_private_key_password = sftpclient_private_key_password

        self.sftplogin_username = sftplogin_username
        self.sftplogin_userpassword = sftplogin_userpassword

        self.sftpclient = ""

        self.private_key = paramiko.RSAKey.from_private_key_file(
            filename=self.sftpclient_private_key_path
        )

        self.transport = paramiko.Transport(
            (self.sftpserver_address, int(self.sftpserver_port))
        )

        self.rlogger_name = self.generate_time_stamp()
        self.rlogger = Logger(self.rlogger_name + "_sftp_transfer.log", level="info")

    def generate_time_stamp(self):
        time_stamp = time.strftime("%Y%m%d_%H%M%S", time.localtime())
        return time_stamp

    def connect_sftpserver_with_private_key(self):
        print(
            "\nConnecting to sftpserver: %s:%s"
            % (self.sftpserver_address, self.sftpserver_port)
        )

        self.rlogger.logger.info(
            "\nConnecting to sftpserver: %s:%s"
            % (self.sftpserver_address, self.sftpserver_port)
        )

        self.transport.connect(username=self.sftplogin_username, pkey=self.private_key)

        self.sftpclient = paramiko.SFTPClient.from_transport(self.transport)
        folder_list = self.sftpclient.listdir()

        if folder_list:
            print(
                "Successfully connected to sftpserver: %s:%s"
                % (self.sftpserver_address, self.sftpserver_port)
            )
            self.rlogger.logger.info(
                "Successfully connected to sftpserver: %s:%s"
                % (self.sftpserver_address, self.sftpserver_port)
            )

            print("current_path_folder_list:%s\n" % folder_list)
            self.rlogger.logger.info("current_path_folder_list:%s\n" % folder_list)

    def disconnect_sftpserver(self):
        self.transport.close()

    def sftpserver_listdir(self, target_directory):
        tmp_folder_list = self.sftpclient.listdir(target_directory)
        # print("directory_list [%s]: %s" % (target_directory, tmp_folder_list))
        return tmp_folder_list

    def sftpserver_listdir_attr(self, target_directory):
        tmp_folder_list = self.sftpclient.listdir_attr(target_directory)
        print("directory_listdir_attr [%s]: %s" % (target_directory, tmp_folder_list))
        self.rlogger.logger.info(
            "directory_listdir_attr [%s]: %s" % (target_directory, tmp_folder_list)
        )
        return tmp_folder_list

    def sftpserver_lstat(self, target_directory):
        """_summary_
            similar to linux command 'ls -l'
        Args:
            target_directory (_type_): _description_
            target directory we want to stat
        Returns:
            _type_: _description_
        """
        tmp_folder_lstat = self.sftpclient.lstat(target_directory)
        print("directory_lstat [%s]: %s" % (target_directory, tmp_folder_lstat))
        self.rlogger.logger.info(
            "directory_lstat [%s]: %s" % (target_directory, tmp_folder_lstat)
        )

        return tmp_folder_lstat

    def sftpserver_posix_rename(self, target_directory, oldpath, newpath):
        self.sftpserver_chdir(target_directory)
        self.sftpclient.posix_rename(oldpath=oldpath, newpath=newpath)
        print(
            "rename_directory_list [%s]: %s"
            % (target_directory, self.sftpserver_listdir("./"))
        )
        self.rlogger.logger.info(
            "rename_directory_list [%s]: %s"
            % (target_directory, self.sftpserver_listdir("./"))
        )

    def sftpserver_chdir(self, target_directory):
        if target_directory != self.sftpserver_getcwd():
            print(f"{target_directory} != {self.sftpserver_getcwd()}")
            self.sftpclient.chdir(target_directory)
        else:
            print("Already in target_directory path!\n")
            self.rlogger.logger.info("Already in target_directory path!\n")

        target_directory_folder_list = self.sftpclient.listdir()
        print("%s: %s:\n" % (target_directory, target_directory_folder_list))
        self.rlogger.logger.info(
            "%s: %s:\n" % (target_directory, target_directory_folder_list)
        )

        return target_directory_folder_list

    def sftpserver_file(self, target_directory, file_name, mode, bufsize):
        tmp_target_dir_file_list = self.sftpserver_chdir(target_directory)
        if file_name in tmp_target_dir_file_list:
            print(self.sftpclient.open(filename=file_name, mode=mode, bufsize=bufsize))

    def sftpserver_getcwd(self):
        tmp_current_dir_file_path = self.sftpclient.getcwd()
        print("current work directory: %s" % tmp_current_dir_file_path)
        self.rlogger.logger.info(
            "current work directory: %s" % tmp_current_dir_file_path
        )

        return tmp_current_dir_file_path

    def sftpserver_mkdir(self, target_directory, new_dir_name, permissions_mode):
        tmp_target_dir_file_list = self.sftpserver_chdir(target_directory)
        print("Creating directory %s" % new_dir_name)
        self.rlogger.logger.info("Creating directory %s" % new_dir_name)

        tmp_current_dir_file_list = self.sftpclient.listdir(target_directory)
        if new_dir_name in tmp_current_dir_file_list:
            print("new directory already exists!\n")
            self.rlogger.logger.info("new directory already exists!\n")
        else:
            self.sftpclient.mkdir(new_dir_name, permissions_mode)
            tmp_current_dir_file_list = self.sftpclient.listdir(target_directory)
            print("Current directory list: %s" % tmp_current_dir_file_list)
            self.rlogger.logger.info(
                "Current directory list: %s" % tmp_current_dir_file_list
            )
            if new_dir_name in tmp_current_dir_file_list:
                print("\nSuccessfully to create directory: %s\n" % new_dir_name)
                self.rlogger.logger.info(
                    "\nSuccessfully to create directory: %s\n" % new_dir_name
                )

    def sftpserver_posix_rename(self, target_directory, oldpath, newpath) -> None:
        self.sftpserver_chdir(target_directory)
        self.sftpclient.posix_rename(oldpath=oldpath, newpath=newpath)
        print(
            "rename_directory_list [%s]: %s"
            % (target_directory, self.sftpserver_listdir("./"))
        )
        self.rlogger.logger.info(
            "rename_directory_list [%s]: %s"
            % (target_directory, self.sftpserver_listdir("./"))
        )

    def sftpserver_filepath_ISDIR(self, remote_path):
        tmp_stat = self.sftpclient.stat(remote_path)
        # print('stat: %s' % tmp_stat)

        tmp_stat_stmode = tmp_stat.st_mode
        # print('st_mode: %s\n' % tmp_stat_stmode)

        if stat.S_ISDIR(tmp_stat_stmode):
            # print('%s is a directory!' % file_remote_path)
            return True
        else:
            # print('%s is not a directory!' % file_remote_path)
            return False

    def local_filepath_ISDIR(self, local_abs_path):
        tmp_stat_stmode = os.stat(local_abs_path).st_mode
        # print('st_mode: %s\n' % tmp_stat_stmode)

        if stat.S_ISDIR(tmp_stat_stmode):
            # print('%s is a directory!' % file_local_abs_path)
            return True
        else:
            # print('%s is not a directory!' % file_local_abs_path)
            return False

    def sftpserver_put_callback(self, completed_transfer_bytes, total_transfer_bytes):
        print(
            "transfer_bytes: %d/%d" % (completed_transfer_bytes, total_transfer_bytes)
        )
        self.rlogger.logger.info(
            "transfer_bytes: %d/%d" % (completed_transfer_bytes, total_transfer_bytes)
        )

        if completed_transfer_bytes != total_transfer_bytes:
            print("file transfer is going!\n")
            self.rlogger.logger.info("file transfer is going!\n")
        else:
            print("file transfer successfully!\n")
            self.rlogger.logger.info("file transfer successfully!\n")

    def sftpserver_put_singlefile(self, file_local_abs_path, remote_folder_path):
        tmp_local_path_file_name = file_local_abs_path
        tmp_local_path_file_name_split = tmp_local_path_file_name.split("/")
        file_name = tmp_local_path_file_name_split[
            len(tmp_local_path_file_name_split) - 1
        ]
        print("file transferring: %s" % file_local_abs_path)
        self.rlogger.logger.info("file transferring: %s" % file_local_abs_path)

        tmp_remote_path_dir_file_list = self.sftpserver_listdir(remote_folder_path)
        if file_name in tmp_remote_path_dir_file_list:
            print("%s already exists in %s!\n" % (file_name, remote_folder_path))
            self.rlogger.logger.info(
                "%s already exists in %s!\n" % (file_name, remote_folder_path)
            )

        else:
            self.sftpclient.put(
                localpath=file_local_abs_path,
                remotepath=(remote_folder_path + file_name),
                callback=self.sftpserver_put_callback,
                confirm=True,
            )

    def sftpserver_put_folder(self, local_folder_abs_path, remote_folder_path):
        tmp_path_file_list_for_logger = []
        tmp_local_path_file_list = os.listdir(local_folder_abs_path)

        self.rlogger.logger.info("local path file list:\n")
        tmp_path_file_list_for_logger = "\n".join(tmp_local_path_file_list)
        self.rlogger.logger.info("\n%s\n" % (tmp_path_file_list_for_logger))

        tmp_path_file_list_for_logger = []
        tmp_remote_path_file_list = self.sftpserver_listdir(remote_folder_path)

        self.rlogger.logger.info("remote path file list:\n")
        tmp_path_file_list_for_logger = "\n".join(tmp_remote_path_file_list)
        self.rlogger.logger.info("\n%s\n" % (tmp_path_file_list_for_logger))
        tmp_path_file_list_for_logger = []

        for file_name in tmp_local_path_file_list:
            # should be regular file name
            if file_name not in tmp_remote_path_file_list:
                self.sftpserver_put_singlefile(
                    local_folder_abs_path + file_name, remote_folder_path
                )
            else:
                print("%s already exists in remote path file list\n" % (file_name))
                self.rlogger.logger.info(
                    "%s already exists in remote path file list\n" % (file_name)
                )

    def sftpserver_put(self, local_abs_path, remote_path):
        if not self.sftpserver_filepath_ISDIR(remote_path=remote_path):
            print("Error: %s is not a directory!" % remote_path)
            self.rlogger.logger.info("Error: %s is not a directory!" % remote_path)
        else:
            if not self.local_filepath_ISDIR(local_abs_path=local_abs_path):
                self.sftpserver_put_singlefile(local_abs_path, remote_path)
            else:
                self.sftpserver_put_folder(local_abs_path, remote_path)

    def sftpserver_get_callback(self, completed_received_bytes, total_receive_bytes):
        print(
            "receiving_bytes: %d/%d" % (completed_received_bytes, total_receive_bytes)
        )
        self.rlogger.logger.info(
            "receiving_bytes: %d/%d" % (completed_received_bytes, total_receive_bytes)
        )

        if completed_received_bytes != total_receive_bytes:
            print("file receive is going!\n")
            self.rlogger.logger.info("file receive is going!\n")
        else:
            print("file receive successfully!\n")
            self.rlogger.logger.info("file receive successfully!\n")

    def sftpserver_get_singlefile(self, file_remote_path, local_folder_abs_path):
        tmp_remote_path_file_name = file_remote_path
        tmp_remote_path_file_name_split = tmp_remote_path_file_name.split("/")
        file_name = tmp_remote_path_file_name_split[
            len(tmp_remote_path_file_name_split) - 1
        ]
        print("file receiving: %s" % file_remote_path)
        self.rlogger.logger.info("file receiving: %s" % (file_remote_path))

        tmp_remote_path_dir_file_list = os.listdir(local_folder_abs_path)
        if file_name in tmp_remote_path_dir_file_list:
            print("%s already exists in %s!\n" % (file_name, local_folder_abs_path))
            self.rlogger.logger.info(
                "%s already exists in %s!\n" % (file_name, local_folder_abs_path)
            )
        else:
            self.sftpclient.get(
                remotepath=file_remote_path,
                localpath=local_folder_abs_path + file_name,
                callback=self.sftpserver_get_callback,
            )

    def sftpserver_get_folder(self, remote_folder_path, local_folder_abs_path):
        tmp_path_file_list_for_logger = []
        tmp_local_path_file_list = os.listdir(local_folder_abs_path)

        self.rlogger.logger.info("local path file list:\n")
        tmp_path_file_list_for_logger = "\n".join(tmp_local_path_file_list)
        self.rlogger.logger.info("\n%s\n" % (tmp_path_file_list_for_logger))

        tmp_path_file_list_for_logger = []
        tmp_remote_path_file_list = self.sftpserver_listdir(remote_folder_path)

        self.rlogger.logger.info("remote path file list:\n")
        tmp_path_file_list_for_logger = "\n".join(tmp_remote_path_file_list)
        self.rlogger.logger.info("\n%s\n" % tmp_path_file_list_for_logger)
        tmp_path_file_list_for_logger = []

        for file_name in tmp_remote_path_file_list:
            # should be regular file name
            if file_name not in tmp_local_path_file_list:
                self.sftpserver_get_singlefile(
                    remote_folder_path + file_name, local_folder_abs_path
                )
            else:
                print("%s already exists in local path file list\n" % file_name)
                self.rlogger.logger.info(
                    "%s already exists in local path file list\n" % file_name
                )

    def sftpserver_get(self, remote_path, local_abs_path):
        if not self.local_filepath_ISDIR(local_abs_path):
            print("Error: %s is not a directory!" % local_abs_path)
            self.rlogger.logger.info("Error: %s is not a directory!" % local_abs_path)
        else:
            if not self.sftpserver_filepath_ISDIR(remote_path):
                self.sftpserver_get_singlefile(remote_path, local_abs_path)
            else:
                self.sftpserver_get_folder(remote_path, local_abs_path)


# monolith csv logs
monolith_csv_logs_aws_file_path = "/Monolith /PVT/MES-Data-v0.1/Parametric-v0.2/Upload/"

# monolith txt logs
monolith_txt_main_logs_aws_file_path = "/Monolith /PVT/txt-files/monolith-main-bft/"
monolith_txt_cassette_logs_aws_file_path = (
    "/Monolith /PVT/txt-files/monolith-cassette-ft/"
)
monolith_txt_receiver_logs_aws_file_path = (
    "/Monolith /PVT/txt-files/monolith-receiver-ft/"
)
monolith_txt_bollard_logs_aws_file_path = (
    "/Monolith /PVT/txt-files/monolith-bollard-ft/"
)

# cosmo txt logs
astro_fatp_csv_logs_aws_file_path = "/Astro/Parametric-v0.1/Upload/"
astro_fatp931_txt_logs_aws_file_path = (
    "/Astro/Logs/vcu_fwre-flash-931/vcu_fwre-flash-931/"
)
astro_fatp932_txt_logs_aws_file_path = (
    "/Astro/Logs/selfdiagonstic-932/selfdiagonstic-932/"
)
astro_fatp933_txt_logs_aws_file_path = "/Astro/Logs/fatp-ft-933/fatp-ft-933/"
astro_fatp934_txt_logs_aws_file_path = "/Astro/Logs/test-ride-934/test-ride-934/"
astro_fatp935_txt_logs_aws_file_path = (
    "/AAstro/Logs/fatp-provision-935/fatp-provision-935/"
)

# scud_maple_csv_logs_aws_file_path = "/Maple/MES-Data-v0.1/Parametric-v0.1/Upload/MP/"
simon_destination_folder_path = "/Users/yuanyong/Desktop/astro_dock_charge/"
specific_string_in_file_name = ["FV2532CSBK5030045", "FV2532CSBK5030066"]


if __name__ == "__main__":
    # 创建一个 SFTP 对象来来设定初始参数
    # foxlink
    sftp_rsa_access = sftp_rsa_access(
        "s-bd4d248215874269b.server.transfer.ap-southeast-1.amazonaws.com",
        22,
        "./id_foxlink",
        "foxlink",
    )

    # sftp_rsa_access = sftp_rsa_access(
    #     '192.168.123.144',
    #     2022,
    #     './id_rsa',
    #     'test',
    # )

    # scud
    # sftp_rsa_access = sftp_rsa_access(
    #     "s-bd4d248215874269b.server.transfer.ap-southeast-1.amazonaws.com",
    #     22,
    #     "./id_scud",
    #     "batterycm2",
    # )

    # 连接 SFTP 服务器
    sftp_rsa_access.connect_sftpserver_with_private_key()

    # 进入到 SFTP 服务器的指定文件路径并确认
    """ 不能依赖于getcwd()以及chdir()函数
    如果 sftp.normalize('.') 返回了正确的路径，但紧接着调用 sftp.getcwd() 依然返回 None, 这通常是因为你使用的 Paramiko 版本 或 服务器 SFTP 服务端实现（如某些受限的 Docker 容器或老旧的 OpenSSH）不支持内部状态同步。
    实际上，在 paramiko 的开发实践中, getcwd() 并不是一个可靠的函数。它只是一个客户端本地的变量，并不代表服务器的真实状态。
    解决方案：摒弃 getcwd()，改用绝对路径变量
    为了确保程序 100% 稳定，我们应该手动维护一个路径变量，而不是依赖 sftp.getcwd()
    """
    # sftp_rsa_access.sftpserver_chdir(".")
    current_abs_path = sftp_rsa_access.sftpclient.normalize(".")
    print(f"当前绝对路径是: {current_abs_path}")
    sftp_rsa_access.rlogger.logger.info(f"current_abs_path: {current_abs_path}")

    # astro
    target_path = (
        f"{current_abs_path.rstrip('/')}{astro_fatp932_txt_logs_aws_file_path}"
    )

    # maple
    # target_path = f"{current_abs_path.rstrip('/')}{scud_maple_csv_logs_aws_file_path}"

    print(f"target_path: {target_path}")
    sftp_rsa_access.rlogger.logger.info(f"target_path: {target_path}")

    try:
        # 使用 listdir 而不是 listdir_attr, 从服务器读取文件列表（共约 10 万+ 项）
        # monolith
        all_filenames = sftp_rsa_access.sftpserver_listdir(
            current_abs_path + "/" + astro_fatp932_txt_logs_aws_file_path
        )

        # maple
        # all_filenames = sftp_rsa_access.sftpserver_listdir(
        #     current_abs_path + "/" + scud_maple_csv_logs_aws_file_path
        # )

        total_count = len(all_filenames)
        print("Total number of files: %d" % total_count)
        sftp_rsa_access.rlogger.logger.info("Total number of files: %d" % total_count)

        # 匹配含有指定字符串的文件名
        matched_files = []

        # 直接在内存中过滤文件名
        for filename in all_filenames:
            if (
                specific_string_in_file_name[1] in filename
                # or specific_string_in_file_name[1] in filename
            ):
                matched_files.append(filename)

        print(f"匹配完成。找到 {len(matched_files)} 个符合要求的文件。")
        sftp_rsa_access.rlogger.logger.info(
            f"匹配完成。找到 {len(matched_files)} 个符合要求的文件。"
        )

        # 开始下载
        if not os.path.exists(simon_destination_folder_path):
            os.makedirs(simon_destination_folder_path)

        for filename in matched_files:
            remote_file = os.path.join(target_path, filename)
            local_file = os.path.join(simon_destination_folder_path, filename)

            print(f"正在下载: {filename} ...")
            sftp_rsa_access.rlogger.logger.info(f"正在下载: {filename} ...")
            sftp_rsa_access.sftpclient.get(remote_file, local_file)

        print(
            f"\n所有匹配文件已下载至: {os.path.abspath(simon_destination_folder_path)}"
        )
        sftp_rsa_access.rlogger.logger.info(
            f"\n所有匹配文件已下载至: {os.path.abspath(simon_destination_folder_path)}"
        )

    except Exception as e:
        print(f"发生错误: {e}")
        sftp_rsa_access.rlogger.logger.info(f"发生错误: {e}")
    finally:
        sftp_rsa_access.sftpclient.close()
        sftp_rsa_access.transport.close()

    # sftp_rsa_access.sftpserver_put(r'F:/vmshare/sftp_trans/local_test/', '/test2/')

    # sftp_rsa_access.disconnect_sftpserver()

    # sftp_rsa_access.disconnect_sftpserver()
