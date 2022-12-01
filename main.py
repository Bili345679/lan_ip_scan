from multiping import MultiPing
import json
import re
import os
from termcolor import colored

# 彩色输出
os.system("color")

# 超时
timeout = 0
# 检测延迟
interval = 0
# 展示ping时长
show_ping_time = True
# 展示ping时长长度
show_ping_time_len = False
# 展示结果
#   all 全部
#   success 仅展示成功的
#   error 仅展示失败的
show_res_flag = "all"
# 循环模式
loop_mode = False
# ip范围
ip_range = [
    0,
    0,
    0,
    0,
    0,
    0,
    0,
    0,
]
# ip列表
ip_list = []

# 初始化设置
def init_config():
    with open("./config.json", "w+") as file:
        json.dump(
            {
                "ip_range": "192.168.0-1.*",
                "timeout": 1,
                "interval": 1,
                "show_ping_time": True,
                "show_res_flag": "success",
                "show_ping_time_len": False,
                "loop_mode": False,
            },
            file,
        )


# 读取配置
def load_config():
    with open("./config.json", "r") as file:
        config = json.load(file)
    
    global timeout
    global interval
    global show_ping_time
    global show_res_flag
    global show_ping_time_len
    global loop_mode

    timeout = config["timeout"]
    interval = config["interval"]
    show_ping_time = config["show_ping_time"]
    show_res_flag = config["show_res_flag"]
    show_ping_time_len = config["show_ping_time_len"]
    loop_mode = config["loop_mode"]
    ip_range_list = config["ip_range"].split(".")
    index = 0
    for each in ip_range_list:
        set_ip_range(each, index)
        index += 1
    set_ip_list()


# 设置ip区域
def set_ip_range(ip_range_list_each, index):
    start = 0
    end = 0
    if ip_range_list_each == "*":
        start = 0
        end = 255
    elif re.match(r"^\d{1,3}$", ip_range_list_each):
        start = int(ip_range_list_each)
        end = int(ip_range_list_each)
    elif re.match(r"^\d{1,3}-\d{1,3}$", ip_range_list_each):
        start = int(ip_range_list_each.split("-")[0])
        end = int(ip_range_list_each.split("-")[1])
    else:
        return False

    ip_range[index * 2] = start
    ip_range[index * 2 + 1] = end


# 设置ip列表
def set_ip_list():
    for num_1 in range(ip_range[1] - ip_range[0] + 1):
        for num_2 in range(ip_range[3] - ip_range[2] + 1):
            for num_3 in range(ip_range[5] - ip_range[4] + 1):
                for num_4 in range(ip_range[7] - ip_range[6] + 1):
                    ip = (
                        str(num_1 + ip_range[0])
                        + "."
                        + str(num_2 + ip_range[2])
                        + "."
                        + str(num_3 + ip_range[4])
                        + "."
                        + str(num_4 + ip_range[6])
                    )
                    ip_list.append(ip)


# 展示结果
def show_res(res):
    # IP字符串最大长度
    ip_max_len = 0
    # 时间字符串最大长度
    ping_time_max_len = 0
    # 每条信息长度
    each_info_len = 0

    # 未排序结果
    res_dict_unsorted = {}
    # 排序后的结果
    res_dict_sorted = {}

    if show_res_flag == "all" or show_res_flag == "success":
        # 成功结果
        res_dict_unsorted.update(res[0])
    if show_res_flag == "all" or show_res_flag == "error":
        # 失败结果
        for each_error_ip in res[1]:
            res_dict_unsorted[each_error_ip] = -1

    # 排序
    ip_list = list(res[0].keys())
    ip_list = sorted(
        res_dict_unsorted,
        key=lambda x: (
            int(x.split(".")[0]),
            int(x.split(".")[1]),
            int(x.split(".")[2]),
            int(x.split(".")[3]),
        ),
    )

    for each_ip in ip_list:
        res_dict_sorted[each_ip] = res_dict_unsorted[each_ip]
        if len(each_ip) > ip_max_len:
            ip_max_len = len(each_ip)

        if (
            not show_ping_time_len
            and len(str(res_dict_sorted[each_ip])) > ping_time_max_len
        ):
            ping_time_max_len = len(str(res_dict_sorted[each_ip]))

    # 终端字符长度
    terminal_width = os.get_terminal_size()[0]
    terminal_height = os.get_terminal_size()[1]
    # 每条信息长度
    # (√/×) ip_max_len ping_time_max_len
    each_info_len = 2 + 1 + ip_max_len + 1 + ping_time_max_len + 1
    
    # 行信息条数
    line_info_count = 0
    for each_ip in res_dict_sorted:
        # 拼接信息
        each_info = ""
        each_info += (colored("√", "green") if res_dict_sorted[each_ip] != -1 else colored("×", "red")) + " "
        each_info += each_ip.ljust(ip_max_len, " ") + " "
        each_info += str(res_dict_sorted[each_ip]).ljust(ping_time_max_len, " ") + "|"

        # 信息条数+1
        line_info_count += 1
        # 剩下区域是否足够发这条信息
        if line_info_count * each_info_len > terminal_width:
            print()
            line_info_count = 1

        print(each_info, end="")


load_config()

mp = MultiPing(ip_list)
mp.send()
res = mp.receive(timeout)

show_res(res)
