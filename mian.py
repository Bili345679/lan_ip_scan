from multiping import MultiPing
import json
import re
import os

# 超时
timeout = 0
# 检测延迟
interval = 0
# 展示ping时长
show_ping_time = True
# 展示结果
#   all 全部
#   success 仅展示成功的
#   error 仅展示失败的
show_res_flag = "all"
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
                "ip_range": "192.168.1.*",
                "timeout": 1,
                "interval": 1,
                "show_ping_time": True,
                "show_res_flag": "all",
            },
            file,
        )


# 读取配置
def load_config():
    with open("./config.json", "r") as file:
        config = json.load(file)
    global timeout
    timeout = config["timeout"]
    interval = config["interval"]
    show_ping_time = config["show_ping_time"]
    show_res_flag = config["show_res_flag"]
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
    
    print(os.get_terminal_size())


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
    res_dict_unsorted = {}
    if show_res_flag == "all" or show_res_flag == "success":
        # 成功结果
        res_dict_unsorted.update(res[0])

    if show_res_flag == "all" or show_res_flag == "error":
        # 失败结果
        for each_error_ip in res[1]:
            res_dict_unsorted[each_error_ip] = -1

    # 排序
    ip_list = list(res[0].keys())
    ip_list = sorted(res_dict_unsorted, key=lambda x: (int(x.split('.')[0]), int(x.split('.')[1]), int(x.split('.')[2]), int(x.split('.')[3])))

    res_dict_sorted = {}
    for each_ip in ip_list:
        res_dict_sorted[each_ip] = res_dict_unsorted[each_ip]

    print(res_dict_sorted)


load_config()

mp = MultiPing(ip_list)
mp.send()
res = mp.receive(timeout)

show_res(res)
