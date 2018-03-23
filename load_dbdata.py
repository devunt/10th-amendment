from scripts.fixture import load_fixtures


def main():
    with open('dbdata.json', 'r', encoding='utf-8') as f:
        data = f.read()
        load_fixtures(data)


if __name__ == '__main__':
    main()
