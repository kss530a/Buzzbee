import tensorflow as tf
import numpy as np
import matplotlib.pyplot as plt
import random

from tensorflow.examples.tutorials.mnist import input_data
mnist = input_data.read_data_sets("MNIST_data/", one_hot=True)

nb_classes = 10
learning_rate=0.01
training_epochs = 15
batch_size = 100

X = tf.placeholder(tf.float32, [None, 784])
Y = tf.placeholder(tf.float32, [None, nb_classes])

with tf.name_scope("layer") as scope:
    w = tf.Variable(tf.random_normal([784, nb_classes]), name='weight')
    b = tf.Variable(tf.random_normal([nb_classes]), name='bias')
    logits = tf.matmul(X, w) + b
    hypothesis = tf.nn.softmax(logits)

    w_hist = tf.summary.histogram("weight", w)
    b_hist = tf.summary.histogram("bias", b)
    hypothesis_hist = tf.summary.histogram("hypothesis", hypothesis)

cost = tf.reduce_mean(tf.nn.softmax_cross_entropy_with_logits(logits=hypothesis, labels=Y))
cost_summ = tf.summary.scalar("cost", cost)

optimizer = tf.train.GradientDescentOptimizer(learning_rate=learning_rate).minimize(cost)

with tf.name_scope("accuracy") as scope:
    prediction = tf.argmax(hypothesis, 1)
    correct_prediction = tf.equal(prediction, tf.argmax(Y,1))
    accuracy = tf.reduce_mean(tf.cast(correct_prediction, tf.float32))

    accu_summ = tf.summary.scalar("accuracy", accuracy)



summary = tf.summary.merge_all()
global_step = 0

sess =tf.Session()
sess.run(tf.global_variables_initializer())
writer = tf.summary.FileWriter('./logs', sess.graph)

for epoch in range(training_epochs):

    avg_cost = 0
    total_batch = int(mnist.train.num_examples/batch_size)


    for i in range(total_batch):
        batch_xs, batch_ys = mnist.train.next_batch(batch_size)
        s, c, _ = sess.run([summary, cost, optimizer], feed_dict={X:batch_xs,
                        Y:batch_ys})
        avg_cost += c / total_batch
        writer.add_summary(s, global_step=global_step)
        global_step += 1

    print('Epoch: ', '%04d' % (epoch + 1), 'cost =', '{:.9f}'.
          format(avg_cost))

#sess.run() = accuracy.eval()
print("Accuracy: ", accuracy.eval(session=sess, feed_dict=
{X: mnist.test.images, Y:mnist.test.labels}))

r = random.randint(0, mnist.test.num_examples -1)
print("Label: ", sess.run(tf.argmax(mnist.test.labels[r:r+1],1)))
print("Prediction: ", sess.run(tf.argmax(hypothesis, 1),
                               feed_dict={X:mnist.test.images[r:r+1]}))
