from service import Service




if __name__ == '__main__':
    ser = Service(interval=0.05, timeout=2)
    ser.run()