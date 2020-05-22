from argparse import ArgumentParser
import configparser
from utils.init_log import init_log
from pathlib import Path


def parse_argument():
    parser = ArgumentParser()
    parser.add_argument('--pop-size', default=50, type=int)
    parser.add_argument('--iterations', default=1000, type=int)
    parser.add_argument('--patience', default=20, type=int)
    parser.add_argument('--cross-rate', default=0.7, type=float)
    parser.add_argument('--mut-rate', default=0.1, type=float)

    return parser.parse_args()


def parse_config():
    parser = configparser.ConfigParser()
    config_file_path = Path(__file__).parent
    parser.read(f"{config_file_path}/config.ini")
    dict_constant = dict()
    dict_constant["epsilon_fs"] = parser.getfloat("CONSTANT", "epsilon_fs")
    dict_constant["epsilon_mp"] = parser.getfloat("CONSTANT", "epsilon_mp")
    dict_constant["E_DA"] = parser.getfloat("CONSTANT", "E_DA")
    dict_constant["E_RX"] = parser.getfloat("CONSTANT", "E_RX")
    dict_constant["E_TX"] = parser.getfloat("CONSTANT", "E_TX")
    dict_constant["l"] = parser.getint("CONSTANT", "l")
    dict_constant["rate_mst"] = parser.getfloat("INIT", "rate_mst")
    dict_constant["rate_spt"] = parser.getfloat("INIT", "rate_spt")
    data_path = f"{config_file_path.parent}/{parser.get('PATH', 'data_path')}"
    return dict_constant, data_path


if __name__ == '__main__':
    # parse_config()
    # logger = init_log()
    # logger.info("arg_parser")
    # logger.warning("this is test")
    dict_const = parse_config()
    print(dict_const)
    # logger.info(dict_const)
