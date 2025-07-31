import pytest
from checkers import checkout, getout
import random, string
import yaml
from datetime import datetime
import os

with open('config.yaml') as f:
    # читаем документ YAML
    data = yaml.safe_load(f)


name_folder = os.path.basename(data["folder_in"])

@pytest.fixture()
def make_folders():
    return checkout(f'mkdir {data["folder_root"]} {data["folder_in"]} {data["folder_out"]} {data["folder_ext"]} {data["folder_ext2"]}','')


@pytest.fixture()
def clear_folders():
    return checkout(f'rm -rf {data["folder_root"]}', '')

@pytest.fixture()
def clear_folders_yield():
    checkout(f'rm -rf {data["folder_root"]}', '')
    yield
    checkout(f'rm -rf {data["folder_root"]}', '')

@pytest.fixture()
def make_files():
    list_of_files = []
    for i in range(data["count"]):
        filename = ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))
        if checkout(f'dd if=/dev/urandom of={data["folder_in"]}{filename} bs={data["bs"]} count=1 iflag=fullblock', ''):
            list_of_files.append(filename)
    return list_of_files


@pytest.fixture()
def make_subfolder():
    testfilename = ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))
    subfoldername = ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))
    if checkout(f'mkdir {data["folder_in"]}{subfoldername}', ''):
        if checkout(f'dd if=/dev/urandom of={data["folder_in"]}{subfoldername}/{testfilename} bs={data["bs"]} count=1 iflag=fullblock', ''):
            path_file = data["folder_in"]+subfoldername+'/'
            path_folder = data["folder_in"]
            return {path_folder: subfoldername, path_file: testfilename}


@pytest.fixture(autouse=True)
def print_time():
    print("Start: ", datetime.now().strftime("%H:%M:%S.%f"))
    yield
    print("Finish: ", format(datetime.now().strftime("%H:%M:%S.%f")))


@pytest.fixture()
def faulty_archive():
    checkout(f'7z a data["folder_out"]arx; truncate -s 1MB data["folder_out"]arx.{data["7z_format"]}' ,'')
    yield
    checkout(f'rm data["folder_out"]arx.{data["7z_format"]}' ,'')


@pytest.fixture()
def write_state():
    start_time = datetime.now()
    load_cp = getout('cat /proc/loadavg')
    yield
    res_time = datetime.now() - start_time
    with open('stat.txt', 'a', encoding='utf-8') as stat:
        stat.write(f'Время выполнения: {res_time}, count: {data["count"]}, bs: {data["bs"]}, CP: {load_cp}\n')

pytest.fixture()
def start_time():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


