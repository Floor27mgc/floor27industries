import argparse
import ast
import csv
import json
import pandas
import re
import shlex


class StatsAggregator(object):
    
    def __init__(self, name):
        self.my_name = name
        self.count = 0
        self.max = 0
        self.min = 0
        self.sum = 0
        self.data = []

    def feed_data(self, data_point):
        self.data.append(data_point)
        if data_point > self.max:
            self.max = data_point
        if data_point < self.min:
            self.min = data_point
        self.sum += data_point
        self.count += 1

    @property
    def name(self):
        return self.my_name

    @property
    def avg(self):
        return 0 if self.count == 0  else self.sum / self.count

    @property
    def maximum(self):
        return self.max

    @property
    def minimum(self):
        return self.min



class DataClass(object):

    NUM_WORLDS = 16
    NUM_LEVELS = 9
    
    def __init__(self):
        self.data = []
        self.world_data = self.init_world_data()

    def init_world_data(self):
        i = 1
        world_data = {}
        while i <= DataClass.NUM_WORLDS:
            world_data[str(i)] = self.init_level_data()
            i+=1
        return world_data

    def init_level_data(self):
        i = 1
        data = {}
        while i <= DataClass.NUM_LEVELS:
            stats_aggregator = StatsAggregator("Level" + str(i))
            data[str(i)] = stats_aggregator
            i+=1
        return data

    @staticmethod
    def remove_non_alnum(text):
        return re.sub(r"[^a-zA-Z0-9]","", text)

    def format_json_string(self, string):
        # hacktacular
        tokens = shlex.split(string)
        json_string = "{"
        for token in tokens:
            t = self.remove_non_alnum(token)
            json_string += "\""
            json_string += t
            if not t.isdigit() and "{" not in t:
                json_string += ":"
            json_string += ""

            if t.isdigit():
                json_string += "\","
        json_string = json_string[3:-1]
        json_string = "{" + json_string + "}"
        return json_string

    def parse_list_from_string(self, data_string):
        d = {}
        try: 
            d = json.loads(self.format_json_string(data_string))
        except ValueError:
            pass
        finally:
            return d

    def tabulate(self, series, column):
        for row in self.data:
            if series in row and column in row:
                if "World:" in row:
                    #print row["Level:"] + " " + row[column]
                    self.world_data[row["World:"]][row["Level:"]].feed_data(int(row[column]))

    def print_averages(self, world_num, level_num):
        print "World {}, {}, {}, {}".format(
            world_num,
            self.world_data[str(world_num)][str(level_num)].name,
            self.world_data[str(world_num)][str(level_num)].avg,
            self.world_data[str(world_num)][str(level_num)].count)

    def debug_data(self):
        for entry in self.data:
            print entry

    def load_data(self, filename):
        with open(filename, "rb") as csvfile:
            reader = csv.reader(csvfile, delimiter=",")
            for row in reader:
                if row[8] != "{}":
                    self.data.append(self.parse_list_from_string(row[8]))
        


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--filename", help="name of file to parse", required=True)
    parser.add_argument("--field", help="field to get data about", default="StrokesThisLevel")
    parser.add_argument("--series", help="series data to grab", default="Level")
    args = parser.parse_args()

    data_class = DataClass()
    data_class.load_data(args.filename)
    data_class.tabulate("{}:".format(args.series), "{}:".format(args.field))
    #data_class.debug_data()
    i = 1
    while i <= DataClass.NUM_WORLDS:
        j = 1
        while j <= DataClass.NUM_LEVELS:
            data_class.print_averages(i, j)
            j+=1
        i+=1
    

if __name__ == "__main__":
    main()
