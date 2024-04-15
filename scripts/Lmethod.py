import numpy as np
from scipy.stats import linregress

def calculate_residuals(data, split_point):
    # Fit a line to each part of the data
    line1 = linregress(range(split_point), data[:split_point])
    line2 = linregress(range(split_point, len(data)), data[split_point:])
    
    # Calculate the residuals for each part
    residuals1 = data[:split_point] - (line1.intercept + line1.slope * np.arange(split_point))
    residuals2 = data[split_point:] - (line2.intercept + line2.slope * np.arange(split_point, len(data)))
    
    # Return the sum of squared residuals
    return sum(residuals1**2) + sum(residuals2**2)

def find_elbow_Lmethod(data):
    if len(data)<=4:
        return len(data)
    # Calculate the residuals for all possible split points
    residuals = [calculate_residuals(data, split_point) for split_point in range(2, len(data)-2)]
    
    # Return the split point with the smallest sum of residuals
    return np.argmin(residuals).item() + 2 # Offset by 2 because we started from 2

if __name__=='__main__':
    # Assume scores are your similarity scores in descending order
    scores = [0.2814037435, 0.2787846576, 0.2726645734, 0.2678206536, 0.1491900043, 
            0.1423106041, 0.1419459577, 0.1365295008, 0.1353198536, 0.133109612,
            0.13207702, 0.125892264, 0.1211496148, 0.1204840938, 0.1199606347,
            0.1194969381, 0.1170563477]

    elbow_point = find_elbow_Lmethod(scores)

    print("Elbow point:", elbow_point)
    print('Elbow list:', scores[:4])