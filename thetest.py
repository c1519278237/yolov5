import os.path
import subprocess
import cv2


class PositionTest:
    def __init__(self, file_path, video_name):
        self.frames = []    # 存储每一帧中的所有位置
        self.pig_paths = []      # 存储所有猪的路径
        self.file_path = file_path
        self.video_name = video_name

    def main_function(self):
        self.main_test()
        self.path_paint()

    def path_paint(self):
        print('painting')
        color = (0, 255, 0)

        # cap = cv2.VideoCapture('runs/detect/exp/VID_test_2.mp4')
        cap = cv2.VideoCapture(self.file_path+'/'+self.video_name+'.mp4')
        print(self.file_path+'/'+self.video_name)
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        fps = cap.get(cv2.CAP_PROP_FPS)
        out = cv2.VideoWriter('output.mp4', fourcc, fps, (width, height))

        which_nums = 1
        paths = [list(to_list) for to_list in self.pig_paths]
        for i in paths:
            i.append(0)

        while True:     # 每一帧
            # print(which_nums)
            ret, frame = cap.read()
            if not ret:
                break
            # 绘制当前帧的路径
            for a_path in paths:
                if a_path[0] == which_nums and a_path[2]+1 < len(a_path[1]):    # 如果其帧指针与当前的帧相同且指向的位置有效
                    for i in range(15):
                        if a_path[2]-i < 0:
                            # print()
                            break
                        point1 = list(a_path[1][a_path[2]-i])
                        point1[0] = int(float(point1[0]) * width)
                        point1[1] = int(float(point1[1]) * height)
                        point2 = list(a_path[1][a_path[2]-i+1])
                        point2[0] = int(float(point2[0]) * width)
                        point2[1] = int(float(point2[1]) * height)
                        print('距离：', self.distance_calculation(point1, point2))
                        if self.distance_calculation(point1, point2) < 20:
                            frame = cv2.line(frame, tuple(point1), tuple(point2), color, 2)
                        else:
                            print('过长，不输出')
                    a_path[0] += 1
                    a_path[2] += 1
            # 将处理后的视频帧输入到文件
            out.write(frame)
            which_nums += 1

        cap.release()
        out.release()
        # cv2.destroyAllWindows()
        # for i in paths:
        #     print(i)

    def main_test(self):
        # 运行yolo，输出结果
        # self.run_detect()

        # 读入输出的结果
        self.read_frame()

        # 逐帧分析
        #   读取第一帧，创建对应猪的列表
        nowsframe = self.frames.pop(0)
        for nowspig in nowsframe:   # 当前帧中的一只猪的数据
            now_position = (nowspig[1], nowspig[2])   # 这只猪的画面坐标
            one_pigs_path = (1, [now_position])           # 这只猪的路径(起始帧，路径)
            self.pig_paths.append(one_pigs_path)      # 将这一路径存到路径集合中
        # print(self.pig_paths)   # 测试用
        #   重复读取余下帧
        which_nums = 2          # 从第二帧开始
        frame_list = [self.pig_paths, []]     # 两个列表，分为“当前帧未使用过”和“使用过”，每帧一翻转
        self.pig_paths = []

        for nows_frame in self.frames:  # 读出一帧
            for nowspig in nows_frame:  # 读出帧中一条
                now_position = (nowspig[1], nowspig[2])
                # 将位置插入对应的路径中
                self.position_insertion(now_position, which_nums, frame_list)

            which_nums += 1
            # 翻转 frame_list，并将中断了的路径存入路径集中
            frame_list.reverse()

            # print("这一帧（", which_nums, ")执行完成，翻转后的列表为：")
            # print("进入下一段的：")
            # for i in frame_list[0]:
            #     print(i)
            # print("应该被存储的")
            # for i in frame_list[1]:
            #     print(i)

            # 存储中断了的路径
            if len(frame_list[1]) != 0:
                for interrupted_path in frame_list[1]:
                    self.pig_paths.append(interrupted_path)
                frame_list[1] = []
        # 存储编辑好的路径
        for a_path in frame_list[0]:

            # print("存入：", a_path)

            self.pig_paths.append(a_path)

        # print(len(self.pig_paths))   # 测试用
        # for i in self.pig_paths:
        #     print(i)

    def position_insertion(self, now_position, which_nums, frame_list):

        print("第几帧：", which_nums)

        min_distance = [-1, -1, -1, -1]     # 【“未使用帧”指针，距离，“已使用帧”指针，距离】
        # 遍历“未使用路径”，求末端与当前位置的距离，标记距离最短的路径

        print("未使用过的路径为：")

        for_i = 0
        for a_path in frame_list[0]:

            print(a_path)

            this_distance = self.distance_calculation(now_position, a_path[1][-1])
            if min_distance[0] == -1 or this_distance < min_distance[1]:
                min_distance[1] = this_distance
                min_distance[0] = for_i
        for_i += 1

        # 遍历“使用过路径”，求-2节点与当前位置的距离，标记距离最短的路径

        print("使用过的路径为：")

        for_i = 0
        for a_path in frame_list[1]:

            print(a_path)
            if len(a_path[1]) != 1:     # 如果是该帧刚建立的路径则跳过
                this_distance = self.distance_calculation(now_position, a_path[1][-2])
                if min_distance[2] == -1 or this_distance < min_distance[3]:
                    print('选中：', a_path)
                    min_distance[3] = this_distance
                    min_distance[2] = for_i
            else:
                print(a_path, '为该帧新建立，被跳过')
            for_i += 1

        print("选出的路径：", min_distance)

        # 比较出最短路径，将位置插入对应的路径中（距离相等时“未使用”优先）
        #   todo：若最短路径大于某值或没有可插入的路径，则新建路径。
        if min_distance[0] == -1 and min_distance[3] == -1 :
            new_path = (which_nums, [now_position])
            frame_list[1].append(new_path)
        else:
            if (min_distance[3] != -1 and min_distance[1] != -1 and min_distance[3] < min_distance[1]) \
                    or min_distance[1] == -1:
                #   若为“使用过路径”
                if self.distance_calculation(frame_list[1][min_distance[2]][1][-1], frame_list[1][min_distance[2]][1][-2]) <= min_distance[3]:
                    # 若-2节点与-1节点的距离更小，则转为”未使用路径“
                    if min_distance[0] != -1:
                        frame_list[0][min_distance[0]][1].append(now_position)
                        frame_list[1].append(frame_list[0].pop(min_distance[0]))
                    else:
                        new_path = (which_nums, [now_position])
                        frame_list[1].append(new_path)

                elif self.distance_calculation(frame_list[1][min_distance[2]][1][-1], frame_list[1][min_distance[2]][1][-2]) > min_distance[3]:
                    # 若-2节点与-1节点的距离更大，则替换该-1节点，并重复调用该函数传入-1节点
                    changed_position = frame_list[1][min_distance[2]][1].pop(-1)
                    frame_list[1][min_distance[2]][1].append(now_position)
                    out_path = frame_list[1].pop(min_distance[2])
                    self.position_insertion(changed_position, which_nums, frame_list)
                    frame_list[1].append(out_path)
            elif (min_distance[3] != -1 and min_distance[1] != -1 and min_distance[3] >= min_distance[1]) \
                    or min_distance[3] == -1:
                # 若为“未使用路径”，移入“使用路径”

                # print("frame:", frame_list)
                # print(len(frame_list))
                # print(min_distance)
                frame_list[0][min_distance[0]][1].append(now_position)
                frame_list[1].append(frame_list[0].pop(min_distance[0]))
            else:
                print("啥情况？？")
                print(min_distance)

    def distance_calculation(self, position_1, position_2):
        distance = \
            ((float(position_1[0])-float(position_2[0]))**2 + (float(position_1[1])-float(position_2[1]))**2)**0.5
        return distance

    # 运行YOLO
    @staticmethod
    def run_detect():
        cmd = ["python", "detect.py", "--save-txt"]
        subprocess.run(cmd)

    # 读取yolo的结果
    def read_frame(self):
        # txt_name = 'runs/detect/exp/labels/VID_test_2_{}.txt'
        txt_name = self.file_path + '/labels/' + self.video_name + '_{}.txt'
        # print(txt_name)

        i = 1
        while True:
            # 遍历到不存在的文件名时退出
            filename = txt_name.format(i)
            if not os.path.exists(filename):
                break

            with open(filename, "r") as f:
                one_frame = []
                for line in f:
                    oneline = line.strip().split(" ")   # 一只猪
                    one_frame.append(oneline)            # 一帧中所有猪

                self.frames.append(one_frame)

            i += 1  # 逐个打开文件



# # get_frame测试
# atest = PositionTest('runs/detect/exp', 'VID_test_2')
# atest.read_frame()
# print(atest.frames)

# main_test 测试
# atest = PositionTest()
# atest.main_test()

# path_paint测试
atest = PositionTest('E:\QQ\FileRecv\1519278237\FileRecv\yolov5(1)\runs\detect\exp27\VID_test_2.mp4', 'VID_test_2')
atest.main_function()