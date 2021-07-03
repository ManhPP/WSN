import pandas as pd
from pandas import ExcelWriter


def process_mip_log():
    result = {}
    for file in ["logs/wsnlog-20210415222037.log"]:
        log = open(file)
        for line in log.readlines():
            if line[0] == 'i':
                path = line.split(":")[0].split("/")[-1]
            if line[0] == 'R':
                opt = line[len("Result: "):-len("\n")]
                if path not in result.keys():
                    result[path] = opt
    df = pd.DataFrame(result.items(), columns=["file", "mip"])
    df.to_excel("log_mip.xlsx")
    print("Done!")


def process_ga_log(file_name, out_file_name):
    f = open(file_name)
    result = []
    count = 0
    special_name = ["mst", "spt", "rnd"]
    writer = pd.ExcelWriter(out_file_name + ".xlsx", engine='xlsxwriter')

    for line in f.readlines():
        if line[0] == 'i':
            path = line.strip().split("/")[-1]
        if line[0] == '[':
            r = line[1:-2].split(",")
            result.append([path] + r)
            count += 1
        if count % 60 == 0 and count//60 > 0:
            df = pd.DataFrame(result, columns=["file", "min", "max", "avg", "std"])
            df.to_excel(writer, sheet_name=special_name.pop(0))
            # df.to_csv(out_file_name + "_" + special_name.pop(0) + ".xlsx")
            result = []
            count = 0
    # df = pd.DataFrame(result, columns=["file", "min", "max", "avg", "std"])
    # df.to_excel(writer, sheet_name=special_name.pop(0))
    writer.save()


if __name__ == '__main__':
    # process_mip_log()
    process_ga_log("logs/wsnlog-20210429131946.log", "ga_large")
