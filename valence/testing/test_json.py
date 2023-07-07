import matplotlib.pyplot as plt

# Sample data
label = ['A']
value = [1, 2, 3, 4]

# Create a scatter plot
plt.scatter(value,[label[0]] * len(value))

# Set plot title and labels
plt.title('Scatter Plot')
plt.xlabel('Label')
plt.ylabel('Value')

plt.show()
