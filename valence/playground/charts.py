import matplotlib.pyplot as plt
import numpy as np

def plot_bar_chart(data, tags):
    # Create x-axis values as indices of the data vector
    x_values = np.arange(len(data))

    # Create a figure and axis
    fig, ax = plt.subplots()

    # Define colors for each unique tag
    unique_tags = set(tags)
    num_unique_tags = len(unique_tags)
    color_map = plt.get_cmap('tab10')

    # Plot the bar chart with different colors for each tag
    handles = []
    for i, tag in enumerate(unique_tags):
        tag_indices = [index for index, t in enumerate(tags) if t == tag]
        bar = ax.bar(x_values[tag_indices], [data[j] for j in tag_indices], color=color_map(i % num_unique_tags))
        handles.append(bar)
        

    # Add labels and title
    ax.legend(handles, unique_tags)
    ax.set_xlabel('Artists')
    ax.set_ylabel('Values')
    ax.set_title('Euclidean Distance between metalcore artist\n Imminence and compared artists')

    # Show the plot
    plt.show()

# Example input vectors
input_vector = [('The Devil Wears Prada', 4349.1395667905235), ('Architects', 5166.580489442609), ('Bring Me The Horizon', 5171.3644955887285), ('Miss May I', 5378.286766261558), ('Underoath', 5568.784072483427), ('Of Mice & Men', 6015.6623172121635), ('Asking Alexandria', 6126.067696922597), ('The Amity Affliction', 6256.8993391443555), ('The Ghost Inside', 6384.291176480426), ('Dance Gavin Dance', 6473.0708160477025), ('For Today', 6496.709083552907), ('blessthefall', 6560.325471467674), ('Atreyu', 6981.811616617234), ('A Day To Remember', 7258.03323027352), ('I Prevail', 7438.2008441641965), ('All That Remains', 7745.690079183813), ('Memphis May Fire', 7947.389972734184), ('We Came As Romans', 8020.461459290988), ('Gyllene Tider', 9098.443670911167), ('Veil Of Maya', 9128.33983713063), ('I See Stars', 9233.891763226628), ('Killswitch Engage', 9395.847619463404), ('Wage War', 9783.686811371013), ('Polaris', 10077.434417431366), ('Parkway Drive', 10189.305551770025), ('ERRA', 10615.78970732106), ('Dotter', 10648.436667583088), ('While She Sleeps', 10968.812432288501), ('Pierce The Veil', 11170.415785134477), ('Miss Li', 11814.603104757132), ('Per Gessle', 11966.187587604232), ('Florence + The Machine', 12243.23559281784), ('Coldplay', 12453.96879380002), ('Danny Saucedo', 12788.661035428016), ('Wiktoria', 13981.01257484726), ('Hanna Ferm', 14141.332602343446), ('Veronica Maggio', 14182.095579657464), ('Jpp', 14301.33874387524), ('Swedish House Mafia', 14408.421076410747), ('Norrlåtar', 14651.978220609657), ('estraden', 15913.889770248124), ('Iggesundsgänget', 16251.218484459458), ('Beartooth', 16637.44348233601), ('Ale Möller', 17354.2766040703), ('Sven Nyhus Kvartett', 17492.683397990506), ('Benjamin Ingrosso', 17669.82012007516), ('Peter Puma Hedlund', 18281.963519178847), ('August Burns Red', 18998.437217626655), ('Alex Järvi', 19229.987382543288), ('Oscar Zia', 19368.72112511266)]
input_vector_vals = [i[1] for i in input_vector]
instance_tag_metalcore = ['Metalcore' for i in range(0,30)]
instance_tag_metalcore[19] = 'Pop'
instance_tag_metalcore[25] = 'Pop'
instance_tag_pop = ['Pop' for i in range(0,20)]
instance_tag_pop[17] = 'Metalcore'
instance_tag = instance_tag_metalcore + instance_tag_pop
#19,25


second_input_vector = [('The Ghost Inside', 5118.934183501285), ('We Came As Romans', 6225.880761331789), ('Polaris', 7807.823757371236), ('Architects', 3839.932943801909), ('While She Sleeps', 8902.484522615903), ('Miss May I', 4209.287248033819), ('Wage War', 8543.48961834144), ('Asking Alexandria', 4864.2210538420495), ('blessthefall', 5388.689988231139), ('ERRA', 8329.038913387734), ('August Burns Red', 15933.769039139248), ('The Amity Affliction', 5077.826220259384), ('The Devil Wears Prada', 3447.92066185862), ('Currents', 100000), ('Bullet For My Valentine', 18591.74095695359), ('Avenged Sevenfold', 26634.423665076276), ('Parkway Drive', 8127.315560118236), ('Bring Me The Horizon', 4220.970925638897), ('Killswitch Engage', 8377.985672978619), ('Of Mice & Men', 5002.156639564045), ('Atreyu', 5878.511374885457), ('All That Remains', 6295.4814200693645), ('Beartooth', 15889.636740445923), ('Underoath', 4879.134032472987), ('I See Stars', 7278.475035841254), ('Veil Of Maya', 7153.221348758048), ('For Today', 5312.157671392792), ('Periphery', 27247.822705914175), ('Memphis May Fire', 6682.117343193604), ('Pierce The Veil', 9974.860233513995), ('A Day To Remember', 5787.212458630182), ('I Prevail', 5841.562244721733), ('Dance Gavin Dance', 4810.331890210483), ('Hanna Ferm', 11170.643380046142), ('Per Gessle', 9733.914832488384)]

# find common artists and show the difference between scores
common_artists = []
for i in input_vector:
    for j in second_input_vector:
        if i[0] == j[0]:
            common_artists.append((i[0], "Euclidean " + str(i[1]), "Minkowski " + str(j[1])))
for i in common_artists:
    print(i)
# Plot the bar chart with different colors for each tag
plot_bar_chart(input_vector_vals, instance_tag)
