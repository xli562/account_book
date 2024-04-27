# 参考来自https://blog.csdn.net/liuaoxiang/article/details/126416405

import datetime
import xlrd
from appium import webdriver
from time import sleep
from appium.webdriver.common.touch_action import TouchAction
from xlrd import xldate_as_datetime

desired_caps={
                "platformName":"Android",   #平台名字
                "platformVersion":"7.1.2",   #设备版本号 ： adb shell getprop ro.build.version.release
                "deviceName":"127.0.0.1:62025", #设备名 ： adb devices
                "appPackage":"com.shark.jizhang", # app包名
                "appActivity":"com.shark.jizhang.module.main.MainActivity",  # 主启动页
                "udid":"127.0.0.1:62025",   # 设备编号
                "unicodeKeyboard":True,    # 支持中文
                "deviceReadyTimeout":20000  # 20s
              }

list_jizhang_zhichu=[]  #读取Excel中的支出项
list_jizhang_shouru=[]  #读取Excel中的收入项
#读取Excel中的数据项
class Jizhang:
    #读取Excel中的支出项
    def zhichu(self):
        # 1.打开Excel文件,工作表
        wb = xlrd.open_workbook(r'C:\Users\aoxiang.liu\Desktop\鲨鱼记账测试数据.xls')
        # 2.获取到sheet表
        sheet = wb.sheet_by_name("支出")  # sheet表名获取
        # 3.读取sheet中全部的内容,共有多少行,多少列(用索引定位)
        for n in range(1, sheet.nrows):
            lst_zhichu=[]
            for r in range(0, sheet.ncols):
                # 表格的数据类型
                # ctype： 0 empty,1 string, 2 number, 3 date, 4 boolean, 5 error
                ctype=sheet.cell(n, r).ctype
                cell=sheet.cell_value(n,r)
                #如果是字符串直接输出
                if ctype==1:
                    cell=cell
                #如果是数值类型直接输出
                elif ctype==2:
                    cell=int(cell)
                #如果是日期类型,转成datetime对象
                elif ctype==3:
                    cell=xldate_as_datetime(cell, 0).strftime('%Y/%m/%d')
                lst_zhichu.append(cell)
            list_jizhang_zhichu.append(lst_zhichu)
        print(f"支出项数据为:{list_jizhang_zhichu}")
        sleep(1)

    #读取Excel中的收入项
    def shouru(self):
        # 1.打开Excel文件,工作表
        wb = xlrd.open_workbook(r'C:\Users\aoxiang.liu\Desktop\鲨鱼记账测试数据.xls')
        # 2.获取到sheet表
        sheet = wb.sheet_by_name("收入")  # sheet表名获取
        # 3.读取sheet中全部的内容,共有多少行,多少列(用索引定位)
        for n in range(1, sheet.nrows):
            lst_shouru=[]
            for r in range(0, sheet.ncols):
                # 表格的数据类型
                # ctype： 0 empty,1 string, 2 number, 3 date, 4 boolean, 5 error
                ctype=sheet.cell(n, r).ctype
                cell=sheet.cell_value(n,r)
                #如果是字符串直接输出
                if ctype==1:
                    cell=cell
                #如果是数值类型直接输出
                elif ctype==2:
                    cell=int(cell)
                #如果是日期类型,转成datetime对象
                elif ctype==3:
                    cell=xldate_as_datetime(cell, 0).strftime('%Y/%m/%d')
                lst_shouru.append(cell)
            list_jizhang_shouru.append(lst_shouru)
        print(f"收入项数据为:{list_jizhang_shouru}")
        sleep(1)

class Shark_jizhang():
    #建立APP软件对象,用appium打开应用软件
    def __init__(self):
        self.awb = webdriver.Remote("http://127.0.0.1:4723/wd/hub", desired_caps)
        sleep(1)

    # 用例1:记账模块系统默认的所有支出和收入项类别
    # 标题:系统默认的所有支出和收入项类别符合需求数量
    # 前置条件:打开登录鲨鱼记账页面
    # 测试数据:无
    # 期望结果:系统默认的所有支出项(34个)和收入项(6个)类别符合需求数量
    def general(self):
        print("记账模块支出项".center(60, "="))
        # 输出记账模块中系统默认的所有支出类别项,包括设置按钮
        self.awb.find_element("id", "com.shark.jizhang:id/addTabFloat").click()  # 点击记账按钮
        sleep(1)
        list_zhichutype1= set()  # 定义空列表存放输出所有的支出类别项
        zhichutype=self.awb.find_elements("xpath","//*[@resource-id='com.shark.jizhang:id/categoryGridListView']/android.widget.LinearLayout/android.widget.TextView") #定位支出项位置元素
        for i in range(len(zhichutype)):
            list_zhichutype1.add(zhichutype[i].text)  # 循环输出支出类别项
        sleep(2)
        self.awb.swipe(300, 800, 300, 500)    #在支出页面向下滑动页面
        sleep(2)
        zhichutype = self.awb.find_elements("xpath","//*[@resource-id='com.shark.jizhang:id/categoryGridListView']/android.widget.LinearLayout/android.widget.TextView")  # 定位支出项位置元素
        for i in range(len(zhichutype)):
            list_zhichutype1.add(zhichutype[i].text)  # 循环输出支出类别项
        sleep(2)
        list_zhichutype=list(list_zhichutype1)
        print(f"系统默认的所有支出类别项为:{list_zhichutype}")

        # ==============================断言===================================
        # 期望结果:系统默认显示的支出项数量符合34个需求
        if len(list_zhichutype)==34:
            print("系统默认显示的支出项数量符合需求,测试通过")
        else:
            print("系统默认显示的支出项数量和需求不一致,测试不通过")
        sleep(1)
        self.awb.find_element("xpath","//*[@text='收入']").click() #点击收入按钮
        sleep(1)

        print("记账模块收入项".center(60,"="))
        #=======================================================================================
        # 输出记账模块中系统默认的所有收入类别项,包括设置按钮
        list_shourutype = []  #定义空列表存放输出所有的收入类别项
        shourutype=self.awb.find_elements("xpath","//*[@resource-id='com.shark.jizhang:id/categoryGridListView']/android.widget.LinearLayout/android.widget.TextView")  #定位收入项位置元素
        for i in range(len(shourutype)):
            list_shourutype.append(shourutype[i].text)  # 循环输出收入类别项
        print(f"系统默认的所有收入类别项为:{list_shourutype}")
        sleep(2)
        # ==============================断言===================================
        # 期望结果:系统默认显示的收入项数量符合6个需求
        if len(list_shourutype) == 6:
            print("系统默认显示的收入项数量符合需求,测试通过")
        else:
            print("系统默认显示的收入项数量和需求不一致,测试不通过")
        sleep(1)

    # 用例2:记一笔支出项
    # 标题:支出项记账成功
    # 前置条件:打开登录鲨鱼页面
    # 测试数据:鲨鱼记账测试数据.xls
    # 期望结果:记账成功后,跳转账本页面,显示的支出记账记录与填写的信息一致
    def zhichu_one(self):
        print("记一笔支出项".center(60, "="))
        self.awb.find_element("id", "com.shark.jizhang:id/addTabFloat").click()  # 点击记账按钮
        sleep(1)
        self.awb.find_element("xpath", f"//*[@text='{list_jizhang_zhichu[0][0]}']").click()  # 点击餐饮按钮
        sleep(1)
        try:
            self.awb.find_element("xpath","//*[@text='知道了']").click()  #点击知道了
        except:
            pass
        sleep(1)
        for i in str(list_jizhang_zhichu[0][1]):
            self.awb.find_element("xpath", f"//*[@text='{i}']").click()  # 点击键盘按钮输入数字
        sleep(1)
        self.awb.find_element("id", "com.shark.jizhang:id/date").click()  # 点击键盘今天按钮
        sleep(1)

        # ==================================================================================================
        # 定位日历表年份元素
        cur_year = datetime.date.today().year
        el_rili =self.awb.find_element("xpath","//*[@resource-id='android:id/pickers']/android.widget.NumberPicker[1]")  # 定位年份选中框的元素
        if cur_year>int(list_jizhang_zhichu[0][2].split('/')[0]):
            num=cur_year-int(list_jizhang_zhichu[0][2].split('/')[0])
            for i in range(num):
                TouchAction(self.awb).press(el_rili, 50, 50).wait(500).move_to(el_rili, 50,120).release().perform()  # 滑动日历表年份条
                sleep(1)
        elif cur_year<int(list_jizhang_zhichu[0][2].split('/')[0]):
            num =int(list_jizhang_zhichu[0][2].split('/')[0])-cur_year
            for i in range(num):
                TouchAction(self.awb).press(el_rili, 50, 120).wait(500).move_to(el_rili, 50,50).release().perform()  # 滑动日历表年份条
                sleep(1)
        else:
            pass

        # ==================================================================================================
        # 定位日历表月份元素
        cur_month = datetime.date.today().month
        el_rili = self.awb.find_element("xpath","//*[@resource-id='android:id/pickers']/android.widget.NumberPicker[2]")  # 定位月份选中框的元素
        if cur_month > int(list_jizhang_zhichu[0][2].split('/')[1]):
            num = cur_month - int(list_jizhang_zhichu[0][2].split('/')[1])
            for i in range(num):
                TouchAction(self.awb).press(el_rili, 50, 50).wait(500).move_to(el_rili, 50,120).release().perform()  # 滑动日历表年份条
                sleep(1)
        elif cur_month < int(list_jizhang_zhichu[0][2].split('/')[1]):
            num = int(list_jizhang_zhichu[0][2].split('/')[1]) - cur_month
            for i in range(num):
                TouchAction(self.awb).press(el_rili, 50, 120).wait(500).move_to(el_rili, 50,50).release().perform()  # 滑动日历表年份条
                sleep(1)
        else:
            pass

        # ==================================================================================================
        # 定位日历表日份元素
        cur_day = datetime.date.today().day
        el_rili = self.awb.find_element("xpath","//*[@resource-id='android:id/pickers']/android.widget.NumberPicker[3]")  # 定位日份选中框的元素
        if cur_day> int(list_jizhang_zhichu[0][2].split('/')[2]):
            num = cur_day - int(list_jizhang_zhichu[0][2].split('/')[2])
            for i in range(num):
                TouchAction(self.awb).press(el_rili, 50, 50).wait(500).move_to(el_rili, 50,120).release().perform()  # 滑动日历表年份条
                sleep(1)
        elif cur_day < int(list_jizhang_zhichu[0][2].split('/')[2]):
            num = int(list_jizhang_zhichu[0][2].split('/')[2]) - cur_day
            for i in range(num):
                TouchAction(self.awb).press(el_rili, 50, 120).wait(500).move_to(el_rili, 50,50).release().perform()  # 滑动日历表年份条
                sleep(1)
        else:
            pass

        self.awb.find_element("id", "com.shark.jizhang:id/dialog_dashboard_date_accept").click()  # 点击日历窗中的确定按钮
        sleep(1)
        self.awb.find_element("id", "com.shark.jizhang:id/done").click()  # 点击完成按钮
        sleep(1)
        try:
            self.awb.find_element('xpath', '//*[@text="不喜欢"]').click()  # 处理弹框,点击不喜欢
        except:
            pass
        sleep(1)

        list_zcmx=[]  #存放取出来的支出明细的详细
        # 定位明细页面上的支出账单项目名
        zcname = self.awb.find_element("xpath","/hierarchy/android.widget.FrameLayout/android.widget.LinearLayout/android.widget.FrameLayout/android.widget.LinearLayout/android.widget.FrameLayout/android.widget.FrameLayout/android.widget.RelativeLayout/android.widget.FrameLayout[2]…