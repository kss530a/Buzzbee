'''
작업
(waiting getPrice() function)Inputdata_X
(waiting data)Inputdata_Y
(Completed)LSTM
(Completed)FCNN
(Completed)TensorBoard
(Need to test)Saver
(Need to do)Arrange(define class, function etc)
reference - http://hunkim.github.io/ml/
refetence2 - http://aikorea.org/blog/rnn-tutorial-2/
'''


import tensorflow as tf
import numpy as np
import os
import matplotlib.pyplot as plt
import hyperParameters as hp
import random


#Variable의 초기 random값을 일정하게 지정
# for reproducibility, debuging
tf.set_random_seed(777)


# hyper-parameters
rnn_layer_size = hp.getHyparam("rnn_layer_size")
seq_length = hp.getHyparam("seq_length") #타임시리즈 1회 처리 수
data_dim = hp.getHyparam("data_dim") #단어 수
hidden_dim = hp.getHyparam("hidden_dim") #RNNCell의 출력 넓이
Normarization = hp.getHyparam("Normarization") # 입력데이터 일반화 - 미필요
fc_hidden_dim = hp.getHyparam("fc_hidden_dim") #FC 내부에서 사용되는 넓이
output_dim = hp.getHyparam("output_dim") #최종 출력값
learning_rate = hp.getHyparam("learning_rate") #1회 학습에서 배우는 정도
iterations = hp.getHyparam("iterations") #학습량
initializer=hp.getHyparam("initializer") #가중치 초기값 설정
CHECK_POINT_DIR = TB_SUMMARY_DIR = hp.getHyparam("CHECK_POINT_DIR") # saver


# # Open, High, Low, Volume, Close
# xy = np.loadtxt('data-02-stock_daily.csv', delimiter=',')
# xy = xy[::-1]
# x = xy
# y = xy[:, [-1]]  # Close as label
#
# def makeXY(company):
#     try:
#         conn = mysql.connect("seungsu", "tmdtn12", "orcl")
#         cur = conn.cursor()
#
#         # X데이터 가져오기
#         sql_select_tables = "select words" \
#                             "from input1 " \
#                             "where pcode='" + company + \
#                             "' order by st_date asc"
#         cur.execute(sql_select_tables)
#         x = cur.fetchall()[:-60] #최근 60분은 y_hat이 없음
#
#         # Y데이터 가져오기
#         sql_select_tables = "select y_hat" \
#                             "from stock_price " \
#                             "where pcode='" + company + \
#                             "' order by st_date asc"
#         cur.execute(sql_select_tables)
#         y = cur.fetchall()[:-60] #최근 60분은 y_hat이 없음
#
#     except mysql.DatabaseError as e:
#         print('makeY Error : ', e)
#     finally:
#         cur.close()
#         conn.close()


# build data-set
# dataX = []
# dataY = []
# for i in range(0, len(y) - seq_length):
#     _x = x[i:i + seq_length]
#     _y = y[i + seq_length]  # Next close price
#     print(_x, "->", _y)
#     dataX.append(_x)
#     dataY.append(_y)R
x_data = []
dataX = []
_dataY = []
dataY = []

# Y 만들기
for i in range(0,100):
    dataY.append([random.randint(0,1)])

# X 만들기
for k in range(0, 100):
    _x_date = []
    for j in range(0,2000):
        _x_date.append(random.randint(0,5))
    x_data.append(_x_date)


# X 시퀀스 만들기
for i in range(0, len(x_data) - 10):
    _x = x_data[i:i+10]
    dataX.append(_x)

dataX=np.array(dataX)
# print(dataX.shape)



# train/test split
train_size = int(len(dataY) * 0.7)
test_size = len(dataY) - train_size
trainX = np.array(dataX[0:train_size])
testX = np.array(dataX[train_size:len(dataX)])
trainY = np.array(dataY[0:train_size])
testY = np.array(dataY[train_size:len(dataY)-10])
# print(trainX.shape)
# print(trainY.shape)
# print(testY.shape)

# input place holders
with tf.name_scope('input_data') as scope:
    X = tf.placeholder(tf.float32, [None, seq_length, data_dim], name="X_input")
    Y = tf.placeholder(tf.float32, [None, output_dim], name="Y_input")

# build a LSTM network - 5단
#activation 필요한지 체크 -> 초기값 설정을 위해 필요
with tf.name_scope('rnn_layer') as scope:
    def lstm_cell():
        cell = tf.contrib.rnn.BasicLSTMCell(num_units=hidden_dim, state_is_tuple=True, activation=tf.tanh)
        return cell
    multi_cells = tf.contrib.rnn.MultiRNNCell([lstm_cell() for _ in range(rnn_layer_size)], state_is_tuple=True)
    outputs, _states = tf.nn.dynamic_rnn(multi_cells, X, dtype=tf.float32)
    # print(outputs)
    x_for_FC = outputs[:,-1]
    # print(x_for_FC)
    tf.summary.histogram("rnn_outputs", outputs)


#LSTM의 ouputs을 FC에 넣기 - 3단, activation=relu
with tf.name_scope('FC_layer1') as scope:
    W1 = tf.Variable(tf.random_normal([hidden_dim, fc_hidden_dim]), name='weight1')
    B1 = tf.Variable(tf.random_normal([fc_hidden_dim]), name='bias1')
    L1 = tf.nn.relu(tf.matmul(x_for_FC, W1) + B1)

    tf.summary.histogram("weights1", W1)
    tf.summary.histogram("bias1", B1)
    tf.summary.histogram("layer1", L1)


with tf.name_scope('FC_layer2') as scope:
    W2 = tf.Variable(tf.random_normal([fc_hidden_dim, fc_hidden_dim]), name='weight2')
    B2 = tf.Variable(tf.random_normal([fc_hidden_dim]), 'bias2')
    L2 = tf.nn.relu(tf.matmul(L1, W2) + B2)

    tf.summary.histogram("weights2", W2)
    tf.summary.histogram("bias2", B2)
    tf.summary.histogram("layer2", L2)


with tf.name_scope('FC_layer3') as scope:
    W3 = tf.Variable(tf.random_normal([fc_hidden_dim, output_dim]), name='weight3')
    B3 = tf.Variable(tf.random_normal([output_dim]), name='bias3')
    Y_hat = tf.nn.relu(tf.matmul(L2, W3) + B3)
    # print(Y_hat)
    #Y_hat = tf.reshape(Y_hat, [-1, 10, 1])
    #Logits must be a [batch_size x sequence_length x logits] tensor

    tf.summary.histogram("weights3", W3)
    tf.summary.histogram("bias3", B3)
    tf.summary.histogram("Y_hat", Y_hat)


# cost/loss
with tf.name_scope('loss') as scope:
    #weight = tf.ones([100, 10])
    #sequence_loss = tf.contrib.seq2seq.sequence_loss(logits=Y_hat, targets=Y, weights=weight)  # sum of the squares
    #loss = tf.reduce_mean(tf.contrib.seq2seq.sequence_loss(logits=Y_hat, targets=Y, weights=weight))
    loss = tf.reduce_sum(tf.square(Y_hat - Y))  # sum of the squares
    loss_summ = tf.summary.scalar("loss", loss)

# optimizer
with tf.name_scope("train"):
    optimizer = tf.train.AdamOptimizer(learning_rate)
    train = optimizer.minimize(loss)

# for Saver
last_iterations = tf.Variable(0, name='last_iterations')

# RMSE
# with tf.name_scope("accuracy"):
#     targets = tf.placeholder(tf.int32, [None, 1], name="targets")
#     predictions = tf.placeholder(tf.float32, [None, 1], name="predictions")
#     rmse = tf.sqrt(tf.reduce_mean(tf.square(targets - predictions)))
#     tf.summary.scalar("rmse", rmse)
targets = tf.placeholder(tf.float32, [None, 1])
predictions = tf.placeholder(tf.float32, [None, 1])
rmse = tf.sqrt(tf.reduce_mean(tf.square(targets - predictions)))

with tf.Session() as sess:
    init = tf.global_variables_initializer()
    sess.run(init)

    # Saver and Restore
    saver = tf.train.Saver()
    checkpoint = tf.train.get_checkpoint_state(CHECK_POINT_DIR)

    if checkpoint and checkpoint.model_checkpoint_path:
        try:
            saver.restore(sess, checkpoint.model_checkpoint_path)
            print("Successfully loaded:", checkpoint.model_checkpoint_path)
        except:
            print("Error on loading old network weights")
    else:
        print("Could not find old network weights")

    start_from = sess.run(last_iterations)


    #for TB
    summary = tf.summary.merge_all()
    writer = tf.summary.FileWriter('./rnn')
    writer.add_graph(sess.graph)
    global_step = 0

    # train my model
    print('Start learning from:', start_from)

    # Training step
    for i in range(iterations):
        _, step_loss, s = sess.run([train, loss, summary], feed_dict={
                                X: trainX, Y: trainY})
        print("[step: {}] loss: {}".format(i, step_loss))
        writer.add_summary(s, global_step=global_step)
        global_step += 1

        print("Saving network...")
        sess.run(last_iterations.assign(iterations + 1))
        if not os.path.exists(CHECK_POINT_DIR):
            os.makedirs(CHECK_POINT_DIR)
    saver.save(sess, CHECK_POINT_DIR + "/model")

    print('Learning Finished!')



# Test step
    with tf.name_scope("accuracy"):
        test_predict = sess.run(Y_hat, feed_dict={X: testX})
        rmse_val = sess.run(rmse, feed_dict={
            targets: testY, predictions: test_predict})

        tf.summary.histogram("test_predict", test_predict)
        tf.summary.histogram("rmse_val", rmse_val)

        print("RMSE: {}".format(rmse_val))


#Plot predictions
# plt.plot(testY)
# plt.plot(test_predict)
# plt.xlabel("Time Period")
# plt.ylabel("Stock Price")
# plt.show()
