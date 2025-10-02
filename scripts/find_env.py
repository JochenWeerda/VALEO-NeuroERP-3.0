import os

def find_env_files(start_path):
    for root, dirs, files in os.walk(start_path):
        for file in files:
            if file == '.env':
                full_path = os.path.join(root, file)
                print(f"Found .env file at: {full_path}")
                try:
                    with open(full_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        print(f"File is valid UTF-8")
                except UnicodeDecodeError:
                    print(f"File is NOT valid UTF-8")

if __name__ == '__main__':
    find_env_files('.') 