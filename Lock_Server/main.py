from Lock_Server.MFCC import MFCC
from Lock_Server.play import Play
import time
from sklearn import neighbors
import numpy as npy
from multiprocessing import Queue,Manager

def weight():
    weight = []
    dis_with_w = []
    for i in range(0,2000):
        weight.append(
            (npy.max(npy.std(vectors,axis=0)) - npy.std(vectors[:,i])) / (npy.sum(npy.max(npy.std(vectors,axis=0)) - npy.std(vectors,axis=0)))
        )
    return weight


if __name__ == "__main__":
    manager = Manager()
    queue = manager.Queue()
    vectors = npy.ones((1,2000))
    queue.put(vectors)
    for x in range(0,40): # 30 -> pos,10 -> baseline
        mfcc = MFCC('/vibration.wav',queue)
        play = Play()
        play.start()
        time.sleep(0.16)
        mfcc.start()

        play.join()
        mfcc.join()
        time.sleep(1)
        if x == 29:
            print("请抬起手")
    vectors = queue.get()
    print(vectors)
    print(vectors.shape)
    newvectors = npy.ones((40,2000))
    n_neighbors = 3
    target1 = npy.array([0,0,0,0,0,0,0,0,0,0,
                         1,1,1,1,1,1,1,1,1,1,
                         2,2,2,2,2,2,2,2,2,2]).T
    target2 = npy.array([3,3,3,3,3,3,3,3,3,3]).T
    for x in range(1,41):
        for y in range(0,2000):
            newvectors[x-1,y] = (vectors[x,y] - npy.min(vectors[1:41,y]))/(npy.max(vectors[1:41,y]) - npy.min(vectors[1:41,y]))

    pos = neighbors.KNeighborsClassifier(n_neighbors,
                                         weights="uniform",
                                         metric="wminkowski",
                                         metric_params={
                                             'w':npy.array(weight())
                                         },p=1)
    print(newvectors[:30,:].shape,target1.shape)
    pos.fit(newvectors[:30,:], target1)
    dist_pos,ind_pos = pos.kneighbors(newvectors[:30,:],n_neighbors=3)
    E_distance_pos = npy.mean(npy.mean(dist_pos,axis=1))

    baseline = neighbors.KNeighborsClassifier(n_neighbors,
                                         weights="uniform",
                                         metric="wminkowski",
                                         metric_params={
                                             'w':npy.array(weight()),
                                             # 'p':1
                                         },p=1)
    baseline.fit(newvectors[30:,:], target2)
    dist_bl,ind_bl = baseline.kneighbors(newvectors[:30,:],n_neighbors=3)
    E_distance_bl = npy.mean(npy.mean(dist_bl,axis=1))
    a = 0.19
    threshold = (1-a)*E_distance_pos + a*E_distance_bl
    print("Threshold is ：{}".format(threshold))
    # mfcc.terminate()
    # play.terminate()
    # sys.exit(0)


