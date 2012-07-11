import math
import itertools
import random
width = 10 # The width of the quilt in blocks
height = 10 # The height of the quilt in blocks
maxLikeness = 0.75
blackRatio = 0.8 # How imporant it is to have the black colors distributed
varianceOfSameColors = 0.8 # Two colors of different shades are this ratio alike
# as opposed to the blues/purples
squareSize = 4 # How big the squares are when measuring variance


# Define the colors (because what fun is it without real colors?)
blues = ['Turqoise', 'Cobalt', 'Azure']
purples = ['Violet', 'Brinjal', 'Lavender']
blacks = ['Midnight', 'Charcoal', 'Gothic', 'Imperial']

# Create a set containing all the possible blocks
primaryColors = blues
primaryColors.extend(purples)
colors = list(itertools.product(primaryColors, blacks))

# Create a list of all the blocks in the quilt
blocks = []
for i in range(width * height // len(colors)):
    blocks.extend(colors)

for i in range((width * height) - len(blocks)):
    blocks.append(colors[i])

# Now skip past all the defines. Wish python had forward declarations...

def GetBlock(lst, x, y, width):
    return lst[y * width + x]

def GetSquare(lst, x, y, width):
    square = []
    for i in range(squareSize):
        for j in range(squareSize):
            square.append(GetBlock(lst, x + i, y + j, width))
    return square

def GetColorVariance(counts, numColor):
    if numColor == 0:
        return 0
    # Colors from lightest to darkest are varianceOfSameColors / 2 apart
    modifier = [1 - ((1 - varianceOfSameColors) / 2.0), 1, 1 + ((1 -varianceOfSameColors) / 2.0)]
    counts = [a * b for a, b in zip(counts, modifier)]
    mean = sum(counts) / numColor
    variance = sum([a * ((b - mean) ** 2) for a, b in zip(counts, modifier)]) / numColor
    idealCounts = [math.floor(numColor / 2.0), 0, math.ceil(numColor / 2.0)]
    idealCounts = [a * b for a, b in zip(idealCounts, modifier)]
    idealMean = sum(idealCounts) / numColor
    idealVariance = sum([a * ((b - idealMean) ** 2) for a, b in zip(idealCounts, modifier)]) / numColor
    return variance / idealVariance


def GetVariance(square):
    blackCounts = [0, 0, 0]
    blueCounts = [0, 0, 0]
    purpleCounts = [0, 0, 0]
    numBlues = 0
    numPurples = 0
    numBlacks = 0
    for block in square:
        numBlues += 1
        if block[0] == "Turqoise":
            blueCounts[0] += 1
        elif block[0] == "Cobalt":
            blueCounts[1] += 1
        elif block[0] == "Azure":
            blueCounts[2] += 1
        else:
            numBlues -= 1
            numPurples += 1
            if block[0] == "Violet":
                purpleCounts[0] += 1
            elif block[0] == "Brinjal":
                purpleCounts[1] += 1
            else:
                purpleCounts[2] += 1

        numBlacks += 1
        if block[1] == "Midnight":
            blackCounts[0] += 1
        elif block[1] == "Charcoal":
            blackCounts[1] += 1
        elif block[1] == "Gothic":
            blackCounts[2] += 1
        else:
            blackCounts[3] += 1

    # First, get the variance of each color group
    blueVar = GetColorVariance(blueCounts, numBlues)
    purpleVar = GetColorVariance(purpleCounts, numPurples)
    blackVar = GetColorVariance(blackCounts, numBlacks)

    # Then, calculate the variance of the blue vs purples   
    # Just treat blue as 0, and purple as 1
    count = numBlues + numPurples
    mean = numPurples / count
    colorVar = sum([(1 - mean) ** 2 for _ in range(count)]) / count

    # Average the variances together using the weights provided
    return ((blueVar * varianceOfSameColors) + (purpleVar * varianceOfSameColors) + (blackVar * blackRatio) + colorVar) / 4

def TestArrangement(blocks):
    maxVariance = 0
    sumVariance = 0
    numBlocks = 0
    for i in range(0, width - squareSize + 1):
        for j in range(0, height - squareSize + 1):
            variance = GetVariance(GetSquare(blocks, i, j, width))
            if variance > maxLikeness:
                return (0,0)
            maxVariance = max(maxVariance, variance)
            sumVariance += variance
            numBlocks += 1
    return (sumVariance / numBlocks, maxVariance)

# This simple algorithm just randomly arranges the tiles
# It then checks to see if it matches the required distribution
# Since local variance is the most desired importance here,
# The algorithm is as follows: Break the rectangle into 3x3 blocks
# Calculate the variance of the square. Require it to be within the bounds
def GetValidArrangement(blocks):
    while True:
        random.shuffle(blocks)
        data = TestArrangement(blocks)
        if data == (0, 0):
            continue
        return (blocks, data)

data = GetValidArrangement(blocks)
row = []
for i in range(len(data[0])):
    row.append(data[0][i])
    if (i + 1) % width == 0:
        print(row)
        row[:] = []
print("Average variance is ", data[1][0])
output = "The max variance for a square of size " + repr(squareSize) + " is"
print(output, data[1][1])




