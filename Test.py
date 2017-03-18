from tkinter import *
from tkinter import ttk
from tkinter import filedialog
import pandas as pd
import os
import matplotlib.pyplot as plt
import seaborn as sns
import statsmodels.stats.multicomp as multi
from scipy.stats.mstats import normaltest


sns.set_style('white')  # white, whitegrid, dark, darkgrid
sns.set_context('notebook')

import statsmodels.api as sm
from statsmodels.formula.api import ols


if os.path.exists('Plots'):
    pass
else:
    os.makedirs('Plots/')

if os.path.exists('Analysis'):
    pass
else:
    os.makedirs('Analysis/')


def analyze_us():
    global data
    if data is None:
        return

    method = combo_analysis.get()
    if method == 'Descriptive stats':
        describe()
    elif method == 'Normality test':
        normality_test()
    elif method == 'ANOVA':
        anova_analysis()


def print_status(text, color):
    message.config(text=text, foreground=color)


def describe():
    global data

    writer = pd.ExcelWriter('Analysis/descriptive statistics.xlsx')
    desc_data = data.describe()
    desc_data.to_excel(writer)
    writer.save()
    os.startfile('Analysis\descriptive statistics.xlsx')


def normality_test():
    global data
    formula = var_formula.get()
    if formula == '':
        print_status('Warning: Please, specify column names in formula.', 'red')
        return
    x_list = formula.split('~')[0].split('+')
    y = None
    try:
        y = formula.split('~')[1]
    except:
        pass

    test_list = []
    p_value_list = []
    index_list = []

    for x in x_list:
        if x not in data.columns:
            print_status("Warning: No such continuous column.", 'red')
            return
        if y not in data.columns:
            print_status('Warning: No such categorical column.', 'red')
            return
        if y is None:
            test, p_value = normaltest(data[x])
            test_list.append(test)
            p_value_list.append(p_value)
            index_list.append(x)
        else:
            for i in set(data[y]):
                test, p_value = normaltest(data[data[y] == i][x])
                test_list.append(test)
                p_value_list.append(p_value)
                index_list.append(x + '[' + i + ']')

    df = pd.DataFrame({"D’Agostino and Pearson’s Normality Test": test_list, "p Value": p_value_list}, index=index_list)
    writer = pd.ExcelWriter('Analysis/Normality.xlsx')
    df.to_excel(writer, sheet_name='Sheet1', startcol=1)
    # df.to_excel(writer, sheet_name='Sheet1', startcol=7)
    writer.save()
    print_status('Status: Normality test performed', 'black')
    os.startfile('Analysis\\Normality.xlsx')


def anova_analysis():
    global data

    mc1 = multi.MultiComparison(data[var_formula.get().split('~')[0]], data[var_formula.get().split('~')[1]])
    result = mc1.tukeyhsd()
    t = result.summary().as_text()
    a_list = t.split('\n')
    cols = [col for col in a_list[2].split(' ') if col]
    df = pd.DataFrame(columns=cols)
    for i in range(4, len(a_list) - 1):

        items = [item for item in a_list[i].split(' ') if item]
        df.loc[i-4] = items

    formula = var_formula.get()
    mod = ols(formula, data=data).fit()

    # print(mod.summary())
    aov_table = sm.stats.anova_lm(mod, typ=2)
    writer = pd.ExcelWriter('Analysis/ANOVA.xlsx')
    caption = pd.DataFrame(columns=[var_formula.get().split('~')[0]])
    caption.to_excel(writer, sheet_name='Sheet1')
    aov_table.to_excel(writer, sheet_name='Sheet1', startcol=1)
    df.to_excel(writer, sheet_name='Sheet1', startcol=7)
    writer.save()
    os.startfile('Analysis\ANOVA.xlsx')


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
        types_list = ['Histogram', 'Scatter plot', 'Bar plot', 'Count bar', 'Boxplot', 'Violin plot', 'Beeswarm plot']
        type_combo.config(values=types_list)
        type_combo.set(types_list[0])
        analysis_types = ['None', 'Descriptive stats', 'Normality test', 'ANOVA']
        combo_analysis.config(values=analysis_types)
        combo_analysis.set(analysis_types[0])
        palettes = ['Blues', 'coolwarm', 'GnBu_d',  'pastel', 'Set1',
                    'summer', 'muted', 'Spectral', 'husl',  'copper', 'magma']
        combo_palette.config(values=palettes)
        combo_palette.set(palettes[0])

        for item in data.columns:
            # insert each new item to the end of the listbox
            listbox.insert('end', item)


def plot_us():
    fig, ax = plt.subplots(1, 1)
    by = var_by.get()
    if by == 'None':
        by = None

    plot_type = type_combo.get()
    if plot_type == 'Histogram':

        g = sns.distplot(data[var_x.get()], rug=True, rug_kws={'color': '#777777', 'alpha': 0.2},
                              hist_kws={'edgecolor': 'black', 'color': '#6899e8', 'label': 'розподіл'},
                              kde_kws={'color': 'black', 'alpha': 0.2, 'label': 'ядрова оцінка густини'})
        sns.despine(left=True, bottom=True)  # видалити осі повністю
        g.set_xlabel(var_x.get(), color='black', fontsize=15, alpha=0.5)
        g.set_ylabel('Густина', color='black', fontsize=15, alpha=0.5)
        plt.legend(loc='upper right')

        fig.savefig('Plots/hist.pdf')
        plt.close(fig)
        os.startfile('Plots\hist.pdf')
        return

    if plot_type == 'Scatter plot':
        a = sns.jointplot(var_x.get(), var_y.get(), data=data, kind='reg', color='#5394d6',
                          annot_kws={'fontsize': 14, 'loc': [-0.1, 0.85]},
                          marginal_kws={'rug': True, 'bins': 25, 'hist_kws': {'edgecolor': 'black'}},
                          joint_kws={'scatter_kws': {'alpha': 0.7}})
        plt.setp(a.ax_marg_x.patches, linewidth=1.0, color='#a9c8e8')
        plt.setp(a.ax_marg_y.patches, linewidth=1.0, color='#a9c8e8')
        a.ax_joint.set_xlabel(var_x.get(), fontsize=15, alpha=0.7)
        a.ax_joint.set_ylabel(var_y.get(), fontsize=15, alpha=0.7)
        plt.savefig('Plots/scatter.pdf')
        plt.close()
        os.startfile('Plots\scatter.pdf')

        return

    if plot_type == 'Bar plot':

        ax = sns.barplot(x=var_x.get(), y=var_y.get(), hue=by, data=data, palette=combo_palette.get(),
                         errcolor='0.4', errwidth=1.1)
        ax.set_ylabel('Середнє значення ' + var_y.get(), color='#666666')
        ax.set_xlabel(var_x.get(), color='#666666')
        plt.legend(loc=[0.8, 0.9])
        sns.despine()
        fig.savefig('Plots/barplot.pdf')
        plt.close(fig)
        os.startfile('Plots\\barplot.pdf')
        return

    if plot_type == 'Count bar':
        ax = sns.countplot(x=var_x.get(), hue=by, data=data, palette=combo_palette.get())
        ax.set_ylabel('Кількість', color='#666666')
        ax.set_xlabel(var_x.get(), color='#666666')
        plt.legend(loc=[0.8, 0.9])
        sns.despine()
        fig.savefig('Plots/countbar.pdf')
        plt.close(fig)
        os.startfile('Plots\\countbar.pdf')
        return

    if plot_type == 'Violin plot':

        ax = sns.violinplot(var_x.get(), var_y.get(), data=data, hue=by, scale='count', split=True, palette=combo_palette.get())
        ax.set_ylabel(var_y.get(), color='#666666')
        ax.set_xlabel(var_x.get(), color='#666666')
        plt.legend(loc='upper right')
        sns.despine()
        plt.savefig('Plots/violin.pdf')
        plt.close(fig)
        os.startfile('Plots\\violin.pdf')
        return

    if plot_type == 'Beeswarm plot':
        ax = sns.swarmplot(var_x.get(), var_y.get(), data=data, hue=by, alpha=0.7)

        mean_width = .5

        for tick, text in zip(ax.get_xticks(), ax.get_xticklabels()):
            sample_name = text.get_text()

            mean_val = data[data[var_x.get()] == sample_name][var_y.get()].mean()

            ax.plot([tick - mean_width / 2, tick + mean_width / 2], [mean_val, mean_val], lw=2, color='#777777')

        ax.set_ylabel(var_y.get(), color='#666666')
        ax.set_xlabel(var_x.get(), color='#666666')
        sns.despine()
        plt.savefig('Plots/beeswarm.pdf')
        plt.close(fig)
        os.startfile('Plots\\beeswarm.pdf')
        return


fig, ax = plt.subplots(1, 1)
data = None

root = Tk()
root.resizable(0,0)

root.wm_title("Plotus")
ttk.Button(root, text="Load data", command=load, width=40).grid(row=0, column=0, columnspan=3, pady=5, padx=5)

type_value = StringVar()
ttk.Label(root, text='Choose plot type: ').grid(row=1, column=0, sticky='W', padx=7)
type_combo = ttk.Combobox(root, textvariable=type_value)
type_combo.grid(row=1, column=1, padx=7)


ttk.Label(root, text='Choose x-axis: ').grid(row=2, column=0, sticky='W', padx=7)
var_x = StringVar()
combo_x = ttk.Combobox(root, textvariable=var_x)
combo_x.grid(row=2, column=1, padx=7)


var_y = StringVar()
ttk.Label(root, text='Choose y-axis: ').grid(row=3, column=0, sticky='W', padx=7)
combo_y = ttk.Combobox(root, textvariable=var_y)
combo_y.grid(row=3, column=1, padx=7)


var_by = StringVar()
ttk.Label(root, text='Choose \'by\' factor: ').grid(row=4, column=0, sticky='W', padx=7)
combo_by = ttk.Combobox(root, textvariable=var_by)
combo_by.grid(row=4, column=1, padx=7)

ttk.Label(root, text='Choose palette:').grid(row=5, column=0, sticky='W', padx=7)
var_palette = StringVar()
combo_palette = ttk.Combobox(root, textvariable=var_palette)
combo_palette.grid(row=5, column=1, padx=7)

ttk.Button(root, text='Plot', command=plot_us, width=40).grid(row=6, column=0, columnspan=3, padx=5, pady=5)

listbox = Listbox(root, width=15, height=5)
listbox.grid(row=7, column=0, rowspan=3, padx=5, pady=5)
# create a vertical scrollbar to the right of the listbox
yscroll = Scrollbar(command=listbox.yview, orient=VERTICAL)
yscroll.grid(row=7, column=0, rowspan=3, sticky='nse')
listbox.configure(yscrollcommand=yscroll.set)


def on_select(evt):
    w = evt.widget
    index = int(w.curselection()[0])
    value = w.get(index)
    var_formula.set(var_formula.get() + value)

listbox.bind('<<ListboxSelect>>', on_select)


def add_plus():
    var_formula.set(var_formula.get() + '+')

def add_tilda():
    var_formula.set(var_formula.get() + '~')

ttk.Button(root, text='+', command=add_plus, width=6).grid(row=10, column=0, padx=8, pady=5, columnspan=1, sticky='W')
ttk.Button(root, text='~', command=add_tilda, width=6).grid(row=10, column=0, padx=22, pady=5, columnspan=1, sticky='E')

analysis_label = ttk.Label(root, text="Choose analysis:")
analysis_label.grid(row=7, column=1, sticky='WS', padx=5)
analysis_label.config(font=('default', 8))
var_analysis = StringVar()
combo_analysis = ttk.Combobox(root, textvariable=var_analysis)
combo_analysis.grid(row=8, column=1, padx=7)

formula_label = ttk.Label(root, text='Write formula:')
formula_label.grid(row=9, column=1, sticky='WS', padx=5)
formula_label.config(font=('default', 8))
var_formula = StringVar()
formula_analysis = ttk.Entry(root, textvariable=var_formula, width=23)
formula_analysis.grid(row=10, column=1, padx=7)

analyze_button = ttk.Button(root, text='Analyze', command=analyze_us, width=40)
analyze_button.grid(row=11, column=0, columnspan=3, padx=5, pady=5)


message = ttk.Label(root, text='Status: Ready')
message.grid(row=12, column=0, columnspan=2, pady=2)
message.config(font=('default', 7))




root.mainloop()
