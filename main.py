import json
import random
from yiban import YiBan
import util
import sys
import datetime
import time
from threading import Thread

path = sys.path[0]

def Process(phone, password, nickname):
    try:
        yb = YiBan(phone, password)
        yb.login()
        yb.getHome()
        print("登录成功 %s" % yb.name)
        yb.auth()
        all_task = yb.getUncompletedList()["data"]
        all_task = list(filter(lambda x: "体温上报" in x["Title"], all_task))
        if len(all_task) == 0:
            print("没找到今天体温上报的任务，可能是你已经上报，如果不是请手动上报。" + time.strftime('%Y-%m-%d %h %H:%M:%S',time.localtime(time.time())))
            with open(path + "/log.txt", "a+") as fp:
                fp.write(yb.name + "||" +"没找到今天体温上报的任务，可能是你已经上报，如果不是请手动上报。" + time.strftime('%Y-%m-%d %h %H:%M:%S',time.localtime(time.time())) + "\n")
        else:
            all_task_sort = util.desc_sort(all_task, "StartTime")  # 按开始时间排序
            new_task = all_task_sort[0]  # 只取一个最新的
            print("找到未上报的任务：", new_task)
            task_detail = yb.getTaskDetail(new_task["TaskId"])["data"]
            ex = {"TaskId": task_detail["Id"],
                  "title": "任务信息",
                  "content": [{"label": "任务名称", "value": task_detail["Title"]},
                              {"label": "发布机构", "value": task_detail["PubOrgName"]},
                              {"label": "发布人", "value": task_detail["PubPersonName"]}]}

            dict_form = {"361a5d69d6db93e55bb656b4185e0447": ["36.2", "36.3", "36.4", "36.5", "36.6", "36.7"][random.randint(0, 5)],
                         "8f9a18d14676aa05e2dc26637225ffa4": ["36.2", "36.3", "36.4", "36.5", "36.6", "36.7"][random.randint(0, 5)],
                         "966c57278836ba050a382a5b70de7582": ["36.2", "36.3", "36.4", "36.5", "36.6", "36.7"][random.randint(0, 5)],  # 随机体温}
                         "2bf9494ae026b145c58b75749a01b22f": ["无"]
                         }
            submit_result = yb.submit(json.dumps(dict_form, ensure_ascii=False), json.dumps(
                ex, ensure_ascii=False), task_detail["WFId"])
            if submit_result["code"] == 0:
                share_url = yb.getShareUrl(submit_result["data"])["data"]["uri"]
                print("已完成一次体温上报[%s] %s" % (task_detail["Title"], nickname)  + time.strftime('%Y-%m-%d %h %H:%M:%S',time.localtime(time.time())))
                with open(path + "/result.txt", "a+") as fp:
                    fp.write("[+] 完成了 %s  | %s\n" % (task_detail["Title"], nickname + time.strftime('%Y-%m-%d %h %H:%M:%S', time.localtime(time.time()))))
                print("访问此网址查看详情：%s" % share_url)
            else:
                print("[%s]遇到了一些错误:%s" % (task_detail["Title"], submit_result["msg"]) + time.strftime('%Y-%m-%d %h %H:%M:%S', time.localtime(time.time())))

                with open(path + "/errors.txt", "a+") as fp:
                    fp.write("\n" + nickname + "|" + "[%s]遇到了一些错误:%s" % (task_detail["Title"], submit_result["msg"]) + time.strftime('%Y-%m-%d %h %H:%M:%S', time.localtime(time.time())))
    except Exception as e:
        print("出错啦")

        print(e)
        with open(path + "/errors.txt", "a+") as fp:
            fp.write("\n" + nickname + "|" + str(e) + time.strftime('%Y-%m-%d %h %H:%M:%S', time.localtime(time.time())))


if __name__ == '__main__':
    try:
        with open(path + "/users.txt", "r", encoding="utf-8") as fp:
            for i in fp.readlines():
                username = i.split("|")[0].strip()
                password = i.split("|")[1].strip()
                nickname = i.split("|")[2].strip()
                t = Thread(target=Process, args=(username, password, nickname,))
                t.start()
            t.join()
    except:
        print("""请检查当前目录下是否存在users.txt, 格式如下
                phone|password|name
                phone|password|name
            """)