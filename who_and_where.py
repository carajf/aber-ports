# IMPORTING REQUIRED MODULES
from pprint import pprint
from anytree.exporter.dotexporter import UniqueDotExporter

# CONNECTING TO THE DATABASE
import pymongo
from pymongo import MongoClient
import matplotlib.pyplot as plt
from anytree import Node, RenderTree
from anytree.exporter import DotExporter


client = MongoClient("mongodb://localhost:27017/")
db = client.aber_ship_db
coll = db.aber_mariners


##################################################
#### HISTOGRAM OF NUMBER OF CREW ON EACH SHIP ####
##################################################


def counting_vessels():
    """for each unique ship
        for each unique person on that ship
            add to the person count of that ship"""

    query = [
        {
            "$group": {
                "_id": {
                    "vessel_name": "$vessel name",
                    "vessel_number": "$official number",
                    "name": "$name",
                    "age": "$age",
                    "DOB": "$year_of_birth",
                    "place_of_birth": "$place_of_birth",
                },  # gets documents which are unique with the grouping above
                "count": {
                    "$sum": 1
                },  # adds 1 to the total count for each document belonging to this name group
            }
        },
        # Sorting the order
        {"$sort": {"count": 1}},
        # Showing only the names and the count of each name
        {
            "$project": {
                "_id": True,
                "count": True,
            }
        },
    ]

    result = coll.aggregate(query)

    vessel_counts = {}

    for doc in result:
        vessel_name = doc["_id"]["vessel_name"]
        if vessel_name in vessel_counts:
            vessel_counts[vessel_name] += 1
        else:
            vessel_counts[vessel_name] = 1

    return vessel_counts


def get_histogram_data():
    """x axis = number of people (e.g. 0-10, 10-20, 20-30)
    y axis = number of ships"""

    vessel_counts = counting_vessels()

    # Sorting the dictionary by highest count (descending order)
    sorted_vessel_counts = dict(
        sorted(vessel_counts.items(), key=lambda item: item[1], reverse=True)
    )

    # Setting the upper bound of the range
    range_upper = list(sorted_vessel_counts.values())[
        0
    ]  # gets the first value from the sorted dictionary, which is the highest value

    # Getting the bins values (difference of 30)
    bins_values = []
    for r in range(0, range_upper, 30):
        bins_values.append(r)

    # Getting the values for the y axis (frequency)
    y_data = []
    for value in vessel_counts.values():
        y_data.append(value)

    # range_list = []
    # a = 0
    # for r in range(0, range_upper, 30):
    #     new_range = range(a, r)
    #     range_list.append(new_range)
    #     a = r+1

    # vessel_ranges = {}

    # # Adding the vessel to the list of vessel values with the range key
    # for vessel, count in vessel_counts.items():
    #     for index in range_list:
    #         if count in index:
    #             this_range = index
    #             if this_range in vessel_ranges.keys():
    #                 vessel_ranges[this_range].append(vessel)
    #             else:
    #                 vessel_ranges[this_range] = []
    #                 vessel_ranges[this_range].append(vessel)
    #             break

    return bins_values, y_data, range_upper


def plot_histogram():
    """Takes the data from the function get_histogram_data() and plots it to a histogram"""

    x, y, range_upper = get_histogram_data()
    plt.hist(y, bins=x)
    plt.ylabel("Number of Ships")
    plt.xlabel("Number of People")
    plt.title("A Histogram Showing the Number of Ships Which Had x Number of People")
    plt.xticks(x)
    plt.xlim(1, range_upper)  # Removes any values of 0
    plt.show()


plot_histogram()


######################################################
#### DESTINATIONS TREE (TOP 10 and 5 MOST VISITED ####
######################################################


def get_port_maps():
    """Gets all of the unique joining ports for every ship, along with the unique leaving port, as long as neither port is blank nor the joining port is Aberystwyth."""
    query = [
        {"$match": {"this_ship_joining_port": {"$ne": "blk"}}},
        {"$match": {"this_ship_joining_port": {"$ne": "Aberystwyth"}}},
        {"$match": {"this_ship_leaving_port": {"$ne": "blk"}}},
        {"$match": {"this_ship_leaving_port": {"$ne": ""}}},
        {"$match": {"this_ship_leaving_port": {"$ne": "Blk"}}},
        {"$match": {"this_ship_leaving_port": {"$ne": "Remains"}}},
        {"$match": {"this_ship_leaving_port": {"$ne": "None"}}},
        {
            "$group": {
                "_id": {
                    "vessel_name": "$vessel name",
                    "vessel_number": "$official number",
                    "joining_port": "$this_ship_joining_port",
                    "joining_date": "$this_ship_joining_date",
                    "leaving_port": "$this_ship_leaving_port",
                },  # gets documents which are unique with the grouping above
            }
        },
        {
            "$group": {
                "_id": {
                    "joining_port": "$_id.joining_port",
                    "leaving_port": "$_id.leaving_port",
                },
                "count": {"$sum": 1},
            }
        },
        {
            "$project": {
                "_id": 0,
                "joining_port": "$_id.joining_port",
                "leaving_port": "$_id.leaving_port",
                "count": True,
            }
        },
    ]

    result = coll.aggregate(query)

    docs = []
    for doc in result:
        docs.append(doc)

    # Counting the number of times a joining port appears (to get the top 10)
    joining_port_counts = {}
    for item in docs:
        joining_port = item.get("joining_port")
        count = item.get("count")
        if joining_port in joining_port_counts:
            joining_port_counts[joining_port] += count
        else:
            joining_port_counts[joining_port] = count

    # Sorting the joining port counts to get the top 10
    sorted_joining_ports = dict(
        sorted(joining_port_counts.items(), key=lambda item: item[1], reverse=True)
    )

    # Top 10
    top_10_with_counts = {
        k: sorted_joining_ports[k] for k in list(sorted_joining_ports)[:10]
    }

    leaving_ports_of_top_10_joining = []

    for doc in docs:
        doc_joining_port = doc.get("joining_port")
        doc_leaving_port = doc.get("leaving_port")
        if doc_joining_port in top_10_with_counts:
            if (
                doc_leaving_port != doc_joining_port
            ):  # Making sure the leaving port is not the joining port, otherwise that won't count as an actual route (and we're interested in routes)
                leaving_ports_of_top_10_joining.append(doc)

    leaving_ports_sorted = sorted(
        leaving_ports_of_top_10_joining, key=lambda k: k["count"], reverse=True
    )

    ten_to_five_dict = {}
    only_get_5 = {}

    for item in leaving_ports_sorted:
        # Get the values from each key
        joining_port = item.get("joining_port")
        leaving_port = item.get("leaving_port")
        count = item.get("count")

        # As the list is in order of the highest counted routes, we can iterate over the dictionary in order of the list items (starting from 0)

        # This adds to the only_get_5 dictionary every time the joining port has already been iterated over, which means the loop will stop when the joining port has the top 5 leaving ports already mapped in the ten_to_five_dict
        if joining_port in only_get_5.keys():
            if only_get_5[joining_port] < 5:
                only_get_5[joining_port] += 1
                ten_to_five_dict[joining_port].append(leaving_port)
        else:  # otherwise create the initial value of 1 and the empty list to append to with the leaving port
            only_get_5[joining_port] = 1
            ten_to_five_dict[joining_port] = []
            ten_to_five_dict[joining_port].append(leaving_port)

    return ten_to_five_dict


def visualise_tree():
    data = get_port_maps()

    root_port = Node("Aberystwyth")
    for key, value in data.items():
        key = Node(key, parent=root_port)
        value = Node(value, parent=key)

    for pre, fill, node in RenderTree(root_port):
        txt_tree = "%s%s" % (pre, node.name)

    DotExporter(root_port).to_dotfile("tree.dot")

    from graphviz import Source

    Source.from_file("tree.dot")
    from graphviz import render

    render("dot", "png", "tree.dot")

    # DotExporter(root_port).to_picture("visited_ports_tree.png")


visualise_tree()
