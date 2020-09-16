def load_conf(path: str):
    module_flag = 0
    module_list = []
    with open(file=path, mode="r") as conf:
        for line in conf:
            strip_line = line.strip()
            if module_flag == 1:
                module_list.append(strip_line)
            if strip_line == "[modules]":
                module_flag = 1

    return module_list
