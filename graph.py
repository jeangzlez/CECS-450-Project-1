import pandas as pd #handles csv reading
import matplotlib.pyplot as plt
import numpy as np #organizes lists of numbers
from matplotlib.widgets import Button, CheckButtons
from matplotlib.patches import Rectangle, Patch
#import matplotlib.patheffects as path_effects


data_frame = pd.read_csv("accident.csv")

filtered_data_frame = data_frame[(data_frame.iloc[:, 1] == 'California') & (data_frame.iloc[:, 11] == 'LOS ANGELES (37)')]

highway_column_index = 25 #CHANGE THESE IF CVS INDEX CHANGES
time_column_index = 21
day_column_index = 19
allowed_highways = ['I-5', 'I-10', 'I-405', 'US-101', 'I-110', 'I-105', 'I-605', 'I-710'] #WHITELIST

#filters based on the allowed highways
filtered_data_frame = filtered_data_frame[filtered_data_frame.iloc[:, highway_column_index].isin(allowed_highways)]


def categorize_time(hour):
    if 0 <= hour <= 11:
        return 'Morning'
    elif 12 <= hour <= 17:
        return 'Afternoon'
    else:
        return 'Evening'


#string to numbers
filtered_data_frame['Hour'] = pd.to_numeric(filtered_data_frame.iloc[:, time_column_index], errors='coerce')
filtered_data_frame['TimeCategory'] = filtered_data_frame['Hour'].apply(categorize_time)

#order of days
day_order_list = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
days_present = [day for day in day_order_list if day in filtered_data_frame.iloc[:, day_column_index].unique()]
number_of_days = len(days_present)

time_categories = ['Morning', 'Afternoon', 'Evening']
time_ranges = ['(12am-11am)', '(12pm-5pm)', '(6pm-11pm)']
category_colors = ['skyblue', 'yellow', 'orange']
bar_width_value = 0.2

#calculates accidents
all_day_counts = {}
maximum_accident_count = 0

for day in days_present:
    day_data_frame = filtered_data_frame[filtered_data_frame.iloc[:, day_column_index] == day] #index check
    counts_table = day_data_frame.groupby([day_data_frame.iloc[:, highway_column_index], 'TimeCategory']).size().unstack(fill_value=0)
    counts_table = counts_table.reindex(index=allowed_highways, fill_value=0) #filter
    counts_table = counts_table.reindex(columns=time_categories, fill_value=0) #filter
    all_day_counts[day] = counts_table
    maximum_accident_count = max(maximum_accident_count, counts_table.values.max())


#most dangerous calculation
def calculate_most_dangerous_combinations(selected_days):
    overall_totals = {}
    for highway in allowed_highways:
        for time_category in time_categories:
            total_accidents = sum(all_day_counts[day].loc[highway, time_category] for day in selected_days)
            overall_totals[(highway, time_category)] = total_accidents

    if not overall_totals:  #return nothing if nothing selected
        return [], 0

    maximum_total_value = max(overall_totals.values())
    most_dangerous_combinations = [combo for combo, value in overall_totals.items() if value == maximum_total_value]

    return most_dangerous_combinations, maximum_total_value


#variables of most dangerous with all days
most_dangerous_combinations, maximum_total_value = calculate_most_dangerous_combinations(days_present)


#plot setup
figure, axis = plt.subplots(figsize=(12, 7))
plt.subplots_adjust(bottom=0.3)

#remove any previous placements
clean_highway_names = [highway.replace('/', '') for highway in allowed_highways]
x_positions = np.arange(len(allowed_highways))
current_day_index = 0

#default settings buttons
button_next_day = None
button_expand_view = None
button_collapse_view = None
checkbox_days = None

#defeault settings tooltips
tooltip_rectangle = None
tooltip_text_elements = None

#filters for checkboxes
selected_days_for_tooltip = {day: True for day in days_present}

#remembers highlighted/selected bar
highlighted_combination = None
original_bar_colors = {}  #remembers original color
bar_groups = None
all_bar_groups = {}  #remembers original color for all days

#default settings
hover_cid = None
click_cid = None
expanded_click_cid = None


def plot_day(day):
    """Draw bars for one day without red coloration."""
    global tooltip_rectangle, tooltip_text_elements, bar_groups, original_bar_colors, all_bar_groups, hover_cid, click_cid

    #clear old tooltip
    if tooltip_rectangle:
        tooltip_rectangle.remove()
        tooltip_rectangle = None
    if tooltip_text_elements:
        for text_element in tooltip_text_elements:
            text_element.remove()
        tooltip_text_elements = None

    axis.clear()
    day_counts = all_day_counts[day]
    bar_groups = []
    original_bar_colors = {}

    #bars for morning/afternoon/evening
    for category_index, time_category in enumerate(time_categories):
        bar_group = axis.bar(x_positions + category_index * bar_width_value, day_counts[time_category],
                             width=bar_width_value,
                             label=f'{time_category} {time_ranges[category_index]}',
                             color=category_colors[category_index])
        bar_groups.append(bar_group)

        #remember original colors for each bar
        for i, bar in enumerate(bar_group):
            original_bar_colors[(i, category_index)] = category_colors[category_index]

    #remember bar groups for this day
    all_bar_groups[day] = bar_groups

    axis.set_xticks(x_positions + bar_width_value)
    axis.set_xticklabels(clean_highway_names, rotation=45)
    axis.set_ylim(0, maximum_accident_count + 1)
    axis.set_xlabel("Highway (Los Angeles)")
    axis.set_ylabel("Number of Accidents (2023)")
    axis.set_title(f"{day}")

    #highlights bars if name and time is true
    if highlighted_combination:
        highway_name, time_category = highlighted_combination
        highlight_combination(highway_name, time_category)

    #key legend
    legend_elements = [
        Patch(color=category_colors[0], label=f'Morning {time_ranges[0]}'),
        Patch(color=category_colors[1], label=f'Afternoon {time_ranges[1]}'),
        Patch(color=category_colors[2], label=f'Evening {time_ranges[2]}'),
        Patch(color='purple', label='Left Click Highlight')
    ]
    axis.legend(handles=legend_elements, title="Time of Day")

    #remove old
    if hover_cid:
        figure.canvas.mpl_disconnect(hover_cid)
    if click_cid:
        figure.canvas.mpl_disconnect(click_cid)


    hover_cid = figure.canvas.mpl_connect('motion_notify_event', lambda event: on_hover(event, bar_groups, day))
    click_cid = figure.canvas.mpl_connect('button_press_event', lambda event: on_click(event, bar_groups, day))
    figure.canvas.draw_idle()


#highlight bars across all days
def highlight_combination(highway_name, time_category):
    if highway_name not in allowed_highways or time_category not in time_categories:
        return

    highway_index = allowed_highways.index(highway_name)
    time_index = time_categories.index(time_category)

    for day, day_bar_groups in all_bar_groups.items():
        if day_bar_groups and len(day_bar_groups) > time_index and len(day_bar_groups[time_index]) > highway_index:
            day_bar_groups[time_index][highway_index].set_color('purple')

    figure.canvas.draw_idle()


#restore bars across all days
def restore_combination(highway_name, time_category):
    if highway_name not in allowed_highways or time_category not in time_categories:
        return

    highway_index = allowed_highways.index(highway_name)
    time_index = time_categories.index(time_category)

    for day, day_bar_groups in all_bar_groups.items():
        if day_bar_groups and len(day_bar_groups) > time_index and len(day_bar_groups[time_index]) > highway_index:
            original_color = category_colors[time_index]
            day_bar_groups[time_index][highway_index].set_color(original_color)

    figure.canvas.draw_idle()


#left click bars
def on_click(event, bar_groups, current_day):
    global highlighted_combination

    if event.inaxes != axis or event.button != 1:  #left clicks
        return

    for category_index, bar_group in enumerate(bar_groups):
        for highway_index, bar in enumerate(bar_group):
            if bar.contains(event)[0]:
                highway_name = allowed_highways[highway_index]
                time_category = time_categories[category_index]
                combination = (highway_name, time_category)

                #unhighlight if already clicked
                if highlighted_combination == combination:
                    restore_combination(highway_name, time_category)
                    highlighted_combination = None
                else:
                    #restore if highlighted already
                    if highlighted_combination:
                        old_highway, old_time = highlighted_combination
                        restore_combination(old_highway, old_time)

                    #highlights all days
                    highlight_combination(highway_name, time_category)
                    highlighted_combination = combination

                return


#tooltip on hover
def on_hover(event, bar_groups, current_day):
    global tooltip_rectangle, tooltip_text_elements, most_dangerous_combinations

    if event.inaxes != axis:
        if tooltip_rectangle:
            tooltip_rectangle.remove()
            tooltip_rectangle = None
        if tooltip_text_elements:
            for text_element in tooltip_text_elements:
                text_element.remove()
            tooltip_text_elements = None
        figure.canvas.draw_idle()
        return

    for category_index, bar_group in enumerate(bar_groups):
        for highway_index, bar in enumerate(bar_group):
            if bar.contains(event)[0]:
                if tooltip_rectangle:
                    tooltip_rectangle.remove()
                    tooltip_rectangle = None
                if tooltip_text_elements:
                    for text_element in tooltip_text_elements:
                        text_element.remove()
                    tooltip_text_elements = None

                highway_name = clean_highway_names[highway_index]
                original_highway_name = allowed_highways[highway_index]
                time_category = time_categories[category_index]

                #currently selected days for tooltip
                selected_days = [day for day in days_present if selected_days_for_tooltip[day]]

                #calculate most dangerous based on current filter
                most_dangerous_combinations, current_max_total = calculate_most_dangerous_combinations(selected_days)

                tooltip_x = event.xdata + 0.5
                tooltip_y = event.ydata

                x_limits = axis.get_xlim()
                y_limits = axis.get_ylim()
                number_of_selected_days = len(selected_days)
                tooltip_width_value = 2
                tooltip_height_value = (number_of_selected_days + 1) * 0.15 + 0.3

                if tooltip_x + tooltip_width_value > x_limits[1]:
                    tooltip_x = event.xdata - tooltip_width_value - 0.2
                if tooltip_y + tooltip_height_value > y_limits[1]:
                    tooltip_y = y_limits[1] - tooltip_height_value - 0.1

                tooltip_rectangle = Rectangle((tooltip_x, tooltip_y), tooltip_width_value, tooltip_height_value, facecolor='white', edgecolor='black', alpha=0.95, zorder=100)
                axis.add_patch(tooltip_rectangle)

                tooltip_text_elements = []

                #check if most dangerous based on current filter
                is_most_dangerous = (original_highway_name, time_category) in most_dangerous_combinations

                #red color and (Most Dangerous)
                title_text = f"{highway_name} - {time_category}"
                if is_most_dangerous:
                    title_text += f" (Dangerous)"

                title_element = axis.text(
                    tooltip_x + tooltip_width_value / 2, tooltip_y + tooltip_height_value - 0.15,
                    title_text,
                    ha='center', va='top', fontweight='bold', fontsize=9, zorder=101,
                    color='red' if is_most_dangerous else 'black'
                )
                tooltip_text_elements.append(title_element)

                y_position = tooltip_y + tooltip_height_value - 0.35
                day_text_index = 0
                total_accidents_value = 0

                for day_name in days_present:
                    if selected_days_for_tooltip[day_name]:
                        day_counts = all_day_counts[day_name]
                        value = int(day_counts.loc[original_highway_name, time_category])
                        total_accidents_value += value

                        weight_value = 'bold' if day_name == current_day else 'normal'
                        color_value = 'green' if day_name == current_day else 'black'

                        day_text_element = axis.text(
                            tooltip_x + 0.1, y_position - day_text_index * 0.15,
                            f"{day_name}: {value}", ha='left', va='center',
                            fontsize=8, fontweight=weight_value, color=color_value, zorder=101
                        )
                        tooltip_text_elements.append(day_text_element)
                        day_text_index += 1

                total_text_element = axis.text(
                    tooltip_x + 0.1, y_position - day_text_index * 0.15,
                    f"Total: {total_accidents_value}", ha='left', va='center',
                    fontsize=8, fontweight='bold', color='blue', zorder=101
                )
                tooltip_text_elements.append(total_text_element)

                figure.canvas.draw_idle()
                return

    if tooltip_rectangle:
        tooltip_rectangle.remove()
        tooltip_rectangle = None
    if tooltip_text_elements:
        for text_element in tooltip_text_elements:
            text_element.remove()
        tooltip_text_elements = None
    figure.canvas.draw_idle()


def checkbox_changed(day_label):
    selected_days_for_tooltip[day_label] = not selected_days_for_tooltip[day_label]
    plot_day(days_present[current_day_index])


def expand_all(event):
    global button_collapse_view, tooltip_rectangle, tooltip_text_elements, checkbox_days, highlighted_combination, all_bar_groups, hover_cid, click_cid, expanded_click_cid, button_next_day, button_expand_view

    #clear ui
    if tooltip_rectangle:
        tooltip_rectangle.remove()
        tooltip_rectangle = None
    if tooltip_text_elements:
        for text_element in tooltip_text_elements:
            text_element.remove()
        tooltip_text_elements = None

    #clear buttons
    if button_next_day:
        button_next_day.ax.remove()
        button_next_day = None
    if button_expand_view:
        button_expand_view.ax.remove()
        button_expand_view = None
    if checkbox_days:
        try:
            checkbox_days.disconnect_events()
            checkbox_days.ax.remove()
        except:
            pass
        checkbox_days = None

    #clear old
    if hover_cid:
        figure.canvas.mpl_disconnect(hover_cid)
        hover_cid = None
    if click_cid:
        figure.canvas.mpl_disconnect(click_cid)
        click_cid = None
    if expanded_click_cid:
        figure.canvas.mpl_disconnect(expanded_click_cid)
        expanded_click_cid = None

    figure.clear()

    all_bar_groups = {}

    #creates the multiple graphs for expanded
    rows = (number_of_days + 2) // 3
    columns = min(3, number_of_days)

    axes_array = figure.subplots(rows, columns, squeeze=False)
    axes_array = axes_array.flatten()

    #adjusts layout for the collapse button
    plt.subplots_adjust(bottom=0.15, top=0.9, left=0.1, right=0.9, hspace=1, wspace=0.4)

    for index, day in enumerate(days_present):
        if index < len(axes_array):
            day_counts = all_day_counts[day]
            current_axis = axes_array[index]
            day_bar_groups = []

            for category_index, time_category in enumerate(time_categories):
                bar_group = current_axis.bar(np.arange(len(allowed_highways)) + category_index * bar_width_value,
                                             day_counts[time_category],
                                             width=bar_width_value, color=category_colors[category_index])
                day_bar_groups.append(bar_group)

            all_bar_groups[day] = day_bar_groups

            current_axis.set_xticks(np.arange(len(allowed_highways)) + bar_width_value)
            current_axis.set_xticklabels(clean_highway_names, rotation=45)
            current_axis.set_ylim(0, maximum_accident_count + 1)
            current_axis.set_title(day, fontsize=12, pad=15)

            #applys selected bar highlight color
            if highlighted_combination:
                highway_name, time_category = highlighted_combination
                highway_index = allowed_highways.index(highway_name)
                time_index = time_categories.index(time_category)
                if (day_bar_groups and len(day_bar_groups) > time_index and
                        len(day_bar_groups[time_index]) > highway_index):
                    day_bar_groups[time_index][highway_index].set_color('purple')

    #clear old
    for j in range(len(days_present), len(axes_array)):
        figure.delaxes(axes_array[j])

    #legend for expanded
    legend_axis = figure.add_axes([.6, .15, 0.3, 0.15])
    legend_axis.axis('off')
    legend_elements = [
        Patch(color=category_colors[0], label=f'Morning {time_ranges[0]}'),
        Patch(color=category_colors[1], label=f'Afternoon {time_ranges[1]}'),
        Patch(color=category_colors[2], label=f'Evening {time_ranges[2]}'),
        Patch(color='purple', label='Left Click Highlight')
    ]
    legend_axis.legend(handles=legend_elements, title="Time of Day", loc='center', frameon=True, ncol=2)

    #click for expanded view to remove highlighting
    def on_expanded_click(event):
        global highlighted_combination
        if (button_collapse_view and event.inaxes == button_collapse_view.ax) or \
                (event.inaxes == legend_axis):
            return

        if event.button != 1:  #left click
            return

        if highlighted_combination:
            highway_name, time_category = highlighted_combination
            restore_combination(highway_name, time_category)
            highlighted_combination = None

            expand_all(event)

    expanded_click_cid = figure.canvas.mpl_connect('button_press_event', on_expanded_click)

    #collapse button
    collapse_axis = plt.axes([0.7, 0.02, 0.2, 0.05])
    button_collapse_view = Button(collapse_axis, "Collapse")
    button_collapse_view.on_clicked(collapse_view)

    figure.canvas.draw_idle()


#collapse button to single day
def collapse_view(event):
    global button_next_day, button_expand_view, current_day_index, button_collapse_view, tooltip_rectangle, tooltip_text_elements, checkbox_days, highlighted_combination, all_bar_groups, hover_cid, click_cid, expanded_click_cid

    #clear old
    if expanded_click_cid:
        figure.canvas.mpl_disconnect(expanded_click_cid)
        expanded_click_cid = None

    figure.clear()

    #reset all to default
    tooltip_rectangle = None
    tooltip_text_elements = None
    button_collapse_view = None
    all_bar_groups = {}

    #switch to main single graph
    global axis
    axis = figure.add_subplot(111)
    plt.subplots_adjust(bottom=0.3)

    plot_day(days_present[current_day_index])

    #checkboxes
    checkbox_axis = plt.axes([0.1, 0.02, 0.5, 0.15])
    checkbox_axis.axis('off')
    checkbox_days = CheckButtons(checkbox_axis, days_present, [selected_days_for_tooltip[day] for day in days_present])
    checkbox_days.on_clicked(checkbox_changed)

    title_axis = plt.axes([.17, 0.17, 0.2, 0.05])
    title_axis.axis('off')
    title_axis.text(0, 0.5, "Filters:", fontsize=10, va='center')

    next_axis = plt.axes([0.7, 0.05, 0.1, 0.05])
    expand_axis = plt.axes([0.81, 0.05, 0.1, 0.05])
    button_next_day = Button(next_axis, "Next")
    button_expand_view = Button(expand_axis, "Expand")
    button_next_day.on_clicked(next_day)
    button_expand_view.on_clicked(expand_all)

    figure.canvas.draw_idle()



def next_day(event):
    global current_day_index, highlighted_combination
    current_day_index = (current_day_index + 1) % number_of_days
    plot_day(days_present[current_day_index])


#show Monday always setting
plot_day(days_present[current_day_index])

#buttons setup
next_axis = plt.axes([0.7, 0.05, 0.1, 0.05])
expand_axis = plt.axes([0.81, 0.05, 0.1, 0.05])
button_next_day = Button(next_axis, "Next")
button_expand_view = Button(expand_axis, "Expand")
button_next_day.on_clicked(next_day)
button_expand_view.on_clicked(expand_all)

#checkboxes setup
checkbox_axis = plt.axes([0.1, 0.02, 0.5, 0.15])
checkbox_axis.axis('off')
checkbox_days = CheckButtons(checkbox_axis, days_present, [selected_days_for_tooltip[day] for day in days_present])
checkbox_days.on_clicked(checkbox_changed)

title_axis = plt.axes([.17, 0.17, 0.2, 0.05])
title_axis.axis('off')
title_axis.text(0, 0.5, "Filters:", fontsize=10, va='center')

plt.show()

#prints the total counts of accidents
"""
data_frame = pd.read_csv("accident.csv")

los_angeles_data = data_frame[
    (data_frame.iloc[:, 1] == 'California') &
    (data_frame.iloc[:, 11] == 'LOS ANGELES (37)')
]

highways_of_interest = ['I-5', 'I-10', 'I-405', 'US-101', 'I-110', 'I-105', 'I-605', 'I-710']
highway_column_index = 25

highway_counts = {}
for highway in highways_of_interest:
    count = len(los_angeles_data[los_angeles_data.iloc[:, highway_column_index] == highway])
    highway_counts[highway] = count

print("Number of accidents in Los Angeles for each highway:")
print("-" * 50)
total_accidents = 0
for highway, count in highway_counts.items():
    print(f"{highway}: {count} accidents")
    total_accidents += count

print("-" * 50)
print(f"Total accidents across all highways: {total_accidents}")
print(f"Total records in Los Angeles: {len(los_angeles_data)}")"""