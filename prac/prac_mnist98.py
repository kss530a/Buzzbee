import tensorflow as tf
import numpy as np
import matplotlib.pyplot as plt
import random

from tensorflow.examples.tutorials.mnist import input_data
mnist = input_data.read_data_sets("MNIST_data/", one_hot=True)

nb_classes = 10
learning_rate = 0.01

X = tf.placeholder(tf.float32, [None, 784])
Y = tf.placeholder(tf.float32, [None, nb_classes])
keep_prob = tf.placeholder(tf.float32)

w1 = tf.get_variable("w1", shape=[784, 512],
                     initializer=tf.contrib.layers.xavier_initializer())
b1 = tf.Variable(tf.random_normal([512]), name='bias')
l1 = tf.nn.relu(tf.matmul(X, w1) + b1)
l1 = tf.nn.dropout(l1, keep_prob=keep_prob)

w2 = tf.get_variable("w2", shape=[512, 512],
                     initializer=tf.contrib.layers.xavier_initializer())
b2 = tf.Variable(tf.random_normal([512]), name='bias')
l2 = tf.nn.relu(tf.matmul(l1, w2) + b2)
l2 = tf.nn.dropout(l2, keep_prob=keep_prob)


w3 = tf.get_variable("w3", shape=[512, 512],
                     initializer=tf.contrib.layers.xavier_initializer())
b3 = tf.Variable(tf.random_normal([512]), name='bias')
l3 = tf.nn.relu(tf.matmul(l2, w3) + b3)
l3 = tf.nn.dropout(l3, keep_prob=keep_prob)


w4 = tf.get_variable("w4", shape=[512, 512],
                     initializer=tf.contrib.layers.xavier_initializer())
b4 = tf.Variable(tf.random_normal([512]), name='bias')
l4 = tf.nn.relu(tf.matmul(l3, w4) + b4)
l4 = tf.nn.dropout(l4, keep_prob=keep_prob)


w5 = tf.get_variable("w5", shape=[512, nb_classes],
                     initializer=tf.contrib.layers.xavier_initializer())
b5 = tf.Variable(tf.random_normal([nb_classes]), name='bias')
hypothesis = tf.matmul(l4, w5) + b5


l2reg = 0.001 * tf.reduce_sum(tf.square(w5)) #regularization strength
cost_i = tf.nn.softmax_cross_entropy_with_logits(logits=hypothesis, labels=Y)
cost = tf.reduce_mean(cost_i + l2reg)
optimizer = tf.train.AdamOptimizer(learning_rate=learning_rate).minimize(cost)

prediction = tf.argmax(hypothesis, 1)
correct_prediction = tf.equal(prediction, tf.argmax(Y,1))
accuracy = tf.reduce_mean(tf.cast(correct_prediction, tf.float32))

training_epochs = 15
batch_size = 100

sess =tf.Session()
sess.run(tf.global_variables_initializer())

for epoch in range(training_epochs):
    avg_cost = 0
    total_batch = int(mnist.train.num_examples/batch_size)

    for i in range(total_batch):
        batch_xs, batch_ys = mnist.train.next_batch(batch_size)
        c, _ = sess.run([cost, optimizer], feed_dict={X:batch_xs,
                        Y:batch_ys, keep_prob:0.7})
        avg_cost += c / total_batch

    print('Epoch: ', '%04d' % (epoch + 1), 'cost =', '{:.9f}'.
          format(avg_cost))

#sess.run() = accuracy.eval()
print("Accuracy: ", accuracy.eval(session=sess, feed_dict=
{X: mnist.test.images, Y:mnist.test.labels, keep_prob:1.0}))

r = random.randint(0, mnist.test.num_examples -1)
print("Label: ", sess.run(tf.argmax(mnist.test.labels[r:r+1],1)))
print("Prediction: ", sess.run(tf.argmax(hypothesis, 1),
                               feed_dict={X:mnist.test.images[r:r+1],keep_prob:1.0 }))

#plt.imshow(mnist.test.images[r:r+1].reshape(28,28),
#           cmap='Greys', interpolation='nearest')
#plt.show()