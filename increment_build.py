# increment_build.py
import os

def increment_build_number(file_path):
    if not os.path.isfile(file_path):
        with open(file_path, 'w') as file:
            file.write('1')
    else:
        with open(file_path, 'r') as file:
            build_number = int(file.read().strip())

        build_number += 1

        with open(file_path, 'w') as file:
            file.write(str(build_number))

if __name__ == "__main__":
    build_number_file = 'build_number.txt'
    increment_build_number(build_number_file)
