import tensorflow as tf
import numpy as np
import matplotlib.pyplot as plt
import random

from tensorflow.examples.tutorials.mnist import input_data
mnist = input_data.read_data_sets("MNIST_data/", one_hot=True)

nb_classes = 10
'''
X = tf.placeholder(tf.float32, [None, 784])
Y = tf.placeholder(tf.float32, [None, nb_classes])


w1 = tf.Variable(tf.random_normal([784, 100]), name='weight')
b1 = tf.Variable(tf.random_normal([100]), name='bias')
layer1 = tf.nn.softmax(tf.matmul(X, w1) + b1)

w2 = tf.Variable(tf.random_normal([100, 100]), name='weight')
b2 = tf.Variable(tf.random_normal([100]), name='bias')
layer2 = tf.nn.softmax(tf.matmul(layer1, w2) + b2)

w3 = tf.Variable(tf.random_normal([100, 100]), name='weight')
b3 = tf.Variable(tf.random_normal([100]), name='bias')
layer3 = tf.nn.softmax(tf.matmul(layer2, w3) + b3)

w4 = tf.Variable(tf.random_normal([100, 10]), name='weight')
b4 = tf.Variable(tf.random_normal([10]), name='bias')
layer4 = tf.nn.softmax(tf.matmul(layer3, w4) + b4)

w5 = tf.Variable(tf.random_normal([10, nb_classes]), name='weight')
b5 = tf.Variable(tf.random_normal([nb_classes]), name='bias')
layer5 = tf.nn.softmax(tf.matmul(layer4, w5) + b5)

logits = tf.matmul(layer5, w5) + b5
hypothesis = tf.nn.softmax(logits)
'''
l2reg = 0.001 * tf.reduce_sum(tf.square(w3)) #regularization strength

cost_i = tf.nn.softmax_cross_entropy_with_logits(logits=logits, labels=Y)
cost = tf.reduce_mean(cost_i + l2reg)
optimizer = tf.train.GradientDescentOptimizer(learning_rate=0.1).minimize(cost)

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
                        Y:batch_ys})
        avg_cost += c / total_batch

    print('Epoch: ', '%04d' % (epoch + 1), 'cost =', '{:.9f}'.
          format(avg_cost))

#sess.run() = accuracy.eval()
print("Accuracy: ", accuracy.eval(session=sess, feed_dict=
{X: mnist.test.images, Y:mnist.test.labels}))

r = random.randint(0, mnist.test.num_examples -1)
print("Label: ", sess.run(tf.argmax(mnist.test.labels[r:r+1],1)))
print("Prediction: ", sess.run(tf.argmax(hypothesis, 1),
                               feed_dict={X:mnist.test.images[r:r+1]}))

plt.imshow(mnist.test.images[r:r+1].reshape(28,28),
           cmap='Greys', interpolation='nearest')
plt.show()