from tkinter import *
from tkinter import ttk
from tkinter import filedialog
import pandas as pd
import os
import matplotlib.pyplot as plt
import seaborn as sns
import statsmodels.stats.multicomp as multi

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
    elif method == 'ANOVA':
        anova_analysis()


def describe():
    global data

    writer = pd.ExcelWriter('Analysis/descriptive statistics.xlsx')
    desc_data = data.describe()
    desc_data.to_excel(writer)
    writer.save()
    os.startfile('Analysis\descriptive statistics.xlsx')


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
        analysis_types = ['None', 'Descriptive stats', 'ANOVA']
        combo_analysis.config(values=analysis_types)
        combo_analysis.set(analysis_types[0])
        palettes = ['Blues', 'coolwarm', 'GnBu_d',  'pastel', 'Set1',
                    'summer', 'muted', 'Spectral', 'husl',  'copper', 'magma']
        combo_palette.config(values=palettes)
        combo_palette.set(palettes[0])
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
ttk.Button(root, text="Load data", command=load, width=39).grid(row=0, column=0, columnspan=3)


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

ttk.Label(root, text='Choose palette:').grid(row=5, column=0)
var_palette = StringVar()
combo_palette = ttk.Combobox(root, textvariable=var_palette)
combo_palette.grid(row=5, column=1)

ttk.Button(root, text='Plot', command=plot_us, width=39).grid(row=6, column=0, columnspan=3)

ttk.Label(root, text="Choose analysis:").grid(row=7, column=0)
var_analysis = StringVar()
combo_analysis = ttk.Combobox(root, textvariable=var_analysis)
combo_analysis.grid(row=7, column=1)

ttk.Label(root, text='Write formula x~y').grid(row=8, column=0)
var_formula = StringVar()
formula_analysis = ttk.Entry(root, textvariable=var_formula, width=23)
formula_analysis.grid(row=8, column=1)

ttk.Button(root, text='Analyze', command=analyze_us, width=39).grid(row=9, column=0, columnspan=3)





root.mainloop()
