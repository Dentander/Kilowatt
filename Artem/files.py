def convert_to_my_type(in_path, out_path):
    """
    Конвертация файла .wi с клеточным полем в наш .txt

    :param in_path: путь конвертируемого файла
    :param out_path: путь к результирующему файлу
    """
    input_file = open(in_path)
    output_file = open(out_path, 'w')
    for i, line in enumerate(input_file):
        for j, char in enumerate(line):
            if char == '#':
                output_file.writelines(f'c {j} {i}\n')
            if char == '@':
                output_file.writelines(f'h {j} {i}\n')
            if char == '~':
                output_file.writelines(f't {j} {i}\n')
    input_file.close()
    output_file.close()
