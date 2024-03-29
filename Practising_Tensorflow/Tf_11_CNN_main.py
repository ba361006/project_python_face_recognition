import tensorflow as tf 
from tensorflow.examples.tutorials.mnist import input_data

mnist = input_data.read_data_sets('MNIST_data', one_hot = True)

def compute_accuracy(v_xs, v_ys):
    global prediction
    y_pre = sess.run(prediction, feed_dict = {xs: v_xs, keep_prob: 1})


    # print('y_pre[0]:', y_pre[0])
    # print('type(y_pre):', type(y_pre))
    correct_prediction = tf.equal(tf.argmax(y_pre,1),tf.argmax(v_ys,1))
    # print('correct_prediction:', sess.run(correct_prediction))
    
    accuracy = tf.reduce_mean(tf.cast(correct_prediction, tf.float32))
    # print('accuracy:', sess.run(accuracy))

    result = sess.run(accuracy, feed_dict = {xs:v_xs, ys:v_ys, keep_prob:1})
    return result

def weight_variable(shape):
    #tf.truncated_normal(shape, mean, stddev) 維度、平均值、標準
    #同樣也是常態分布函數只是與一般常用的差在如果出來的值與平均值差別大於兩倍標準差就重新再生成一次
    initial = tf.truncated_normal(shape, stddev = 0.1)
    return tf.Variable(initial)

def bias_variable(shape):
    initial = tf.constant(0.1, shape = shape)
    return tf.Variable(initial)

def conv2d(x, W):
    # tf.nn.conv2d(inputs, filter, strides, padding)
    #inputs: [batch, in_height, in_width, in_channels]；[輸入的張數, 輸入的長, 輸入的寬, 有幾層(顏色)]
    #filter: [filter_height, filter_width, in_channels, out_channels]；[filter長, filter寬, 輸入層數, 輸出層數]
    #stride [1 ,x_movement, y_movement, 1]  前後兩個固定為1
    return tf.nn.conv2d(x, W, strides = [1,1,1,1], padding = 'SAME') #SAME是尺寸大小一致，超出filter的地方補0；VALID則是尺寸會變小

def max_pool_2x2(x):
    #若strides要大一點則先取小的stride再經由pooling取需要的步伐
    #tf.nn.max_pool(value, ksize, strides, padding, name=None)
    #value: [batch, height, width, channels]；
    #ksize [batch, height, width, channels]；一般不會希望pooling到batch與channel 所以這兩個會是1； 基本上這裡的height與width就是filter的長寬並只印出最大值
    return tf.nn.max_pool(x, ksize = [1,2,2,1], strides = [1,2,2,1], padding = 'SAME')
    
    


xs = tf.placeholder(tf.float32, [None,784])
ys = tf.placeholder(tf.float32, [None,10])
keep_prob = tf.placeholder(tf.float32)
x_image = tf.reshape(xs, [-1, 28, 28, 1])#第一個-1: 先不理輸入有幾個batch，與placeholder的None頗像
print(x_image.shape) #[n_samples, 28, 28, 1]


##  conv1 layer ##
W_conv1 = weight_variable([5, 5, 1, 32])#patch 5x5(5x5 filter), in size 1(厚度), out size 32(高度)
b_conv1 = bias_variable([32])
h_conv1 = tf.nn.relu(conv2d(x_image, W_conv1) + b_conv1)# output size 28x28x32
h_pool1 = max_pool_2x2(h_conv1)                         # output size 14x14x32


##  conv2 layer ##
W_conv2 = weight_variable([5, 5, 32, 64])#patch 5x5(5x5 filter), in size 32(厚度), out size 64(高度)
b_conv2 = bias_variable([64])
h_conv2 = tf.nn.relu(conv2d(h_pool1, W_conv2) + b_conv2)# output size 14x14x64
h_pool2 = max_pool_2x2(h_conv2)                         # output size 7x7x64


##  func1 layer ##
W_fc1 = weight_variable([7*7*64, 1024])
b_fc1 = bias_variable([1024])   #1024是隨便取的
#[n_samples, 7,7,64] >>> [n_samples, 7*7*64]
h_pool2_flat = tf.reshape(h_pool2, [-1,7*7*64]) #改變不知道有多少張且經池化過後的圖片的維度轉成與全連接層相同的維度
h_fc1 = tf.nn.relu(tf.matmul(h_pool2_flat, W_fc1) + b_fc1)
h_fc1_drop = tf.nn.dropout(h_fc1, keep_prob)


##  func2 layer ##
W_fc2 = weight_variable([1024, 10])
b_fc2 = bias_variable([10])
prediction = tf.nn.softmax(tf.matmul(h_fc1_drop, W_fc2) + b_fc2)

# prediction = tf.matmul(h_fc1_drop, W_fc2) + b_fc2
# cross_entropy = tf.reduce_sum(tf.nn.softmax_cross_entropy_with_logits(logits = prediction, labels = ys))

cross_entropy = tf.reduce_mean(-tf.reduce_sum(ys * tf.log(prediction),
                                              reduction_indices=[1]))       # loss
train_step = tf.train.AdamOptimizer(1e-4).minimize(cross_entropy)


init = tf.initialize_all_variables()

with tf.Session() as sess:
    sess.run(init)
    for i in range(1001):
        batch_xs, batch_ys = mnist.train.next_batch(100) 
        sess.run(train_step, feed_dict={xs: batch_xs, ys: batch_ys, keep_prob: 0.5})
        if i %50 ==0:
            print("i= ", i, compute_accuracy(
                mnist.test.images[:1000], mnist.test.labels[:1000]
            ))
            print('prediction', sess.run(prediction,feed_dict={xs: batch_xs, ys: batch_ys, keep_prob: 0.5}))
            print('batch_xs.shape', batch_xs.shape)
            # print('loss = ', sess.run(train_step, feed_dict={xs: batch_xs, ys: batch_ys, keep_prob: 0.5}))
        # if i % 100 == 0:
            # print('batch_ys:',batch_ys)
            # print('type(batch_ys:)',type(batch_ys))# numpy.ndarray