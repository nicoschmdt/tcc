from .tu2017 import treatData


if __name__ == "__main__":
    from sys import argv

    if argv[1] == "tu2017":
        treatData.main()