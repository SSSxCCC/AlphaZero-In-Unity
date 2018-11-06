import json
import os
from matplotlib import pyplot


def loss_entropy_vs_batch():
    path_prefix = "../Gobang/model2_10_10_5/"
    path_suffix = "/statistics.json"
    batch_list = list(range(50, 11001, 50))
    loss_list, entropy_list = [], []
    for batch in batch_list:
        with open(path_prefix + str(batch) + path_suffix, "r") as file:
            load_dict = json.load(file)
        loss_list.append(load_dict["loss"])
        entropy_list.append(load_dict["entropy"])
    pyplot.xlabel("n")
    pyplot.ylabel("value")
    pyplot.plot(batch_list, loss_list, label="loss")
    pyplot.plot(batch_list, entropy_list, label="entropy")
    pyplot.legend()
    pyplot.show()


def loss_entropy_vs_time():
    path_prefix = "../Gobang/tictatoe/"
    path_suffix = "/statistics.json"
    batch_list = list(range(50, 7351, 50))
    loss_list, entropy_list, times = [], [], []
    for batch in batch_list:
        file_path = path_prefix + str(batch) + path_suffix
        with open(file_path, "r") as file:
            load_dict = json.load(file)
        loss_list.append(load_dict["loss"])
        entropy_list.append(load_dict["entropy"])
        if len(times) == 0:
            first_time = os.path.getctime(file_path)
        times.append(os.path.getctime(file_path) - first_time)
    pyplot.xlabel("time")
    pyplot.ylabel("value")
    pyplot.plot(times, loss_list, label="loss")
    pyplot.plot(times, entropy_list, label="entropy")
    pyplot.legend()
    pyplot.show()


def loss_vs_batch():
    path_prefix = "../Gobang/model_8_8_5/"
    path_suffix = "/statistics.json"
    batch_list = list(range(50, 11001, 50))
    loss_list = []
    for batch in batch_list:
        with open(path_prefix + str(batch) + path_suffix, "r") as file:
            load_dict = json.load(file)
        loss_list.append(load_dict["loss"])

    path_prefix = "../Gobang/model2_8_8_5/"
    path_suffix = "/statistics.json"
    #batch_list = list(range(50, 11001, 50))
    loss_list2 = []
    for batch in batch_list:
        with open(path_prefix + str(batch) + path_suffix, "r") as file:
            load_dict = json.load(file)
        loss_list2.append(load_dict["loss"])

    pyplot.xlabel("n")
    pyplot.ylabel("loss")
    pyplot.plot(batch_list, loss_list, label="cnn")
    pyplot.plot(batch_list, loss_list2, label="resnet")
    pyplot.legend()
    pyplot.show()


if __name__ == "__main__":
    loss_vs_batch()