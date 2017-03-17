from tkinter import *
from tkinter import ttk
from tkinter import filedialog
import pandas as pd
import os
import matplotlib.pyplot as plt
import seaborn as sns
sns.set_style('white')  # white, whitegrid, dark, darkgrid
sns.set_context('notebook')





def load():
    global data
    file = filedialog.askopenfile(parent=root, mode='rb', title='Choose your file')
    if file is not None:
        data = pd.read_excel(file)
        combo_x.config(values=data.columns.tolist())
        combo_x.set(data.columns[0])
        combo_y.config(values=data.columns.tolist())
        combo_y.set(data.columns[0])
        values_list = ['None'] + data.columns.tolist()
        combo_by.config(values=values_list)
        combo_by.set(values_list[0])
        types_list = ['histogram','scatter','bar','boxplot','violin','beeswarm']
        type_combo.config(values=types_list)
        type_combo.set(types_list[0])
def plot_us():
    fig, ax = plt.subplots(1, 1)
    by = var_by.get()
    if by == 'None':
        by = None

    plot_type = type_combo.get()
    if plot_type == 'histogram':
        print('hello')
    g = sns.distplot(data[var_x.get()], rug=True, rug_kws={'color': '#777777', 'alpha': 0.2},
                          hist_kws={'edgecolor': 'black', 'color': '#6899e8', 'label': 'розподіл'},
                          kde_kws={'color': 'black', 'alpha': 0.2, 'label': 'ядрова оцінка густини'})
    sns.despine(left=True, bottom=True)  # видалити осі повністю
    g.set_xlabel(var_x.get(), color='black', fontsize=15, alpha=0.5)
    g.set_ylabel('Густина', color='black', fontsize=15, alpha=0.5)
    plt.legend(loc='upper right')

    fig.savefig('Output/hist.pdf')
    plt.close(fig)
    os.startfile('Output\hist.pdf')
    return

    # if plot_type == 'scatter':
    #     a = sns.jointplot(var_x.get(), var_y.get(), data=data, kind='reg', color='#5394d6',
    #                       annot_kws={'fontsize': 14, 'loc': [-0.1, 0.85]},
    #                       marginal_kws={'rug': True, 'bins': 25, 'hist_kws': {'edgecolor': 'black'}},
    #                       joint_kws={'scatter_kws': {'alpha': 0.7}})
    #     plt.setp(a.ax_marg_x.patches, linewidth=1.0, color='#a9c8e8')
    #     plt.setp(a.ax_marg_y.patches, linewidth=1.0, color='#a9c8e8')
    #     a.ax_joint.set_xlabel(var_x.get(), fontsize=15, alpha=0.7)
    #     a.ax_joint.set_ylabel(var_y.get(), fontsize=15, alpha=0.7)
    #     plt.savefig('Output/scatter.pdf')
    #     plt.close()
    #     os.startfile('Output\scatter.pdf')
    #
    #     return
    #
    # if plot_type == 'bar':
    #
    #     ax = sns.barplot(x=var_x.get(), y=var_y.get(), hue=by, data=data, palette='Blues',
    #                      errcolor='0.4', errwidth=1.1)
    #     ax.set_ylabel('Середнє значення ' + var_y.get(), color='#666666')
    #     ax.set_xlabel(var_x.get(), color='#666666')
    #     plt.legend(loc=[0.8, 0.9])
    #     sns.despine()
    #     fig.savefig('Output/barplot.pdf')
    #     plt.close(fig)
    #     os.startfile('Output\\barplot.pdf')
    #     return
    #
    #
    # if plot_type == 'violin':
    #
    #     ax = sns.violinplot(var_x.get(), var_y.get(), data=data, hue=by, scale='count', split=True, palette='Blues')
    #     ax.set_ylabel(var_y.get(), color='#666666')
    #     ax.set_xlabel(var_x.get(), color='#666666')
    #     plt.legend(loc='upper right')
    #     sns.despine()
    #     plt.savefig('Output/violin.pdf')
    #     plt.close(fig)
    #     os.startfile('Output\\violin.pdf')
    #     return
    #
    #
    # if plot_type == 'beeswarm':
    #     ax = sns.swarmplot(var_x.get(), var_y.get(), data=data, hue=by, alpha=0.7)
    #
    #     mean_width = .5
    #
    #     for tick, text in zip(ax.get_xticks(), ax.get_xticklabels()):
    #         sample_name = text.get_text()
    #
    #         mean_val = data[data[var_x.get()] == sample_name][var_y.get()].mean()
    #
    #         ax.plot([tick - mean_width / 2, tick + mean_width / 2], [mean_val, mean_val], lw=2, color='#777777')
    #
    #     ax.set_ylabel(var_y.get(), color='#666666')
    #     ax.set_xlabel(var_x.get(), color='#666666')
    #     sns.despine()
    #     plt.savefig('Output/beeswarm.pdf')
    #     plt.close(fig)
    #     os.startfile('Output\\beeswarm.pdf')
    #     return



fig, ax = plt.subplots(1, 1)
data = None

root = Tk()

root.wm_title("Plotus")
ttk.Button(root, text="Load data", command=load).grid(row=0, column=0, columnspan=2)

type_value = StringVar()
ttk.Label(root, text='Choose plot type: ').grid(row=1, column=0)
type_combo = ttk.Combobox(root, textvariable=type_value)
type_combo.grid(row=1, column=1)

ttk.Label(root, text='Choose x-axis: ').grid(row=2, column=0)
var_x = StringVar()
combo_x = ttk.Combobox(root, textvariable=var_x)
combo_x.grid(row=2, column=1)


var_y = StringVar()
ttk.Label(root, text='Choose y-axis: ').grid(row=3, column=0)
combo_y = ttk.Combobox(root, textvariable=var_y)
combo_y.grid(row=3, column=1)


var_by = StringVar()
ttk.Label(root, text='Choose \'by\' factor: ').grid(row=4, column=0)
combo_by = ttk.Combobox(root, textvariable=var_by)
combo_by.grid(row=4, column=1)





ttk.Button(root, text='Plot!', command=plot_us).grid(row=5, column=0,columnspan=2)


root.mainloop()
