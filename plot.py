import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt


def main():
    sample = readcsv(sys.path[0] + '/bike_data.csv')
    lineplot(sample)
    barplot(sample)
    freqplot(sample)


def readcsv(filename):
    """
    read the csv file with the given file name
    add the year column to the data
    return the dataframe of the csv file
    """
    df = pd.read_csv(filename)
    df["year"] = pd.to_datetime(df["starttime"]).dt.year
    return df


def lineplot(data):
    """
    take in a dataframe
    draw line plots and save the fiugre as lineplots.png
    """
    sample = data
    sns.set_style('darkgrid', {"xtick.major.size": 20, "ytick.major.size": 20})
    plt.tight_layout()
    with sns.plotting_context(rc={"legend.fontsize": 17}):

        linefig, ax = plt.subplots(2, figsize=(8, 11))
        # plot the average trip duration of different years
        # showing the difference between genders
        years_gender = sample.groupby(["year", "gender"])["tripduration"]\
            .mean()
        years_gender = years_gender.reset_index()
        sns.lineplot(x="year", y="tripduration", hue="gender", legend="brief",
                     data=years_gender, ax=ax[0])
        ax[0].set_title("relation between gender and average trip duriation",
                        fontsize=20)
        ax[0].set_xlabel("year", fontsize=18)
        ax[0].set_ylabel("trip duriation", fontsize=18)

        ax[0].set_xticklabels(years_gender["year"])

        legend = ax[0].legend()
        legend.get_texts()[1].set_text("unknown")
        legend.get_texts()[2].set_text("male")
        legend.get_texts()[3].set_text("female")

        # plot the average trip duration of different years
        # showing the difference between usertypes
        years_type = sample.groupby(["year", "usertype"])["tripduration"]\
            .mean()
        sns.lineplot(x="year", y="tripduration", hue="usertype",
                     legend="brief", data=years_type.reset_index(), ax=ax[1])
        ax[1].set_title("relation between user type and \
                        average trip duriation", fontsize=20)
        ax[1].set_xlabel("year", fontsize=18)
        ax[1].set_ylabel("trip duriation", fontsize=18)

        ax[0].set_xticklabels(years_gender["year"])

        linefig.savefig("lineplots.png")


def barplot(data):
    """
    take in a dataframe
    draw line plots and save the fiugre as barplots.png
    """
    sample = data
    sns.set_style('darkgrid', {"xtick.major.size": 20, "ytick.major.size": 20})
    plt.tight_layout()
    with sns.plotting_context(rc={"legend.fontsize": 17}):
        barfig, ax = plt.subplots(ncols=2, figsize=(14, 6))
        # plot the trip count of different seaons in each year
        sample["count"] = 1
        tripcount_season = sample.groupby(["year", "Season"])["count"].sum()
        sns.barplot(x="year", y="count", hue="Season",
                    data=tripcount_season.reset_index(), ax=ax[0])
        ax[0].legend(loc='upper left', bbox_to_anchor=(1.04, 1))

        ax[1].set_xlabel("year", fontsize=18)
        ax[1].set_ylabel("trip count", fontsize=18)

        # plot the trip count of different period in each year
        tripcount_period = sample.groupby(["year", "Period"])["count"].sum()
        sns.barplot(x="year", y="count", hue="Period",
                    data=tripcount_period.reset_index(), ax=ax[1])
        ax[1].legend(loc='upper left', bbox_to_anchor=(1.04, 1))

        ax[1].set_xlabel("year", fontsize=18)
        ax[1].set_ylabel("trip count", fontsize=18)

        barfig.tight_layout()
        barfig.savefig("barplots.png")


def freqplot(data):
    """
    take in a dataframe
    draw line plots and save the fiugre as freqplots.png
    """
    sample = data
    sns.set_style('darkgrid', {"xtick.major.size": 20, "ytick.major.size": 20})
    plt.tight_layout()
    with sns.plotting_context(rc={"legend.fontsize": 17}):
        freqfig, ax = plt.subplots(1, figsize=(8, 6))
        sample["count"] = 1
        sample = sample.groupby(["year", "month"])["count"].sum()
        years2 = sample.reset_index()

        sns.lineplot(x="month", y="count", hue="year", data=years2, ax=ax)
        freqfig.savefig("freqplots.png")


if __name__ == '__main__':
    main()
