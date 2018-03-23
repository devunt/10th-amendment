from scripts.generator import generate_data_json


def main():
    data = generate_data_json()
    with open('docs/data.json', 'w', encoding='utf-8') as f:
        f.write(data)


if __name__ == '__main__':
    main()
