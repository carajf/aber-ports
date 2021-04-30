############################################
############## PREREQUISITES ###############
############################################

# IMPORTING REQUIRED MODULES
from pprint import pprint
from tkinter import *
from tkinter import ttk
import tkinter as tk
import matplotlib.pyplot as plt
import datetime

# CONNECTING TO THE DATABASE
import pymongo
from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017/")
db = client.aber_ship_db
coll = db.aber_mariners


# GLOBAL VARIABLES - these are nececssary to make certain functions work where they are not nested inside other functions where these variables are created
global tree_count
tree_count = 0

global sel_name_tree
global sel_name_2_tree


############################################
###### QUERYING DB FOR MARINER NAMES #######
############################################

# FINDING MARINERS AND GROUPING BY NAME
def group_by_name():
    """Function which groups mariners by name, counts how many times that name appears in the datatbase, and returns the result in a list 'grouped_mariner'."""

    query = [  # Grouping those with the same name to make selection easier
        {
            "$group": {
                "_id": {"name": "$name"},  # groups documents  by the "name" field
                "uniqueIds": {
                    "$addToSet": "$_id"
                },  # # adds to the uniqueIds array any unique _id found in this group
                "count": {
                    "$sum": 1
                },  # adds 1 to the total count for each document belonging to this name group
            }
        },
        # Sorting the order in which the names print (descending)
        {"$sort": {"count": -1}},
        # Showing only the names and the count of each name
        {"$project": {"_id": 0, "name": "$_id.name", "count": True}},
    ]

    mariners = coll.aggregate(query)
    groups = []
    for mariner in mariners:
        groups.append(mariner)

    return groups


# Triggers the group_by_name function and assigns the returned data to the grouped_mariners variable
grouped_mariners = group_by_name()


########################################################
###### PRESENTING TO USER AND ALLOWING SELECTION #######
########################################################


def view_mariners(the_mariners):

    global sel_name_tree
    global sel_name_2_tree

    # The function which is triggered when a user selects an item from the list
    def list_select(event):

        # Definining which item is selected
        widget = event.widget
        index = int(widget.curselection()[0])
        value = widget.get(index)

        global tree_count

        # Delete any old TreeView from previous user selection
        if tree_count == 0:
            sel_name_tree.delete(*sel_name_tree.get_children())
        else:
            sel_name_2_tree.delete(*sel_name_2_tree.get_children())

        def unique_selected(name):
            print('You selected item %d: "%s"' % (index, value))

            query = [  # Grouping those with the same name to make selection easier
                {"$match": {"name": "%s" % (value)}},
                {
                    "$group": {
                        "_id": {
                            "name": "$name",
                            "age": "$age",
                            "DOB": "$year_of_birth",
                            "place_of_birth": "$place_of_birth",
                        },  # groups documents  by the three fields
                        "uniqueIds": {
                            "$addToSet": "$_id"
                        },  # adds to the uniqueIds array any unique _id found in this group
                        "count": {
                            "$sum": 1
                        },  # adds 1 to the total count for each document belonging to this name group
                    }
                },
                # Sorting the order in which the names print (descending)
                {"$sort": {"count": -1}},
                # Showing only the names and the count of each name
                {
                    "$project": {
                        "_id": 0,
                        "uniqueIds": True,
                        "mariner": "$_id",
                        "count": True,
                    }
                },
            ]

            result = coll.aggregate(query)

            unique_mariners = []
            for mariner in result:
                unique_mariners.append(mariner)

            return unique_mariners

        # Getting the unique mariners from the chosen name
        selected_mariners = unique_selected(value)

        # Inserting the unique mariners with the selected name
        for selected_mariner in selected_mariners:

            # Creating a list in which all values of the desired keys will be stored in (for displaying items in the GUI list in the desired format)
            pretty = []

            # Setting the default blank variable in case the desired key does not exist
            default = "blk"

            # Adding the name
            pretty.append(selected_mariner["mariner"]["name"])

            # Looping through each desired key to check it exists, otherwise assigning the key with the value 'blk' for 'blank'
            if "DOB" in selected_mariner["mariner"]:
                pretty.append(selected_mariner["mariner"]["DOB"])
            else:
                selected_mariner["mariner"]["DOB"] = default
                pretty.append(selected_mariner["mariner"]["DOB"])

            if "age" in selected_mariner["mariner"]:
                pretty.append(selected_mariner["mariner"]["age"])
            else:
                selected_mariner["mariner"]["age"] = default
                pretty.append(selected_mariner["mariner"]["age"])

            if "place_of_birth" in selected_mariner["mariner"]:
                pretty.append(selected_mariner["mariner"]["place_of_birth"])
            else:
                selected_mariner["mariner"]["place_of_birth"] = default
                pretty.append(selected_mariner["mariner"]["place_of_birth"])

            # Insert mariner into one of the trees
            if tree_count == 1:
                new_entry = sel_name_2_tree.insert(
                    "", "end", text=selected_mariner["uniqueIds"], values=(pretty)
                )
                current_tree = 1
            else:
                new_entry = sel_name_tree.insert(
                    "", "end", text=selected_mariner["uniqueIds"], values=(pretty)
                )
                current_tree = 0

        if current_tree == 1:
            tree_count -= 1
        else:
            tree_count += 1

    # The function which is triggered when a user selects an item from the tree
    def tree_select(event):

        cur = sel_name_tree.focus()
        curItem = sel_name_tree.item(cur)

        # Splitting the values in the 'text' key otherwise the numbers were being iterated over per digit
        selected_ids = str(curItem["text"]).split()
        int_selected_ids = list(map(int, selected_ids))

        # Creating the new Window for the mariner detail to be displayed in
        newWindow = tk.Toplevel(window)
        newWindow.geometry("1280x720")

        # Creating the TreeView widget in which the selected mariner's details to be displayed in
        columns = (
            "_id",
            "Vessel Name",
            "Official Number",
            "Port of Registry",
            "Name",
            "Year of Birth",
            "Age",
            "Place of Birth",
            "Home Address",
            "Last Ship Name",
            "Last Ship Port",
            "Last Ship Leaving Date",
            "This Ship Joining Date",
            "This Ship Joining Port",
            "This Ship Capacity",
            "This Ship Leaving Date",
            "This Ship Leaving Port",
            "This Ship Leaving Cause",
            "Signed with Mark",
        )

        # Create Treeview with the above defined columns
        sel_mariner_tree = ttk.Treeview(newWindow, columns=columns, show="headings")

        # Defining headers for each column
        for column in columns:
            sel_mariner_tree.heading(column, text=column)

        # Triggers a function when an item is selected from the list
        # sel_name_tree.bind("<ButtonRelease-1>", tree_select)

        # Creating treeview object
        sel_mariner_tree.pack(side=RIGHT, expand=True, fill=BOTH)

        # Scrollbars
        scrollbar3 = Scrollbar(sel_mariner_tree, orient="horizontal")
        scrollbar3.pack(side=BOTTOM, fill=X)
        sel_mariner_tree.config(xscrollcommand=scrollbar3.set)
        scrollbar3.config(command=sel_mariner_tree.xview)

        # Inputting the mariner info into the new tree
        result = coll.find({"_id": {"$in": int_selected_ids}})

        values = []

        for doc in result:
            values = doc.values()
            values_list = list(values)

            sel_mariner_tree.insert("", "end", text=doc["_id"], values=(values_list))

    def tree_select_2(event):
        cur = sel_name_2_tree.focus()
        curItem = sel_name_2_tree.item(cur)

        # Splitting the values in the 'text' key otherwise the numbers were being iterated over per digit
        selected_ids = str(curItem["text"]).split()
        int_selected_ids = list(map(int, selected_ids))

        # Creating the new Window for the mariner detail to be displayed in
        newWindow = tk.Toplevel(window)
        newWindow.geometry("1280x720")

        # Creating the TreeView widget in which the selected mariner's details to be displayed in
        columns = (
            "_id",
            "Vessel Name",
            "Official Number",
            "Port of Registry",
            "Name",
            "Year of Birth",
            "Age",
            "Place of Birth",
            "Home Address",
            "Last Ship Name",
            "Last Ship Port",
            "Last Ship Leaving Date",
            "This Ship Joining Date",
            "This Ship Joining Port",
            "This Ship Capacity",
            "This Ship Leaving Date",
            "This Ship Leaving Port",
            "This Ship Leaving Cause",
            "Signed with Mark",
        )

        # Create Treeview with the above defined columns
        sel_mariner_tree = ttk.Treeview(newWindow, columns=columns, show="headings")

        # Defining headers for each column
        for column in columns:
            sel_mariner_tree.heading(column, text=column)

        # Triggers a function when an item is selected from the list
        # sel_name_tree.bind("<ButtonRelease-1>", tree_select)

        # Creating treeview object
        sel_mariner_tree.pack(side=RIGHT, expand=True, fill=BOTH)

        # Scrollbars
        scrollbar3 = Scrollbar(sel_mariner_tree, orient="horizontal")
        scrollbar3.pack(side=BOTTOM, fill=X)
        sel_mariner_tree.config(xscrollcommand=scrollbar3.set)
        scrollbar3.config(command=sel_mariner_tree.xview)

        # Inputting the mariner info into the new tree
        result = coll.find({"_id": {"$in": int_selected_ids}})

        values = []

        for doc in result:
            values = doc.values()
            values_list = list(values)

            sel_mariner_tree.insert("", "end", text=doc["_id"], values=(values_list))

    #### CREATING THE GUI

    # Create the root window
    window = Tk()
    # Define the window paramters
    window.geometry("1400x720")
    window.title("Mariners")

    # Frames for lists
    title_frame = tk.Frame(window)
    title_frame.pack(side=TOP)
    lists_frame = tk.Frame(window)
    lists_frame.pack(expand=TRUE, fill=BOTH)
    buttons_frame = tk.Frame(window)
    buttons_frame.pack(side=BOTTOM, fill=BOTH)

    # Define a label for the list
    lbl_title = Label(title_frame, text="Mariners", font=("Helvetica", 16, "bold"))
    lbl_desc = Label(
        title_frame,
        text="This is a list displaying all of the names of mariners found in the records. The count is the number of times this name appears in the records. Click on a name to narrow down your search for a particular mariner.",
        font=("Helvetica", 12),
        wraplength=300,
        justify="left",
    )
    lbl_title.pack(side=TOP, pady=(10, 0))
    lbl_desc.pack(side=TOP, pady=(0, 10))

    # Defining listbox object
    all_names_list = Listbox(lists_frame, font=("Helvetica", 12))
    # Triggers the list_select function when an item is selected from the list
    all_names_list.bind("<<ListboxSelect>>", list_select)
    # Creating listbox object
    all_names_list.pack(side=LEFT, expand=True, fill=BOTH)

    # Creating the TreeView widget in which the unique mariners by selected name will be stored in
    sel_name_tree = ttk.Treeview(lists_frame)
    sel_name_tree["columns"] = ("Unique IDs", "Name", "DOB", "Age", "Birthplace")
    sel_name_tree.column("#0", width=0)  # hiding this column
    sel_name_tree.column("#1", width=150)
    sel_name_tree.column("#2", width=100)
    sel_name_tree.column("#3", width=75)
    sel_name_tree.column("#4")

    # Defining headers for each column
    sel_name_tree.heading("#0", text="Unique IDs", anchor=tk.W)
    sel_name_tree.heading("#1", text="Name", anchor=tk.W)
    sel_name_tree.heading("#2", text="DOB", anchor=tk.W)
    sel_name_tree.heading("#3", text="Age", anchor=tk.W)
    sel_name_tree.heading("#4", text="Birthplace", anchor=tk.W)

    # Triggers a function when an item is selected from the list
    sel_name_tree.bind("<Double-1>", tree_select)
    # Creating treeview object
    sel_name_tree.pack(side=RIGHT, expand=True, fill=BOTH)

    # Creating the second Treeview for the second selected name (up to two trees may show at one time)
    sel_name_2_tree = ttk.Treeview(lists_frame)
    sel_name_2_tree["columns"] = ("Unique IDs", "Name", "DOB", "Age", "Birthplace")
    sel_name_2_tree.column("#0", width=0)  # hiding this column
    sel_name_2_tree.column("#1", width=150)
    sel_name_2_tree.column("#2", width=100)
    sel_name_2_tree.column("#3", width=75)
    sel_name_2_tree.column("#4")

    # Defining headers for each column
    sel_name_2_tree.heading("#0", text="Unique IDs", anchor=tk.W)
    sel_name_2_tree.heading("#1", text="Name", anchor=tk.W)
    sel_name_2_tree.heading("#2", text="DOB", anchor=tk.W)
    sel_name_2_tree.heading("#3", text="Age", anchor=tk.W)
    sel_name_2_tree.heading("#4", text="Birthplace", anchor=tk.W)

    # Triggers a function when an item is selected from the list
    sel_name_2_tree.bind("<Double-1>", tree_select_2)
    # Creating treeview object
    sel_name_2_tree.pack(side=RIGHT, expand=True, fill=BOTH)

    # Insert the mariners
    x = 1
    for mariner in the_mariners:
        all_names_list.insert(x, mariner["name"])
        x += 1

    # Create the scrollbars
    scrollbar1 = Scrollbar(all_names_list)
    scrollbar2 = Scrollbar(sel_name_tree)
    scrollbar3 = Scrollbar(sel_name_2_tree)
    scrollbar1.pack(side=RIGHT, fill=Y)
    scrollbar2.pack(side=RIGHT, fill=Y)
    scrollbar3.pack(side=RIGHT, fill=Y)

    # Attach the scrollbars
    all_names_list.config(yscrollcommand=scrollbar1.set)
    sel_name_tree.config(yscrollcommand=scrollbar2.set)
    sel_name_2_tree.config(yscrollcommand=scrollbar3.set)
    scrollbar1.config(command=all_names_list.yview)
    scrollbar2.config(command=sel_name_tree.yview)
    scrollbar3.config(command=sel_name_2_tree.yview)

    # Create button for showing rank proportions
    lbl_buttons = tk.Label(
        buttons_frame, text="Rank Distributions:", font=("Helvetica", 12, "bold")
    )
    btn_bar = tk.Button(
        buttons_frame,
        text="Top 20 Rank Distributions (Bar Chart)",
        wraplength=150,
        justify=CENTER,
        command=bar_chart,
    )
    btn_pie = tk.Button(
        buttons_frame,
        text="Top 20 Rank Distributions (Pie Chart)",
        wraplength=150,
        justify=CENTER,
        command=pie_chart,
    )
    lbl_buttons.pack(side=LEFT)
    btn_bar.pack(side=RIGHT)
    btn_pie.pack(side=tk.BOTTOM)

    # Creating button to view promotion track of 2 individuals
    btn_track_promotion = tk.Button(
        buttons_frame,
        text="Track Promotions",
        wraplength=150,
        justify=CENTER,
        command=two_selected,
    )
    btn_track_promotion.pack(side=LEFT)

    # Display until user exits
    window.mainloop()


###################################
###### RANK VISUALISATIONS ########
###################################


def proportion_ranks():

    query = [
        {
            "$group": {
                "_id": {
                    "name": "$name",
                    "age": "$age",
                    "DOB": "$year_of_birth",
                    "place_of_birth": "$place_of_birth",
                    "rank": "$this_ship_capacity",
                },  # groups documents  by these fields
                # "uniqueIds": {"$addToSet": "$_id"}, # adds to the uniqueIds array any unique _id found in this group
            }
        },
        {
            "$group": {
                "_id": "$_id.rank",
                "count": {
                    "$sum": 1
                },  # adds 1 to the total count for each document belonging to this name group
            }
        },
        # Sorting the order
        {"$sort": {"count": -1}},
        # Showing only the names and the count of each name
        {
            "$project": {
                "_id": True,
                "count": True,  # "rank": "$_id.rank", "name": "$_id.name" #"count": True "uniqueIds": True
            }
        },
    ]

    result = coll.aggregate(query)

    ranks = []
    counts = []
    for doc in result:
        ranks.append(doc["_id"])
        counts.append(doc["count"])

    return ranks, counts

    # ranks = list(map(lambda doc: doc['_id'], docs[:20]))
    # counts = list(map(lambda doc: doc['count'], docs[:20]))


def bar_chart():
    ranks, counts = proportion_ranks()

    plt.bar(ranks[:20], counts[:20])
    plt.title("Bar chart showing rank distribution of top 20 ranks.")
    plt.xlabel("Rank")
    plt.xticks(
        rotation=45, horizontalalignment="right", fontweight="light", fontsize="x-large"
    )
    plt.tight_layout()
    plt.ylabel("Count")
    plt.show()


def pie_chart():
    ranks, counts = proportion_ranks()

    plt.pie(
        counts[:20],
        labels=ranks[:20],
        startangle=90,
        autopct="%1.1f%%",
        pctdistance=1.0,
        rotatelabels=True,
    )
    plt.title("Pie chart showing rank distribution of the top 20 ranks.", loc="center")
    plt.legend(
        title="Ranks",
        bbox_to_anchor=(1, 0.5),
        loc="center right",
        fontsize=10,
        bbox_transform=plt.gcf().transFigure,
    )
    plt.show()


def two_selected():
    cur1 = sel_name_tree.focus()
    cur1Item = sel_name_tree.item(cur1)
    cur2 = sel_name_2_tree.focus()
    cur2Item = sel_name_2_tree.item(cur2)

    # Splitting the values in the 'text' key otherwise the numbers were being iterated over per digit
    selected_ids_1 = str(cur1Item["text"]).split()
    selected_ids_2 = str(cur2Item["text"]).split()

    # Converting IDs to ints
    int_selected_ids_1 = list(map(int, selected_ids_1))
    int_selected_ids_2 = list(map(int, selected_ids_2))

    result1 = coll.find({"_id": {"$in": int_selected_ids_1}})
    list1 = []
    for doc in result1:
        list1.append(doc)

    result2 = coll.find({"_id": {"$in": int_selected_ids_2}})
    list2 = []
    for doc in result2:
        list2.append(doc)

    def get_join_date(doc):
        joining_date = doc.get("this_ship_joining_date", "blk")
        if isinstance(joining_date, datetime.datetime) == True:
            return joining_date.strftime("%Y-%m-%d")
        if isinstance(joining_date, datetime.time) == True:
            return joining_date.strftime("%Y-%m-%d")
        else:
            return joining_date

    list1.sort(key=get_join_date)
    list2.sort(key=get_join_date)

    ranks_1 = []
    dates_1 = []
    ranks_2 = []
    dates_2 = []

    for doc in list1:
        dates_1.append(doc.get("this_ship_joining_date", "blk"))
        ranks_1.append(doc.get("this_ship_capacity", "blk"))

    for doc in list2:
        dates_2.append(doc.get("this_ship_joining_date", "blk"))
        ranks_2.append(doc.get("this_ship_capacity", "blk"))

    # Choose some nice levels
    # levels = np.tile([-7, 7, -5, 5, -3, 3, -1, 1], int(np.ceil(len(dates)/6)))[:len(dates)]

    plt.plot(dates_1, ranks_1)
    plt.plot(dates_2, ranks_2)
    plt.legend([list1[0]["name"], list2[0]["name"]])

    # cara = []
    # for d in dates:
    #   cara.append(1)

    # # Create figure and plot a stem plot with the date
    # fig, ax = plt.subplots()
    # ax.scatter(dates, cara)

    # # ax.scatter(dates, [1]*len(dates),marker='Mate', s=100)
    # ax.set(title="Promotion timeline")

    # for i, txt in enumerate(ranks):
    #   ax.annotate(txt, (dates[i], cara[i]))

    # ranks = []
    # dates = []
    # for doc in list2:
    #   dates.append(doc.get('this_ship_joining_date', 'blk'))
    #   ranks.append(doc.get('this_ship_capacity', 'blk'))

    # cara = []
    # for d in dates:
    #   cara.append(1.2)

    # ax.scatter(dates, cara)

    # for i, txt in enumerate(ranks):
    #   ax.annotate(txt, (dates[i], cara[i]))

    # ax.vlines(dates, 0, levels, color="tab:red")  # The vertical stems.
    # ax.plot(dates, np.zeros_like(dates), "-o", color="k", markerfacecolor="w")  # Baseline and markers on it.

    # # annotate lines
    # for d, l, r in zip(dates, levels, ranks):
    #   ax.annotate(r, xy=(d, l),
    #               horizontalalignment="right",
    #               verticalalignment="bottom" if l > 0 else "top",
    #               xytext=(-3, np.sign(l)*3), textcoords="offset points")

    # format xaxis with 4 month intervals
    # ax.xaxis.set_major_locator(mdates.MonthLocator(interval=4))
    # ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))
    # plt.setp(ax.get_xticklabels(), rotation=30, ha="right")

    # pprint(ax.get_yticklabels())
    # pprint(ax.get_xticklabels())

    # remove y axis and spines
    # ax.yaxis.set_visible(False)
    # ax.spines[["left", "top", "right"]].set_visible(False)
    # ax.xaxis.set_ticks_position('bottom')

    # ax.margins(y=0.1)

    # plt.plot(ranks)

    plt.show()

    # pprint(dates)
    # print("Hello")
    # pprint(ranks)


# Triggers the view_mariners function with the grouped mariner data which displays the GUI
view_mariners(grouped_mariners)
