from multiping import MultiPing
import json
import re
import os
from termcolor import colored
import time

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
# 是否缩短IP
shorten_ip = True
# 缩短IP长度
shorten_ip_len = 0
# 展示结果
#   all 全部
#   success 仅展示成功的
#   error 仅展示失败的
show_res_flag = "all"
# 循环模式
loop_mode = False
# 掉线检测
offline_check_times = 5
# 掉线次数转字符串最大长度
offline_check_times_max_len = 0
# 是否显示掉线次数
show_offline_check_times_flag = True
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
# 自最后一次在线，到现在为止的掉线次数
offline_times = {}


# 初始化设置
def init_config():
    with open("./config.json", "w+") as file:
        json.dump(
            {
                "ip_range": "192.168.0-1.*",  # IP范围 192: 这一位只扫描192;   0 - 1: 这一位扫描0与1;   *: 这意味扫描0到255
                "timeout": 1,  # PING超时时间，如果超过{interval}，判断为PING失败
                "interval": 1,  # 检测间隔，当{loop_mode}为True时，每间隔{interval}秒，检测一次
                "show_ping_time": True,  # 是否展示实际PING值
                "show_res_flag": "all",  # 显示哪些结果 "success": 仅显示成功结果;   "error": 仅显示失败结果;   "all": 显示成功与失败的结果
                "show_ping_time_len": 5,  # 显示ping值的字符串长度
                "shorten_ip": True,  # 是否缩短显示IP，例如：扫描192.168.0-1.*时，隐藏"192.168.",仅显示后两位
                "loop_mode": True,  # 循环模式
                "offline_check_times": -1,  # 掉线检测
                # 当{offline_check_times}为整数时，当最后一次检测成功某IP成功，到最后一次检测某IP失败，超过循环次数时，不显示该IP，否则一直显示该IP
                # 当{offline_check_times}为-1时，则一直显示检测到的IP，无论其是否掉线
                "show_offline_check_times_flag": True,  # 是否显示掉线次数
            },
            file,
        )


# 读取配置
def load_config():
    try:
        with open("./config.json", "r") as file:
            config = json.load(file)
    except Exception:
        init_config()
        load_config()
        return True

    global timeout
    global interval
    global show_ping_time
    global show_res_flag
    global show_ping_time_len
    global shorten_ip
    global loop_mode
    global offline_check_times
    global show_offline_check_times_flag

    timeout = config["timeout"]
    interval = config["interval"]
    show_ping_time = config["show_ping_time"]
    show_res_flag = config["show_res_flag"]
    show_ping_time_len = config["show_ping_time_len"]
    loop_mode = config["loop_mode"]
    shorten_ip = config["shorten_ip"]
    offline_check_times = config["offline_check_times"]
    show_offline_check_times_flag = config["show_offline_check_times_flag"]
    ip_range_list = config["ip_range"].split(".")

    index = 0
    for each in ip_range_list:
        set_ip_range(each, index)
        index += 1

    set_ip_list()


# 设置ip区域
def set_ip_range(ip_range_list_each, index):
    global shorten_ip_len
    start = 0
    end = 0
    if ip_range_list_each == "*":
        start = 0
        end = 255
    elif re.match(r"^\d{1,3}$", ip_range_list_each):
        # 所有目标IP的该位数字一样，可以隐藏
        if shorten_ip:
            shorten_ip_len += len(ip_range_list_each)
            if index < 3:
                shorten_ip_len += 1

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
                    offline_times[ip] = 0


# 掉线结果统计
def offline_res(res):
    global offline_check_times_max_len
    offline_check_times_max_len = 0
    for each in res[0]:
        # 在线
        offline_times[each] = 0
    for each in res[1]:
        # 掉线
        offline_times[each] += 1
        # 字符串长度
        if len(str(offline_times[each])) > offline_check_times_max_len:
            offline_check_times_max_len = len(str(offline_times[each]))


# 展示结果
def show_res(res):
    # IP字符串最大长度
    ip_max_len = 0
    # 时间字符串最大长度
    ping_time_max_len = 0 if not show_ping_time_len else show_ping_time_len
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

    # 打印
    # 终端字符长度
    terminal_width = os.get_terminal_size()[0]
    terminal_height = os.get_terminal_size()[1]

    print("".ljust(terminal_width, "#"))

    # 每条信息长度
    each_info_len = 0
    # 在线判断
    each_info_len += 2 + 1
    # ip地址
    each_info_len += (ip_max_len - shorten_ip_len) + 1
    # ping值
    each_info_len += ping_time_max_len + 1
    # 掉线次数
    if show_offline_check_times_flag:
        each_info_len += offline_check_times_max_len + 1
    # 分隔
    each_info_len += 1

    # 行信息条数
    line_info_count = 0
    for each_ip in res_dict_sorted:
        # 跳过超过掉线次数上限的结果
        if (
            show_offline_check_times_flag
            and offline_check_times != -1
            and offline_times[each_ip] > offline_check_times
        ):
            continue

        # 拼接信息
        each_info = ""

        # 在线判断
        each_info += (
            colored("√", "green")
            if res_dict_sorted[each_ip] != -1
            else colored("×", "red")
        ) + " "

        # ip地址
        each_info += each_ip.ljust(ip_max_len, " ")[shorten_ip_len:] + " "

        # ping值
        ping_value = res_dict_sorted[each_ip]
        if ping_value == -1:
            each_info += "".ljust(show_ping_time_len, "-")
        else:
            each_info += str(ping_value).ljust(ping_time_max_len, " ")[
                0:show_ping_time_len
            ]
        each_info += " "

        # 掉线次数
        if show_offline_check_times_flag:
            offline_times_value_string = str(offline_times[each_ip]).ljust(offline_check_times_max_len, " ")
            each_info += (
                colored(offline_times_value_string, "green")
                if offline_times[each_ip] == 0
                else colored(offline_times_value_string, "red")
            )

        # 分隔
        each_info += "|"

        # 信息条数+1
        line_info_count += 1
        # 剩下区域是否足够发这条信息
        if line_info_count * each_info_len > terminal_width:
            print()
            line_info_count = 1

        print(each_info, end="")
    print()
    print("".ljust(terminal_width, "#"))


load_config()

while True:
    mp = MultiPing(ip_list)
    mp.send()
    try:
        res = mp.receive(timeout)
    except:
        print("error")

    # 掉线结果
    offline_res(res)

    # 展示结果
    show_res(res)

    if not loop_mode:
        break
    else:
        time.sleep(interval)
