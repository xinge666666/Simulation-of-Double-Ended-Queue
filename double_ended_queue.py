"""

Project of ISE 762: Simulation of Double Ended Queue ( An inventory system)

Variables:

t: current time
n: queue length, positive means available on-hand inventory; negative mean back orders exist
p_rate: production status, on-hand inventory (n > a)--> low production rate, back orders (n < -a), high production rate

q_plus: cumulative inventory level --> inventory holding cost
q_minus: cumulative backorder level --> order holding cost
n_plus: total number of inventory wastage
n_minus: total number of order cancellation(out of impatience)
n_match: total number of orders satisfied (real served orders)

Event_list = {1: product arrival, 2: product perish, 3: order arrival, 4: order cancellation}
t_p_arrival, t_p_perish, t_o_arrival, t_o_cancel

"""
import numpy as np
import matplotlib.pyplot as plt


def exponential_interval(rate):
    return -np.log(np.random.rand(1)) / rate


# Common parameters
p_perish_rate = 0.001  # product perish rate
o_arrival_rate = 6  # order arrival rate
o_cancel_rate = 0.001  # order cancel rate
threshold = 10
low_p_rate = 2
high_p_rate = 10
# simulation setting
n_runs = 1  # number of simulation repetition
t_max = 10 ** 5  # max simulation time

# main routine
for i in range(n_runs):

    t = 0  # simulation starts from time 0
    n = 0  # initial queue length
    perish_list = []
    patience_list = []
    all_event_time_list = []
    n_list = []
    q_plus, q_minus, n_plus, n_minus, n_match = [0] * 5

    # assume initially at low production rate !!!
    p_rate = low_p_rate  # low: 2, high: 10
    p_arrival_time = exponential_interval(p_rate)
    p_perish_time = np.inf  # no initial inventory
    o_arrival_time = exponential_interval(o_arrival_rate)
    o_cancel_time = np.inf  # no initial back order

    event_list = [p_arrival_time, p_perish_time, o_arrival_time, o_cancel_time]

    while t < t_max:
        idx = np.argmin(event_list)  # index of next event
        t1 = min(event_list)  # time of next event
        all_event_time_list.append(t1)
        n_list.append(n)
        # next event is product arrival
        if idx == 0 and n >= 0:  # next event is product arrival, sees no back order, inventory increase
            n += 1  # count new inventory
            q_plus += (t1 - t) * (n - 1)
            if n >= threshold:  # switch to low production rate
                p_rate = low_p_rate
            # generate arrival time and also perish time for each product arrival
            p_arrival_time = t1 + exponential_interval(p_rate)
            p_perish_time = p_arrival_time + exponential_interval(p_perish_rate)
            perish_list.append(p_perish_time)
            event_list[0] = p_arrival_time
            event_list[1] = min(perish_list)

        elif idx == 0 and n < 0:  # next event is product arrival, sees back order, backorder decrease
            n += 1  # this arrival is instantly satisfied
            n_match += 1
            q_minus += (t1 - t) * (n - 1)
            patience_list.pop(0)
            if len(patience_list) == 0:
                event_list[3] = np.inf
            else:
                event_list[3] = min(patience_list)  # update patience_list
            # generate new arrival time but no perish time since product arrival are satisfied instantly
            p_arrival_time = t1 + exponential_interval(p_rate)
            event_list[0] = p_arrival_time

        # next event is order arrival
        elif idx == 2 and n <= 0:  # next event is backorder arrival, sees backorder, backorder stack
            n -= 1  # count new backorder
            q_minus += (t1 - t) * (n + 1)
            if n <= -threshold:  # switch to high production rate
                p_rate = high_p_rate
            # generate new backorder arrival and patience time
            o_arrival_time = t1 + exponential_interval(o_arrival_rate)
            o_cancel_time = o_arrival_time + exponential_interval(o_cancel_rate)
            patience_list.append(o_cancel_time)
            event_list[2] = o_arrival_time
            event_list[3] = min(patience_list)

        elif idx == 2 and n > 0:  # next event is order arrival, sees available inventory, inventory decrease
            n -= 1  # the backorder is instantly satisfied
            n_match += 1
            q_plus += (t1 - t) * (n + 1)
            perish_list.pop(0)
            if len(perish_list) == 0:  # after popping, the perish_list is empty
                event_list[1] = np.inf
            else:
                event_list[1] = min(perish_list)
            # generate new order arrival but no patience time
            o_arrival_time = t1 + exponential_interval(o_arrival_rate)
            event_list[2] = o_arrival_time

        # next event is product perish
        elif idx == 1:  # product perish happens only when n>0
            n -= 1
            n_plus += 1
            q_plus += (t1 - t) * (n + 1)
            perish_list.remove(event_list[idx])  # delete the corresponding perish time
            if n == 0:  # The perish product is the only one in inventory, perish list will become empty
                event_list[1] = np.inf
            else:  # after this perish, still positive inventory
                event_list[1] = min(perish_list)

        elif idx == 3:  # order cancellation, happens only when n<0
            n += 1
            n_minus += 1
            q_minus += (t1 - t) * (n - 1)
            patience_list.remove(event_list[idx])
            if n == 0:  # The canceled order is the only one in queue, patience list will become empty
                event_list[3] = np.inf
            else:  # after this order cancel, still exists backorders
                event_list[3] = min(patience_list)

        t = t1  # update the current time point
plt.step(all_event_time_list[:300], n_list[1:301])
plt.show()

