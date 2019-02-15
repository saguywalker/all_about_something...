class Time:
    def __init__(self, hr, mn, sec, msec):
        self.hr = hr
        self.mn = mn
        self.sec = sec
        self.msec = msec

    def add(self, time_sec):
        sec_plus_time_sec = self.sec + time_sec
        if sec_plus_time_sec < 60:
            new_sec = sec_plus_time_sec
            return Time(int(self.hr), int(self.mn), int(new_sec), int(self.msec))
        else:
            remain_time_sec = time_sec - (60 - self.sec)
            new_sec = 0
            new_mn = self.mn + 1

            new_hr = self.hr + (remain_time_sec // 3600)
            remain_time_sec %= 3600

            new_mn = new_mn + (remain_time_sec // 60)
            remain_time_sec %= 60
            if new_mn > 60:
                new_hr += new_mn // 60
                new_mn -= new_mn // 60 * 60

            new_sec = new_sec + remain_time_sec

            return Time(int(new_hr), int(new_mn), int(new_sec), int(self.msec))

    def __repr__(self):
        return "{:02d}:{:02d}:{:02d}.{:03d}".format(self.hr, self.mn, self.sec, self.msec)




if __name__ == "__main__":
    time = Time(10,56,24,706)
    print("original:",time)
    print("add 123:",time.add(123))
    print("add 5:",time.add(5))
    print("add 4000:",time.add(4000))
    print("add 258:",time.add(258))

