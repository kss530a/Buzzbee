import tensorflow as tf
import numpy as np

x_data =np.array([[0,0],[0,1],[1,0],[1,1]], dtype=np.float32)
y_data = np.array([[0],[1],[1],[0,]])

X = tf.placeholder(tf.float32)
Y = tf.placeholder(tf.float32)

w1 = tf.Variable(tf.random_normal([2, 10]), name='weight')
b1 = tf.Variable(tf.random_normal([1]), name='bias')
layer1 = tf.sigmoid(tf.matmul(X, w1) +b1)

w2 = tf.Variable(tf.random_normal([10, 1]), name='weight')
b2 = tf.Variable(tf.random_normal([1]), name='bias')
hypothesis = tf.sigmoid(tf.matmul(layer1, w2) + b2)


cost = -tf.reduce_mean(Y * tf.log(hypothesis) + (1-Y)*tf.log(1-hypothesis))
optimizer = tf.train.GradientDescentOptimizer(learning_rate=0.05).minimize(cost)

prediction = tf.cast(hypothesis>0.5, dtype=tf.float32)
accuracy = tf.reduce_mean(tf.cast(tf.equal(prediction, Y), tf.float32))

sess =tf.Session()
sess.run(tf.global_variables_initializer())

for step in range(10001):
    a, c = sess.run([optimizer, cost],
                       feed_dict={X:x_data, Y:y_data})
    if step % 100 == 0:
        print(step, c)

h, c, a = sess.run([hypothesis, prediction, accuracy],
                   feed_dict={X:x_data, Y:y_data})
print("\nHypothesis: ", h, "\ncorrect: ", c, "\nAccuracy: ", a)

