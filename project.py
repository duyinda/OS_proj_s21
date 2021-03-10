import sys, types, time, random, os
import scheduler2 as scheduler
import process
import math
import copy
import random


class Rand48(object):
	def __init__(self, seed):
		self.n = seed
	def seed(self, seed):
		self.n = seed
	def srand(self, seed):
		self.n = (seed << 16) + 0x330e
	def next(self):
		self.n = (25214903917 * self.n + 11) & (2**48 - 1)
		'''print("n "+str(self.n))'''
		return self.n
	def drand(self):
		return float(self.next())/float((2**48))
	def lrand(self):
		return self.next() >> 17
	def mrand(self):
		n = self.next() >> 16
		if n & (1 << 31):
			n -= 1 << 32
		return n   

def rand(rand48,Lambda,upper_bound):
	while(1):
		r=rand48.drand()
		'''r = random.random()'''
		if r==0: continue
		x = (-math.log(r))/Lambda
		if x>upper_bound: continue
		else: return x


if __name__ == '__main__':
	debug = 0

	seed = int(sys.argv[1] )
	Lambda = float(sys.argv[2])
	upper_bound = int(sys.argv[3])
	process_num = int(sys.argv[4])
	context_switch = int(sys.argv[5])
	alpha = float(sys.argv[6])
	t_slice = int(sys.argv[7])
	if len(sys.argv) >8:
		end_beginning = sys.argv[8]
	random.seed(seed)
	rand48 = Rand48(seed)
	rand48.srand(seed)
	processes = []

	totalBurstNum = 0
	simulators = []

	for i in range(int(process_num)):
		time = 0
		process_name = chr(ord('@')+int(i)+1)
		arrival_time = int(math.floor(rand(rand48, float(Lambda), int(upper_bound))))
		burst_num = int(math.floor(rand48.drand()*100)+1)
		totalBurstNum +=burst_num
		bursts = []
		for j in range(burst_num):
			CPUburstTime = int(math.ceil(rand(rand48,Lambda,upper_bound)))
			CPUburst = process.Burst(process_name,"CPU",CPUburstTime)
			bursts.append(CPUburst)
			if j!=burst_num-1:
				IOburstTime = int(math.ceil(rand(rand48,Lambda,upper_bound)))
				IOburst = process.Burst(process_name,"IO",IOburstTime)
				bursts.append(IOburst)

		processes.append( process.Process(process_name, burst_num, arrival_time,bursts))
	
	for p in processes:
		p.initializeTau(Lambda,alpha)
		
	
	
	fcfs = scheduler.FCFS("FCFS")
	sjf=scheduler.SJF("SJF")
	srt=scheduler.SRT("SRT")
	rr = scheduler.RR("RR",t_slice)
	simulatorFCFS = scheduler.Simulator(1,context_switch,t_slice, fcfs,copy.deepcopy(processes))
	simulatorRR = scheduler.Simulator(1,context_switch,t_slice, rr,copy.deepcopy(processes))
	simulatorSJF = scheduler.Simulator(1,context_switch,t_slice, sjf,copy.deepcopy(processes))
	simulatorSRT = scheduler.Simulator(1,context_switch,t_slice, srt,copy.deepcopy(processes))
	simulators.append(simulatorFCFS)
	
	simulators.append(simulatorSJF)
	
	simulators.append(simulatorSRT)
	
	simulators.append(simulatorRR)
	
	for simulator in simulators:
		for p in processes:
			print('Process '+str(p.getId())+' [NEW] (arrival time '+str(p.getArrivalTime())+' ms) '+str(p.getNumBursts())+' CPU bursts')
	
		while(1):
			terminate = simulator.run()
			if debug == 1:
				print("time "+str(simulator.getTime())+"ms: "+"ready:" +str(simulator.getReady())+"running: "+str(simulator.getRunning())+"blocked: "+str(simulator.getBlocked()))
				print("contextSwitchOut " +str(simulator.getContextSwitchOut())+"contextSwitchIn " +str(simulator.getContextSwitchIn()))
			if terminate == 1:
				break    
	




	f= open("simout.txt","w+")
	for simulator in simulators:
		f.write("Algorithm "+simulator.getName())
		f.write("\n")
		f.write("-- average CPU burst time: "+"%.3f" %(simulator.getTotalBurstTime()/float(totalBurstNum))+" ms\n")
		f.write("-- average wait time: "+"%.3f" %(float(simulator.getTotalWaitTime()+simulator.getNumPreemptions()*context_switch/2)/float(totalBurstNum)  )+" ms\n")
		f.write("-- average turnaround time: "+"%.3f" %(float(simulator.getTotalTurnaroundTime()+simulator.getNumPreemptions()*context_switch/2)/float(totalBurstNum))+" ms\n")
		f.write("-- total number of context switches: "+str(simulator.getNumContextSwitches())+"\n")
		f.write("-- total number of preemptions: "+str(simulator.getNumPreemptions())+"\n")
	f.close()