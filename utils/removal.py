import pandas as pd
import os


def sortKey(filename):
    return int(filename.split(".")[0])

def removeRowsCSV(path, filenames):
    print(f"Removing rows from {path}")
    df = pd.read_csv(path)
    df.drop(df[df.Filename.isin(filenames)].index, inplace = True)
    df.to_csv(path, index = False)

def removeImages(dir, filenames):
    for filename in filenames:
        print(f"Removing {dir}/{filename}")
        os.remove(f"{dir}/{filename}")

def adjustImageNames(path):
    print(f"Adjusting images names for {path}")
    idx = 1; renew = False
    for imgName in sorted(os.listdir(path), key = sortKey):
        if(f"{idx}.png" != imgName):
            renew = True
            os.rename(f"{path}/{imgName}", f"{path}/{idx}.png")
        idx += 1
    return idx, renew
        
def adjustCSV(path, idx, renew):
    if(not renew):
        return
    print(f"Adjusting rows for {path}")    
    newNames = [f"{i}.png" for i in range(1, idx)]
    df = pd.read_csv(path)
    df.Filename = newNames
    df.to_csv(path, index = False)


with open("./remove.txt", mode = "r", encoding = "utf-8") as f:
    for line in f:
        town, images = line.strip().split(": ")
        filenames = [img + ".png" for img in images.split(", ")]
        imgDir = f"../dataset/{town}"; csvPath = f"../dataset/tabular/{town}.csv"
        removeImages(imgDir, filenames)
        removeRowsCSV(csvPath, filenames)
        idx, renew = adjustImageNames(imgDir)
        adjustCSV(csvPath, idx, renew)