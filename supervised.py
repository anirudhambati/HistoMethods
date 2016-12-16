"""Analyzes the (pre-extracted) Nuclei of 
K. Sirinukunwattana, S.E.A. Raza, Y.W Tsang, I.A. Cree, D.R.J. Snead, N.M. Rajpoot, 
Locality Sensitive Deep Learning for Detection and Classification of Nuclei in Routine Colon Cancer Histology Images
IEEE Transactions on Medical Imaging, 2016 (in press)

Using Lasagne and Theano setup
1. Fully Supervised Learning for CNN"""

from scipy import misc
import numpy as np 
import matplotlib.pyplot as plt
import scipy.io as sio
import lasagne
import theano
import theano.tensor as T
import sklearn.metrics as m

def onehot_to_vector(labels):
    x = len(labels)
    vector = np.zeros((x,4))
    for k in range(x):
        vector[k,labels[k]] = 1
    return vector
        

def read_data():
    images = np.zeros((100,500,500,3), dtype=np.uint8)
    path = "/home/veda/ColonHistology/CRCHistoPhenotypes_2016_04_28/Classification/"
    for i in range(1,101):
        filename = "img" + str(i)
        fullpath = path + filename + "/" + filename + ".bmp" 
        images[i-1,:,:,:] = misc.imread(fullpath)
    
    return images

"Labels are in the form [epithelial, fibroblast, inflammatory, other]"
def create_dataset(images):
    data = np.zeros((0,3,27,27)).astype(np.uint8)
    labels = np.zeros((0,1)).astype(np.int8)
    r = 13
    no_fibroblast = 0
    no_epithelial = 0
    no_inflammatory = 0
    no_others = 0
    
    #take 1 500x500 image
    for k in range(0,100):
        
        if(k % 10 == 0):
            print("Loading Image " + str(k) + " of 100")
        
        
        image = images[k]
     
        fibroblast = sio.loadmat("/home/veda/ColonHistology/CRCHistoPhenotypes_2016_04_28/Classification/img" + str(k+1) + "/img" + 
                                 str(k+1) +"_fibroblast")
        coors = fibroblast["detection"]
        if(coors.shape[0] > 0):
            for i in range(0,coors.shape[0]):
                
                y = coors[i,0]
                y = y.astype(np.int32)
                x = coors[i,1]
                x = x.astype(np.int32)
                
                
                if(y > 26 and y < 474 and x > 26 and x < 474):
                    add = image[x-r:x+r+1,y-r:y+r+1,:]
                    add = np.swapaxes(np.swapaxes(add, 1, 2), 0, 1)
                    add = np.expand_dims(add,axis=0)
                    data = np.concatenate((add,data))
                    labels = np.append(labels,1)
                    no_fibroblast += 1
                
                #label_vector = np.expand_dims(np.array([0,1,0,0]),axis=0)
              #  labels = np.concatenate((label_vector,labels),axis=0)
            
        epithelial = sio.loadmat("/home/veda/ColonHistology/CRCHistoPhenotypes_2016_04_28/Classification/img" + str(k+1) + "/img" + 
                                 str(k+1) +"_epithelial")
        coors = epithelial["detection"]
        if(coors.shape[0] > 0):
            for i in range(0,coors.shape[0]):
                
                y = coors[i,0]
                y = y.astype(np.int32)
                x = coors[i,1]
                x = x.astype(np.int32)
                
                
                if(y > 26 and y < 474 and x > 26 and x < 474):
                    add = image[x-r:x+r+1,y-r:y+r+1,:]
                    add = np.swapaxes(np.swapaxes(add, 1, 2), 0, 1)
                    add = np.expand_dims(add,axis=0)
                    data = np.concatenate((add,data))
                    labels = np.append(labels,0)
                    no_epithelial += 1
                    
        inflammatory = sio.loadmat("/home/veda/ColonHistology/CRCHistoPhenotypes_2016_04_28/Classification/img" + str(k+1) + "/img" + 
                                 str(k+1) +"_inflammatory")
        coors = inflammatory["detection"]
        if(coors.shape[0] > 0):
            for i in range(0,coors.shape[0]):
                
                y = coors[i,0]
                y = y.astype(np.int32)
                x = coors[i,1]
                x = x.astype(np.int32)
                
                
                if(y > 26 and y < 474 and x > 26 and x < 474):
                    add = image[x-r:x+r+1,y-r:y+r+1,:]
                    add = np.swapaxes(np.swapaxes(add, 1, 2), 0, 1)
                    add = np.expand_dims(add,axis=0)
                    data = np.concatenate((add,data))
                    labels = np.append(labels,2)
                    no_inflammatory += 1
          
        others = sio.loadmat("/home/veda/ColonHistology/CRCHistoPhenotypes_2016_04_28/Classification/img" + str(k+1) + "/img" + 
                                 str(k+1) +"_others")
        coors = others["detection"]
        if(coors.shape[0] > 0):
            for i in range(0,coors.shape[0]):
                
                y = coors[i,0]
                y = y.astype(np.int32)
                x = coors[i,1]
                x = x.astype(np.int32)
                
                
                if(y > 26 and y < 474 and x > 26 and x < 474):
                    add = image[x-r:x+r+1,y-r:y+r+1,:]
                    add = np.swapaxes(np.swapaxes(add, 1, 2), 0, 1)
                    add = np.expand_dims(add,axis=0)
                    data = np.concatenate((add,data))
                    labels = np.append(labels,3)
                    no_others += 1
    
                    
    print("Number of Fibroblasts: " + str(no_fibroblast)
    + " Number of Epithelial: " + str(no_epithelial) + 
    " Number of inflammatory: " + str(no_inflammatory) + 
    " Number of others: " + str(no_others))
    data = data.astype(np.float32)
    data = data / 255
    data = (data - np.mean(data)) / np.std(data)          
    labels = labels.astype(np.int32)
    return data, labels
    
    
def data_split(data,labels):
    train_data = np.zeros((0,3,27,27)).astype(np.float32)
    train_labels = np.zeros((0,1)).astype(np.int8)
    val_data = np.zeros((0,3,27,27)).astype(np.float32)
    val_labels = np.zeros((0,1)).astype(np.int8)
    test_data = np.zeros((0,3,27,27)).astype(np.float32)
    test_labels = np.zeros((0,1)).astype(np.int8)
    for n in range(0,labels.shape[0]):
        
        if(n % 5000 == 0):
            print("Splitting Image " + str(n) + " of " + str(labels.shape[0]))
        
        im = np.expand_dims(data[n,:,:,:],axis=0)
        lab = labels[n]
        splitr = np.random.random();
        
        if(splitr < 0.2):
            test_data = np.concatenate((test_data,im))
            test_labels = np.append(test_labels,lab)
            #test_labels = np.concatenate((test_labels,lab))
        elif(splitr > 0.85):
            val_data = np.concatenate((val_data,im))
            val_labels = np.append(val_labels,lab)
            #val_labels = np.concatenate((val_labels,lab))
        else:
            train_data = np.concatenate((train_data,im))
            train_labels = np.append(train_labels,lab)
            #train_labels = np.concatenate((train_labels,lab))
    return train_data, train_labels, val_data, val_labels, test_data, test_labels
        
    
def check_coordinates(images):
    for k in range(7,8):
        image = images[k]
        fibroblast = sio.loadmat("/home/veda/ColonHistology/CRCHistoPhenotypes_2016_04_28/Classification/img" + str(k+1) + "/img" + 
                                 str(k+1) +"_epithelial")
        coors = fibroblast["detection"]
        r = 10
        for i in range(0,coors.size/2):
            y = coors[i,0] 
            x = coors[i,1]
            image[x-r:x+r,y-r:y+r,:] =0
        imgplot = plt.imshow(image.astype(np.uint8))
        return coors

#this is temporary until CNN architecture is created to match the paper 
def build_cnn(input_var=None):

    network = lasagne.layers.InputLayer(shape=(None, 3, 27, 27),
    input_var=input_var)
    print(lasagne.layers.get_output_shape(network))

    network = lasagne.layers.Conv2DLayer(
    network, num_filters=36, filter_size=(4, 4),
    nonlinearity=lasagne.nonlinearities.rectify)
    print(lasagne.layers.get_output_shape(network))
    
    network = lasagne.layers.MaxPool2DLayer(network, pool_size=(2, 2))
    print(lasagne.layers.get_output_shape(network))
    
    network = lasagne.layers.Conv2DLayer(
    network, num_filters=48, filter_size=(3, 3),
    nonlinearity=lasagne.nonlinearities.rectify)
    print(lasagne.layers.get_output_shape(network))
    
    network = lasagne.layers.MaxPool2DLayer(network, pool_size=(2, 2))
    print(lasagne.layers.get_output_shape(network))

    network = lasagne.layers.DenseLayer(network,
    num_units=512,
    nonlinearity=lasagne.nonlinearities.rectify)
    print(lasagne.layers.get_output_shape(network))

    network = lasagne.layers.DenseLayer(network,
    num_units=512,
    nonlinearity=lasagne.nonlinearities.rectify)
    print(lasagne.layers.get_output_shape(network))
    
    network = lasagne.layers.DenseLayer(network,
    num_units=4,
    nonlinearity=lasagne.nonlinearities.softmax)
    print(lasagne.layers.get_output_shape(network))
    return network

def iterate_minibatches(inputs, targets, batchsize, shuffle=False):
    assert len(inputs) == len(targets)
    if shuffle:
        indices = np.arange(len(inputs))
        np.random.shuffle(indices)
        
    if(batchsize > len(targets)):
        yield inputs, targets
        
        
    for start_idx in range(0, len(inputs) - batchsize + 1, batchsize):
        if shuffle:
            excerpt = indices[start_idx:start_idx + batchsize]
        else:
            excerpt = slice(start_idx, start_idx + batchsize)
        yield inputs[excerpt], targets[excerpt] 
        
def main():    
    images = read_data()
    num_epochs = 100
    data, labels = create_dataset(images)
    X_train, y_train, X_val, y_val, X_test, y_test = data_split(data,labels)
    #Create training functions in theano
    input_var = T.tensor4('inputs')
    target_var = T.ivector('targets')
    network = build_cnn(input_var)
    
    
    epsilon = 1e-9
    
    prediction = lasagne.layers.get_output(network)
    prediction = T.clip(prediction,epsilon,1-epsilon)
    loss = lasagne.objectives.categorical_crossentropy(prediction, target_var)
    loss = loss.mean()

    params = lasagne.layers.get_all_params(network, trainable=True)
    updates = lasagne.updates.nesterov_momentum(
    loss, params, learning_rate=0.01, momentum=0.9)

    test_prediction = lasagne.layers.get_output(network, deterministic=True)
    test_prediction = T.clip(prediction,epsilon,1-epsilon)
    test_loss = lasagne.objectives.categorical_crossentropy(test_prediction,
    target_var)
    test_loss = test_loss.mean()

    train_fn = theano.function([input_var, target_var], [loss,prediction], updates=updates)

    val_fn = theano.function([input_var, target_var], [test_loss, test_prediction])
    
    # Finally, launch the training loop.
    print("Starting training...")
    # We iterate over epochs:
    for epoch in range(num_epochs):
        # In each epoch, we do a full pass over the training data:
        train_err = 0
        rd_err = 0
        train_batches = 0
        train_preds = np.zeros((0,4))
        train_order = np.zeros((0,4))
        test_preds = np.zeros((0,4))
        test_order = np.zeros((0,4))
     
        for batch in iterate_minibatches(X_train, y_train, 500, shuffle=True):
            inputs, targets = batch
            rd_err, preds = train_fn(inputs, targets)
            train_preds = np.concatenate((train_preds,preds))
            train_order = np.concatenate((train_order,onehot_to_vector(targets)))
            train_batches += 1
            train_err += rd_err
            
        print("Training ROC: " + str(m.roc_auc_score(train_order,train_preds)))
            
        # And a full pass over the validation data:
        val_err = 0
        val_batches = 0
        val_acc = 0
        for batch in iterate_minibatches(X_val, y_val, 500, shuffle=False):
            inputs, targets = batch
            err, preds = val_fn(inputs, targets)
            test_preds = np.concatenate((test_preds,preds))
            test_order = np.concatenate((test_order,onehot_to_vector(targets)))
            val_err += err
            val_batches += 1
        # Then we print the results for this epoch:
        print("Epoch {} of {} Completed".format(
        epoch + 1, num_epochs))
        print(" training loss:\t\t{:.6f}".format(train_err / train_batches))
        print(" validation loss:\t\t{:.6f}".format(val_err / val_batches))
        print("Validation ROC: " + str(m.roc_auc_score(test_order,test_preds)))
    # After training, we compute and print the test error:
    test_err = 0
    test_batches = 0
    for batch in iterate_minibatches(X_test, y_test, 500, shuffle=False):
        inputs, targets = batch
        err, preds = val_fn(inputs, targets)
        test_err += err
        test_batches += 1
    print("Final results:")
    print(" test loss:\t\t\t{:.6f}".format(test_err / test_batches))
main()

