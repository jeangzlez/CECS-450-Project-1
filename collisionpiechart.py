from matplotlib import pyplot as plt
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np

# Creating datasets
collisionsI10 = ['Curb', 'Impact Attenuator/Crash Cushion', 'Motor Vehicle In-Transport',
                 'Pedestrian', 'Guardrail Face', 'Bridge Pier or Support']
dataI10 = [3, 2, 10, 6, 1, 1]

collisionsI105 = ['Motor Vehicle In-Transport', 'Parked Motor Vehicle',
                 'Pedestrian', 'Guardrail Face']
dataI105 = [1, 3, 1, 1]

collisionsI110 = ['Curb', 'Impact Attenuator/Crash Cushion', 'Motor Vehicle In-Transport',
                 'Pedestrian', 'Post, Pole or Other Supports']
dataI110 = [2, 1, 1, 3, 1]

collisionsI405 = ['Concrete Traffic Barrier', 'Motor Vehicle In-Transport', 'Parked Motor Vehicle',
                 'Pedalcyclist', 'Pedestrian', 'Curb']
dataI405 = [4, 7, 1, 1, 5, 1]

collisionsI5 = ['Curb', 'Guardrail Face', 'Motor Vehicle In-Transport',
                'Parked Motor Vehicle', 'Pedestrian', 'Post, Pole or Other Supports',
                'Rollover/Overturn', 'Guardrail End', 'Concrete Traffic Barrier',
                'Embankment', 'Impact Attenuator/Crash Cushion']
dataI5 = [1, 1, 9, 2, 7, 1, 1, 1, 2, 1, 1]

collisionsI605 = ['Motor Vehicle In-Transport', 'Pedestrian', 'Unknown Object Not Fixed',
                  'Rollover/Overturn', 'Tree (Standing Only)']
dataI605 = [3, 2, 1, 1, 1]

collisionsI710 = ['Curb', 'Motor Vehicle In-Transport', 'Other Fixed Object',
                  'Traffic Sign Support', 'Guardrail Face']
dataI710 = [3, 2, 2, 1, 1]

collisionsUS101 = ['Motor Vehicle In-Transport', 'Pedestrian', 'Traffic Sign Support', 'Tree (Standing Only)',
                  'Working Motor Vehicle', 'Concrete Traffic Barrier', 'Curb']
dataUS101 = [6, 9, 1, 1, 1, 1, 2]

# Create Matplotlib figure with 8 subplots (4 rows, 2 columns)
fig, axes = plt.subplots(4, 2, figsize=(12, 14))

# Plot 1: I-10
wedges1, texts1, autotexts1 = axes[0, 0].pie(dataI10, autopct='%1.1f%%', textprops={'fontsize': 7})
axes[0, 0].legend(wedges1, collisionsI10, loc="upper left", bbox_to_anchor=(1, 0, 0.5, 1), fontsize=7)
axes[0, 0].set_title('I-10', fontsize=11, weight='bold')

# Plot 2: I-105
wedges2, texts2, autotexts2 = axes[0, 1].pie(dataI105, autopct='%1.1f%%', textprops={'fontsize': 7})
axes[0, 1].legend(wedges2, collisionsI105, loc="upper left", bbox_to_anchor=(1, 0, 0.5, 1), fontsize=7)
axes[0, 1].set_title('I-105', fontsize=11, weight='bold')

# Plot 3: I-110
wedges3, texts3, autotexts3 = axes[1, 0].pie(dataI110, autopct='%1.1f%%', textprops={'fontsize': 7})
axes[1, 0].legend(wedges3, collisionsI110, loc="upper left", bbox_to_anchor=(1, 0, 0.5, 1), fontsize=7)
axes[1, 0].set_title('I-110', fontsize=11, weight='bold')

# Plot 4: I-405
wedges4, texts4, autotexts4 = axes[1, 1].pie(dataI405, autopct='%1.1f%%', textprops={'fontsize': 7})
axes[1, 1].legend(wedges4, collisionsI405, loc="upper left", bbox_to_anchor=(1, 0, 0.5, 1), fontsize=7)
axes[1, 1].set_title('I-405', fontsize=11, weight='bold')

# Plot 5: I-5
wedges5, texts5, autotexts5 = axes[2, 0].pie(dataI5, autopct='%1.1f%%', textprops={'fontsize': 7})
axes[2, 0].legend(wedges5, collisionsI5, loc="upper left", bbox_to_anchor=(1, 0, 0.5, 1), fontsize=7)
axes[2, 0].set_title('I-5', fontsize=11, weight='bold')

# Plot 6: I-605
wedges6, texts6, autotexts6 = axes[2, 1].pie(dataI605, autopct='%1.1f%%', textprops={'fontsize': 7})
axes[2, 1].legend(wedges6, collisionsI605, loc="upper left", bbox_to_anchor=(1, 0, 0.5, 1), fontsize=7)
axes[2, 1].set_title('I-605', fontsize=11, weight='bold')

# Plot 7: I-710
wedges7, texts7, autotexts7 = axes[3, 0].pie(dataI710, autopct='%1.1f%%', textprops={'fontsize': 7})
axes[3, 0].legend(wedges7, collisionsI710, loc="upper left", bbox_to_anchor=(1, 0, 0.5, 1), fontsize=7)
axes[3, 0].set_title('I-710', fontsize=11, weight='bold')

# Plot 8: US-101
wedges8, texts8, autotexts8 = axes[3, 1].pie(dataUS101, autopct='%1.1f%%', textprops={'fontsize': 7})
axes[3, 1].legend(wedges8, collisionsUS101, loc="upper left", bbox_to_anchor=(1, 0, 0.5, 1), fontsize=7)
axes[3, 1].set_title('US-101', fontsize=11, weight='bold')

# Add overall title
fig.suptitle('Highway Collision Types by Route', fontsize=14, weight='bold')

# Show matplotlib plot
plt.tight_layout()
plt.show()

# Create interactive Plotly figure with subplots
fig_plotly = make_subplots(
    rows=4, cols=2,
    specs=[[{'type':'domain'}, {'type':'domain'}],
           [{'type':'domain'}, {'type':'domain'}],
           [{'type':'domain'}, {'type':'domain'}],
           [{'type':'domain'}, {'type':'domain'}]],
    subplot_titles=('I-10', 'I-105', 'I-110', 'I-405', 'I-5', 'I-605', 'I-710', 'US-101')
)

# Add pie charts with interactive tooltips and hover effects
fig_plotly.add_trace(go.Pie(
    labels=collisionsI10, values=dataI10,
    hovertemplate="<b>%{label}</b><br>Count: %{value}<br>Percent: %{percent}<extra></extra>",
    marker=dict(line=dict(color='white', width=2)),
    pull=[0.05]*len(dataI10),
    name='I-10'), row=1, col=1)

fig_plotly.add_trace(go.Pie(
    labels=collisionsI105, values=dataI105,
    hovertemplate="<b>%{label}</b><br>Count: %{value}<br>Percent: %{percent}<extra></extra>",
    marker=dict(line=dict(color='white', width=2)),
    pull=[0.05]*len(dataI105),
    name='I-105'), row=1, col=2)

fig_plotly.add_trace(go.Pie(
    labels=collisionsI110, values=dataI110,
    hovertemplate="<b>%{label}</b><br>Count: %{value}<br>Percent: %{percent}<extra></extra>",
    marker=dict(line=dict(color='white', width=2)),
    pull=[0.05]*len(dataI110),
    name='I-110'), row=2, col=1)

fig_plotly.add_trace(go.Pie(
    labels=collisionsI405, values=dataI405,
    hovertemplate="<b>%{label}</b><br>Count: %{value}<br>Percent: %{percent}<extra></extra>",
    marker=dict(line=dict(color='white', width=2)),
    pull=[0.05]*len(dataI405),
    name='I-405'), row=2, col=2)

fig_plotly.add_trace(go.Pie(
    labels=collisionsI5, values=dataI5,
    hovertemplate="<b>%{label}</b><br>Count: %{value}<br>Percent: %{percent}<extra></extra>",
    marker=dict(line=dict(color='white', width=2)),
    pull=[0.05]*len(dataI5),
    name='I-5'), row=3, col=1)

fig_plotly.add_trace(go.Pie(
    labels=collisionsI605, values=dataI605,
    hovertemplate="<b>%{label}</b><br>Count: %{value}<br>Percent: %{percent}<extra></extra>",
    marker=dict(line=dict(color='white', width=2)),
    pull=[0.05]*len(dataI605),
    name='I-605'), row=3, col=2)

fig_plotly.add_trace(go.Pie(
    labels=collisionsI710, values=dataI710,
    hovertemplate="<b>%{label}</b><br>Count: %{value}<br>Percent: %{percent}<extra></extra>",
    marker=dict(line=dict(color='white', width=2)),
    pull=[0.05]*len(dataI710),
    name='I-710'), row=4, col=1)

fig_plotly.add_trace(go.Pie(
    labels=collisionsUS101, values=dataUS101,
    hovertemplate="<b>%{label}</b><br>Count: %{value}<br>Percent: %{percent}<extra></extra>",
    marker=dict(line=dict(color='white', width=2)),
    pull=[0.05]*len(dataUS101),
    name='US-101'), row=4, col=2)

# Update layout
fig_plotly.update_layout(
    title_text="Interactive Highway Collision Types by Route",
    showlegend=True,
    height=1200
)

fig_plotly.show()
