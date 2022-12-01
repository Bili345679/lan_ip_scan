'''
遇到问题没人解答？小编创建了一个Python学习交流QQ群：857662006 
寻找有志同道合的小伙伴，互帮互助,群里还有不错的视频学习教程和PDF电子书！
'''
import re
def main():
    tel = input("请输入手机号:")
    # ret = re.match(r"1[35678]\d{9}", tel)
    # 由于手机号位数大于11位也能匹配成功，所以修改如下：
    ret = re.match(r"^1[35678]\d{9}$", tel)
    if ret:
        print("匹配成功")
    else:
        print("匹配失败")
if __name__ == "__main__":
    main()
