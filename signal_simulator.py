'''
Copyright by:
	Sudiro
		[at] SudiroEEN@gmail.com
'''


import sys
from PyQt5.QtWidgets import (QLineEdit, QLabel, QPushButton,
							 QSlider, QComboBox, QApplication,
							 QVBoxLayout, QHBoxLayout,QWidget)

from PyQt5.QtCore import Qt, pyqtSlot, QThread, pyqtSignal
from PyQt5.QtGui import QIcon
from pyqtgraph import PlotWidget, plot
import pyqtgraph as pg 

import numpy as np 
import threading
import time

class myGUI(QWidget):
	def __init__(self):
		super().__init__()
		self.init_param()
		self.init_gui()

		self.work_thread = self.Worker(self)
		self.work_thread.signal.connect(self.simulate)
		self.work_thread.start()

	def init_param(self):
		self.kind_sig = "Step"
		self.kind_val = "Amplitude"
		self.delay_ = .0
		self.ampSlope = .0
		self.start_time = .0
		self.sim_active = False

	def init_gui(self):
		self.gw = pg.PlotWidget()

		self.lbSigType = QLabel("Signal Type")
		self.cb = QComboBox()
		self.cb.addItem("Step")
		self.cb.addItem("Ramp")
		self.cb.addItem("Example Sinus")
		self.cb.currentIndexChanged.connect(self.cb_clk)

		self.lbAmpSig = QLabel(self.kind_val)
		self.sd = QSlider(Qt.Horizontal)
		self.sd.setMinimum(0)
		self.sd.setMaximum(100)
		self.sd.setValue(1)
		self.sd.setTickInterval(10)
		self.sd.setTickPosition(QSlider.TicksBelow)
		self.sd.valueChanged.connect(self.sd_clk)

		self.lbDelay = QLabel("delay")
		self.leDelay = QLineEdit()

		self.lbStartTime = QLabel("Start Time")
		self.leStartTime = QLineEdit()

		self.pbRun = QPushButton(QIcon("icon/execute.png"), "Run")
		self.pbRun.clicked.connect(self.pbRun_clk)

		self.pbStop = QPushButton(QIcon("icon/stop.jpg"), "Stop")
		self.pbStop.clicked.connect(self.pbStop_clk)

		vbox1 = QVBoxLayout()
		vbox1.addWidget(self.lbSigType)
		vbox1.addWidget(self.lbAmpSig)
		vbox1.addWidget(self.lbDelay)
		vbox1.addWidget(self.lbStartTime)

		vbox2 = QVBoxLayout()
		vbox2.addWidget(self.cb)
		vbox2.addWidget(self.sd)
		vbox2.addWidget(self.leDelay)
		vbox2.addWidget(self.leStartTime)

		vbox3 = QVBoxLayout()
		vbox3.addWidget(self.pbRun)
		vbox3.addWidget(self.pbStop)

		hbox = QHBoxLayout()
		hbox.addLayout(vbox1)
		hbox.addLayout(vbox2)
		hbox.addLayout(vbox3)

		vbox_main = QVBoxLayout()
		vbox_main.addWidget(self.gw)
		vbox_main.addLayout(hbox)

		self.setLayout(vbox_main)
		self.setWindowTitle("Signal Simulator")
		self.show()

	def cb_clk(self):
		self.kind_sig = self.cb.currentText()
		if self.kind_sig == 'Ramp':
			self.kind_val = "Slope"
		else:
			self.kind_val = "Amplitude"

		boolean = True
		if self.kind_sig == 'Example Sinus':
			boolean = False
		else:
			boolean = True

		self.sd.setEnabled(boolean)
		self.leStartTime.setEnabled(boolean)
		self.leDelay.setEnabled(boolean)

		self.lbAmpSig.setText(self.kind_val)

	def sd_clk(self):
		self.ampSlope = float(self.sd.value())

	def pbRun_clk(self):
		self.sim_active = True
		self.pbRun.setEnabled(False)

	def pbStop_clk(self):
		self.sim_active = False
		self.pbRun.setEnabled(True)

	@pyqtSlot(object)
	def simulate(self, data):
		data = np.array(data)
		self.gw.plot(data[:,0], data[:,1], clear=True)

	class Worker(QThread):
		signal = pyqtSignal(object)

		def __init__(self, outer_):
			super().__init__()
			self.outer_ = outer_
			self.time_val = list()
			self.value = .0
			self.time_ = .0

		def sig_gen(self):
			ks = self.outer_.kind_sig
			d = self.outer_.delay_
			A = self.outer_.ampSlope

			if ks == 'Step':
				if self.time_ > d:
					return A
				else:
					return 0.
			elif ks == 'Ramp':
				if self.time_ > d:
					return A*self.time_
				else:
					return 0.
			elif ks == 'Example Sinus':
				return np.sin(2.*np.pi*self.time_)

		def run(self):
			t0 = time.time()
			t1 = t0
			while True:
				if self.outer_.sim_active:
					if len(self.time_val) > 500:
						del self.time_val[0]

					t1 = time.time()
					self.time_ = t1 - t0 + self.outer_.start_time
					self.value = self.sig_gen()
					self.time_val.append([self.time_, self.value])

					self.signal.emit(self.time_val)
					time.sleep(0.01)

app = QApplication(sys.argv)
sigSim = myGUI()
sys.exit(app.exec_())
