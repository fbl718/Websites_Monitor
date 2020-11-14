from apscheduler.schedulers.background import BackgroundScheduler

class output():
    def __init__(self):
        self.value=10
        self.schedule=BackgroundScheduler()

    def out(self):
        self.value=self.value+1
        print(self.value)

    def auto(self):
        schedule.start()
        print('here')


if __name__ == '__main__':
    sample=output()
    schedule = BackgroundScheduler()
    schedule.add_job(sample.out, 'interval', seconds=5)
    sample.auto()
    x=input("")