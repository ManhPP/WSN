import pandas as pd


def process_mip_log():
    result = {}
    for file in ["logs/wsnlog-20210415222037.log"]:
        log = open(file)
        for line in log.readlines():
            if line[0] == 'i':
                path = line[len(
                    "input path /home/tamnt/mpp/WSN/data/new_hop/"):-len(
                    ": \n")]
            if line[0] == 'R':
                opt = line[len("Result: "):-len("\n")]
                if path not in result.keys():
                    result[path] = opt
    df = pd.DataFrame(result.items(), columns=["file", "mip"])
    df.to_csv("log_mip.csv")
    print("Done!")


def process_ga_log(file_name, out_file_name):
    f = open(file_name)
    result = []
    count = 0
    special_name = ["mst", "spt", "rnd"]
    for line in f.readlines():
        if line[0] == 'i':
            path = line[len("input path: /home/tamnt/mpp/WSN/data/new_hop/"):-len("\n")]
        if line[0] == '[':
            r = line[1:-2].split(",")
            result.append([path] + r)
            count += 1
        if count % 60 == 0 and count//60 > 0:
            df = pd.DataFrame(result, columns=["file", "min", "max", "avg", "std"])
            df.to_csv(out_file_name + "_" + special_name.pop(0) + ".csv")
            result = []
            count = 0


if __name__ == '__main__':
    # process_mip_log()
    process_ga_log("logs/wsnlog-20210426220003.log", "ga_small")
