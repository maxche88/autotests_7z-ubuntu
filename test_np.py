from checkers import n_checkout, checkout, getout
import pytest
import yaml

with open('config.yaml') as f:
    # читаем документ YAML
    data = yaml.safe_load(f)

name_folder = os.path.basename(data["folder_in"])


class TestPositive:
    def test_step1(self, clear_folders, make_folders, make_files, print_time, write_state):
        # test1. Создаёт архив. Проверяет существование архива "arx.7z".
        res1 = checkout(f'7z a -t{data["7z_format"]} {data["folder_out"]}arx', 'Everything is Ok')
        res2 = checkout(f'ls {data["folder_out"]}', 'arx.'+data["7z_format"])
        assert res1 and res2, 'test1 FAIL'

    def test_step2(self, write_state):
        # test2. Проверяет целостность архива.
        assert checkout(f'7z t {data["folder_out"]}arx.{data["7z_format"]}', 'Everything is Ok'), 'test2 FAIL'

    def test_step3(self, write_state):
        # test3. Извлекает содержимое архива folder_out/arx.7z в директорию "folder_ext". 
        res = []
        lst_in = getout(f'ls {data["folder_in"]}').strip().split("\n")
        res.append(checkout(f'7z e {data["folder_out"]}arx.{data["7z_format"]} -o{data["folder_ext"]} -y', 'Everything is Ok'))
        # Перебирает список файлов и добавляет в res результат выполнения функции checkout.
        # Если в директории "folder_ext" существует item то True, иначе False. all возвращает True если все элементы True. 
        for item in lst_in:
            res.append(checkout(f'ls {data["folder_ext"]}', item))
        assert all(res), 'test3 FAIL'

    def test_step4(self, make_files, write_state):
        # test4. Обновляет архив. Проверяет существование новых файлов в обновлённом архиве.
        res = []
        res.append(checkout(f'7z u -t7z {data["folder_out"]}arx {data["folder_in"]}', 'Everything is Ok'))
        for item in make_files:
            res.append(checkout(f'7z l {data["folder_out"]}arx.{data["7z_format"]} ', item))
        assert all(res), 'test4 FAIL'


    def test_step5(self, write_state):
        # test5. Проверяет список файлов в архиве. Сравнивая с созданными файлами фикстурой make_files
        res = []
        lst_in = getout(f'ls {data["folder_in"]}').strip().split("\n")
        for item in lst_in:
            res.append(checkout(f'7z l {data["folder_out"]}arx.{data["7z_format"]}', item))
        assert all(res), 'test5 FAIL'


    def test_step6(self, clear_folders, make_folders, make_files, make_subfolder, write_state):
        # test6. Проверяет структуру распакованных каталогов и файлов.
        res = []
        res.append(checkout(f'7z a -t{data["7z_format"]} {data["folder_out"]}arx', 'Everything is Ok'))
        res.append(checkout(f'7z x {data["folder_out"]}arx.{data["7z_format"]} -o{data["folder_ext2"]} -y', 'Everything is Ok'))
        for path, name in make_subfolder.items():
            res.append(checkout(f'ls {path}', name))
        assert all(res), (path, name)


    def test_step8(self, clear_folders, make_folders, make_files, write_state):
        # test8. Проверяет хэш контрольной суммы.
        res = []
        for i in make_files:
            res.append(checkout(f'cd {data["folder_in"]}; 7z h {i}', 'Everything is Ok'))
            hash = getout(f'cd {data["folder_in"]}; crc32 {i}').upper()
            res.append(checkout(f'cd {data["folder_in"]}; 7z h {i}', hash))
        assert all(res), 'test8 FAIL'


    def test_step7(self, clear_folders, make_folders, make_files, write_state):
        # test7. Удаляет файлы из архива.
        res = []
        res.append(checkout(f'7z a -t{data["7z_format"]} {data["folder_out"]}arx', ''))
        res.append(checkout(f'7z d {data["folder_out"]}arx.{data["7z_format"]}', ''))
        res.append(checkout(f'7z l {data["folder_out"]}arx.{data["7z_format"]}', '0 files'))
        assert all(res), 'test7 FAIL'


class TestNegaqtive:
    def test_n_step1(self, clear_folders, make_folders, write_state):
        # test1_n. Проверка предупреждение добавления не существующией директории в архив.
        res = []
        res.append(n_checkout(f'7z a {data["folder_out"]}arx.{data["7z_format"]} /none/non-existent', 'No such file or directory'))
        res.append(n_checkout(f'7z a /none/arx.{data["7z_format"]} /none/non-existent', ''))
        assert all(res), 'n_test1 FAIL'

    def test_n_step2(self, clear_folders, make_folders, faulty_archive, write_state):
        # test2_n. Проверяет предупреждение при повреждённом архиве.
        res = []
        assert f'7z a -t{data["7z_format"]} {data["folder_out"]}arx', 'test_n_step2 FAIL'

    def test_n_step3(self, clear_folders_yield, make_folders, make_files, write_state):
        # test3_n. Проверяем ошибку создаём архива в директории без права записи.
        res = []
        res.append(checkout(f'chmod -R -w {data["folder_out"]}', ''))
        res.append(n_checkout(f'7z a -t{data["7z_format"]} {data["folder_out"]}arx {data["folder_in"]}', 'Permission denied'))
        res.append(checkout(f'chmod -R +w {data["folder_out"]}', ''))
        assert all(res), 'test_n_step3 FAIL'
