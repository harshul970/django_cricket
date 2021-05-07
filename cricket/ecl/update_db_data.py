from . import views

list_1 = [
    ['SA', 'South Africa'],
    ['ENG', 'England'],
]


def main():
    for i in list_1:
        print(i[0] + " , " + i[1])


if __name__ == '__main__':
    main()
