import numpy as np
import matplotlib.pyplot as plt

def find_elbow(data):
    # Calculate the mean of the data
    mean = np.mean(data)
    # Calculate the standard deviation of the data
    std_dev = np.std(data)
    # Determine the z-scores
    z_scores = [(x - mean) / std_dev for x in data]
    # Determine the elbow point as the point with the maximum z-score
    elbow_point = np.argmax(z_scores)
    return elbow_point

if __name__ == "__main__":
    # Assume scores are your similarity scores in descending order
    scores = [0.2814037435, 0.1787846576, 0.1726645734, 0.1678206536, 0.1491900043,
              0.1423106041, 0.1419459577, 0.1365295008, 0.1353198536, 0.133109612,
              0.13207702, 0.125892264, 0.1211496148, 0.1204840938, 0.1199606347,
              0.1194969381, 0.1170563477]

    elbow_point = find_elbow(scores)

    # You can also plot to visualize it
    print(elbow_point)
    plt.figure(figsize=(10, 5))
    plt.plot(scores, 'o-', label='score')
    plt.vlines(x=elbow_point, ymin=min(scores), ymax=max(scores), colors='r', linestyles='dotted')
    plt.show()
    plt.savefig('elbow.png')