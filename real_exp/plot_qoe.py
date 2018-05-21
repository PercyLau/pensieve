import os
import numpy as np
import matplotlib.pyplot as plt

RESULTS_FOLDER = './results/'
SCHEMES = ['RL']
BITS_IN_BYTE = 8.0
MILLISEC_IN_SEC = 1000.0
M_IN_B = 1000000.0
REBUF_PENALTY = 4.3


# Note that we are only interested in QoE lin, and so will only compute using
# that metric.
# QoE = sum(q(R_n)) - u*sum(T_n) - sum(q(R_n) - q(R_n+1))
def main():

    time_all = {}
    bit_rate_all = {}
    buff_all = {}
    bw_all = {}
    raw_reward_all = {}
    qoe_all = {}

    for scheme in SCHEMES:
        time_all[scheme] = {}
        raw_reward_all[scheme] = {}
        bit_rate_all[scheme] = {}
        buff_all[scheme] = {}
        bw_all[scheme] = {}
        qoe_all[scheme] = {}

    log_files = os.listdir(RESULTS_FOLDER)
    for log_file in log_files:

        time_ms = []
        bit_rate = []
        buff = []
        bw = []
        reward = []
        qoe_val = 0.0


        with open(RESULTS_FOLDER + log_file, 'rb') as f:
            for line in f:
                parse = line.split()
                if len(parse) <= 1:
                        break
                time_ms.append(float(parse[0]))
                bit_rate.append(int(parse[1]))
                buff.append(float(parse[2]))
                bw.append(float(parse[4]) / float(parse[5]) * BITS_IN_BYTE * MILLISEC_IN_SEC / M_IN_B)
                reward.append(float(parse[6]))

        # Compute QoE metric
        # QoE = sum(q(R_n)) - u*sum(T_n) - sum(q(R_n) - q(R_n+1))
        bitrate_sum = np.sum(bit_rate) / 1000.0
        print "Bitrate sum: ", bitrate_sum
        rebuffer_sum = np.sum(buff) / 1000.0
        print "Rebuffer sum: ", rebuffer_sum
        bitrate_diff_sum = 0
        for i in range(len(bit_rate)-1):
            bitrate_diff_sum += abs(bit_rate[i] - bit_rate[i+1])
        bitrate_diff_sum = bitrate_diff_sum / 1000.0
        print "Bitrate diff sum: ", bitrate_diff_sum
        qoe_val = bitrate_sum - REBUF_PENALTY * rebuffer_sum - bitrate_diff_sum
        qoe_val_normalized = qoe_val / len(bit_rate)
        print "Computed QoE metric of: ", qoe_val
        print "Computed normalized QoE metric of: ", qoe_val_normalized

        time_ms = np.array(time_ms)
        time_ms -= time_ms[0]
        for scheme in SCHEMES:
            if scheme in log_file:
                log_file_id = log_file[len('log_' + str(scheme) + '_'):]
                time_all[scheme][log_file_id] = time_ms
                bit_rate_all[scheme][log_file_id] = bit_rate
                buff_all[scheme][log_file_id] = buff
                bw_all[scheme][log_file_id] = bw
                raw_reward_all[scheme][log_file_id] = reward
                qoe_all[scheme][log_file_id] = qoe_val_normalized
                break
            else:
                print "Did not match scheme to logfile"

if __name__ == '__main__':
    main()
