import nuke
import nukescripts
from nukescripts import *
import json



########################################################################
####						PANEL									####
########################################################################

class Rms(nukescripts.PythonPanel):

	def __init__(self):

		nukescripts.PythonPanel.__init__( self, 'readMyScript', 'com.romainbouvard.Rms')

		### MAIN UI ###
		self.addKnob(nuke.PyScript_Knob("convert all Nodes in Black", "allBlack", 'readMyScript.Rms.allBlack()'))
		self.addKnob(nuke.PyScript_Knob("back to default", "Clear",'readMyScript.Rms.clear()'))
		self.addKnob(nuke.Text_Knob("divName","",""))

		#Convert to Selection:
		self.addKnob(nuke.PyScript_Knob("convert as a Selection", 'convertToSelection', 'readMyScript.Rms.convertToSelection()'))		
		self.addKnob(nuke.Text_Knob("divName","",""))

		#Search by Category:
			#Class
		self.addKnob(nuke.PyScript_Knob("search by Class", 'Class', 'readMyScript.Rms.searchClass()'))
		self.searchClassID = nuke.String_Knob('')
		self.searchClassID.clearFlag(nuke.STARTLINE)
		self.addKnob(self.searchClassID)
			#Name
		self.searchNameBt = (nuke.PyScript_Knob("Search by Name", 'Name', 'readMyScript.Rms.searchName()'))
		self.searchNameBt.setFlag(nuke.STARTLINE)
		self.addKnob(self.searchNameBt)
		self.searchNameID = nuke.String_Knob('')
		self.searchNameID.clearFlag(nuke.STARTLINE)
		self.addKnob(self.searchNameID)
		self.addKnob(nuke.Text_Knob("divName","",""))

		#Channel Selection:
		self.addKnob(nuke.PyScript_Knob("list Channels in Script ", 'listChannel', 'readMyScript.Rms.listChannel()'))
		self.addKnob(nuke.PyScript_Knob("Nodes more than RGBA", 'not RGBA', 'readMyScript.Rms.notRGBA()'))
		self.addKnob(nuke.PyScript_Knob("Filter via a maskChannel", 'masked Channels', 'readMyScript.Rms.maskChannel()'))
		self.addKnob(nuke.Text_Knob("divName","",""))

		#OverSize Bbox:
		self.addKnob(nuke.PyScript_Knob("Bbox compare to Input Size", 'oversizeBbox', 'readMyScript.Rms.oversizeBbox()'))
		self.slider = nuke.Double_Knob('')
		self.slider.setRange(1,2)
		self.slider.setValue(1.25)
		self.slider.clearFlag(nuke.STARTLINE)
		self.addKnob(self.slider)
		self.addKnob(nuke.Text_Knob("divName","",""))

		#Channel Filter:
		self.addKnob(nuke.PyScript_Knob("apply on filter All, e.g. Blur", 'filterAll', 'readMyScript.Rms.filterAll()'))
		self.addKnob(nuke.PyScript_Knob("mixKnob not default", 'mixKnob', 'readMyScript.Rms.mixKnob()'))	
		self.addKnob(nuke.Text_Knob("divName","",""))

		#Input / Output:
		self.addKnob(nuke.PyScript_Knob("Hidden Input", 'inputHide', 'readMyScript.Rms.inputHide()'))
		self.addKnob(nuke.PyScript_Knob("no Output", 'noOutput', 'readMyScript.Rms.noOutput()'))
		self.addKnob(nuke.PyScript_Knob("B Branch", 'mainInput', 'readMyScript.Rms.mainInput()'))
		self.addKnob(nuke.Text_Knob("divName","",""))

		#Animation/Tag:
		self.addKnob(nuke.PyScript_Knob("Animated Nodes", 'Animated', 'readMyScript.Rms.AnimationNodes()'))
		self.addKnob(nuke.PyScript_Knob("tag", 'tag', 'readMyScript.Rms.tag()'))		
		self.addKnob(nuke.PyScript_Knob("Disabled Nodes", 'Disable', 'readMyScript.Rms.Disable()'))
		self.addKnob(nuke.Text_Knob("divName","",""))
				
		# dictionaries and colors:
		self.dicOrigin = {}
		self.dicModif = {}
		self.darkColor = self.hexColor(0.25,0.25,0.25)
		self.goodColor = self.hexColor(0,1,0)

	# CORE TOOLS
	# Structure: /1-Edit(value) /2-Store-Restore /3-ColorList 

	def hexColor(self,r,g,b):
		value = int('%02x%02x%02x%02x' % (r*255,g*255,b*255,1),16)
		return value

	def edit (self,value):
		self.value = value
		if value == 0:
			self.store()
			self.colorList()
		else:
			self.restore()

	def store(self):
		for i in nuke.allNodes():
			color = i.knob('tile_color').value()
			name = i.name()
			self.dicOrigin[name] = color			
		return self.dicOrigin

	def restore(self):
		for i in nuke.allNodes():
			name = i.name()
			color= i.knob('tile_color').value()
			i.knob('tile_color').setValue(self.dicOrigin.get(name, color))
		self.dicOrigin.clear()
		self.dicModif.clear()
		return self.dicOrigin, self.dicModif

	def colorList(self):
		# Recolor The node
		for i in nuke.allNodes():
			name = i.name()
			color = i.knob('tile_color').value()
			i.knob('tile_color').setValue(self.dicModif.get(name, color))

	# UTILITIES
	# Structure: /1-CleanData /2-SearchData /3-StoreData /4-RevealData

	def allBlack(self):
		#clean Data
		self.edit(1)
		#search Data
		for i in nuke.allNodes():
			#self.otherNodes.append(i)
			name = i.name()
			self.dicModif[name] = self.darkColor
		#Store Data + Reveal Data
		self.edit(0)

	def clear(self):
		self.edit(1)

	def convertToSelection(self):
		for i in nuke.allNodes():
			name = i.name()
			if self.dicModif[name] != self.darkColor:
				i.knob("selected").setValue(True)
		#clean Data
		self.edit(1)

	def searchClass(self):
		#Restore Data
		self.edit(1)
		#Find Data
		searchClass = self.searchClassID.value()
		for i in nuke.allNodes():
			name = i.name()
			if searchClass in name:
				self.dicModif[name] = self.goodColor
			else:
				self.dicModif[name] = self.darkColor
		#Store Data
		self.edit(0)

	def searchName(self):
		#Restore Data
		self.edit(1)

		#Find Data
		searchName = self.searchNameID.value()
		for i in nuke.allNodes():
			name = i.name()
			if searchName in name:
				self.dicModif[name] = self.goodColor
			else:
				self.dicModif[name] = self.darkColor

		#Store Data
		self.edit(0)

	def listChannel(self):
		self.edit(1)
		L = nuke.layers()
		p = nuke.Panel( 'all Channels' )
		p.addEnumerationPulldown( 'mySelection', ' '.join( L ) )
		if not p.show():
			return
		else:
			layer = p.value('mySelection')
		#for Loop in AllNodes
		if layer:
			for i in nuke.allNodes():
				name = i.name()
				channels = i.channels()
				allLayers = list( set([c.split('.')[0] for c in channels]) )
				if layer in allLayers:
					self.dicModif[name] = self.goodColor
				else:
					self.dicModif[name] = self.darkColor
		#Store Data
		self.edit(0)

	def notRGBA(self):
		self.edit(1)
		# For Channels:
		rgba = ['rgba.red', 'rgba.green', 'rgba.blue', 'rgba.alpha']
		rgb = ['rgba.red', 'rgba.green', 'rgba.blue']
		alpha = ['rgba.alpha']
		empty = []
		allChannels = [rgba] + [rgb] + [alpha] + [empty]

		#Find Data
		for i in nuke.allNodes():
			name = i.name()
			channels = i.channels()
			layers = list( set([c.split('.')[0] for c in channels]) )
			if not channels in allChannels:
				self.dicModif[name] = self.goodColor
			else:
				self.dicModif[name] = self.darkColor

		#Store Data
		self.edit(0)

	def maskChannel(self):
		self.edit(1)
		for i in nuke.allNodes():
			name = i.name()
			if i.knob('maskChannelInput'):
				if i['maskChannelInput'].value() != 'none':
					self.dicModif[name] = self.goodColor
				else:
					self.dicModif[name] = self.darkColor
			else:
				self.dicModif[name] = self.darkColor
		#Store Data
		self.edit(0)

	def filterAll(self):
		self.edit(1)
		for i in nuke.allNodes():
			name = i.name()
			if i.knob('channel'):
				if i['channel'].value() == 'all':
					self.dicModif[name] = self.goodColor
				else:
					self.dicModif[name] = self.darkColor
			else:
				self.dicModif[name] = self.darkColor
		#Store Data
		self.edit(0)

	def oversizeBbox(self):
		self.edit(1)
		#Find Percent Slider
		percentValue = self.slider.value()
		# For loop in allNodes
		for i in nuke.allNodes():
			name = i.name()
			if i.bbox().w() > percentValue*i.width() or i.bbox().h() > percentValue*i.height():
				self.dicModif[name] = self.goodColor
			else:
				self.dicModif[name] = self.darkColor
		#Store Data
		self.edit(0)

	def mixKnob(self):
		self.edit(1)
		for i in nuke.allNodes():
			name = i.name()
			if i.knob('mix'):
				x = i.knob('mix')
				value = x.value()
				if value != 1:
					self.dicModif[name] = self.goodColor
				else:
					self.dicModif[name] = self.darkColor
			else:
				self.dicModif[name] = self.darkColor
		#Store Data
		self.edit(0)

	def inputHide(self):
		self.edit(1)
		for n in nuke.allNodes():
			name = n.name()
			if n.knob('hide_input'):
				if n.Class() != 'Viewer':
					x = n.knob('hide_input')
					value = x.value()
					if value == 0:
						self.dicModif[name] = self.darkColor
					else:
						self.dicModif[name] = self.goodColor
						n.setSelected(1)
						dependenciesOfWrite = nuke.dependencies([n])
						for d in dependenciesOfWrite:
							self.dicModif[name] = self.goodColor
			else:
				self.dicModif[name] = self.darkColor
		#Add Viewer Nodes
		viewer = nuke.allNodes('Viewer')
		for i in viewer:
			name = i.name()
			self.dicModif[name] = self.darkColor
		#Store Data
		self.edit(0)

	def noOutput(self):
		self.edit(1)
		for a in nuke.allNodes():
			name = a.name()
			x = a.dependent()
			y = a.dependencies()
			if y == []:
				self.dicModif[name] = self.darkColor

			else:
				if a.inputs():
					if x == []:
						self.dicModif[name] = self.goodColor
					else:
						self.dicModif[name] = self.darkColor
				else:
					self.dicModif[name] = self.darkColor

		#Add Viewer Nodes
		viewer = nuke.allNodes('Viewer')
		for i in viewer:
			name = i.name()
			self.dicModif[name] = self.darkColor
		#Store Data
		self.edit(0)

	def AnimationNodes(self):
		self.edit(1)
		def isAnimated(node):
			return bool(int(node['indicators'].value()) & 1)

		for n in nuke.allNodes():
			name = n.name()
			if isAnimated(n) == True:
				self.dicModif[name] = self.goodColor
			else:
				self.dicModif[name] = self.darkColor
		#Store Data
		self.edit(0)

	def tag(self):
		self.edit(1)
		for i in nuke.allNodes():
			name = i.name()
			if name[:3] == "tag":
				self.dicModif[name] = self.goodColor
			else:
				self.dicModif[name] = self.darkColor
		#Store Data
		self.edit(0)

	def mainInput(self):
		def climb(node):
			#Start Node:
			thisNode = [node]
			# find if dependency exist and add thisNode to the list:
			for n in thisNode:
				input = n.input(0)
				goodNodes.append(n)
				# Loop if dependency still exist:
				if input:
					climb(input)
					return goodNodes
		
		self.edit(1)
		a = nuke.selectedNode()
		if not a == None:
			goodNodes = []
			climb(a)
			#Recolor D
			if goodNodes != None:
				for i in nuke.allNodes():
					name = i.name()
					self.dicModif[name] = self.darkColor
				for i in goodNodes:
					name = i.name()
					self.dicModif[name] = self.goodColor
		else:
			nuke.message('please select a node')
		#Store Data
		self.edit(0)

	def Disable(self):
		self.edit(1)
		for i in nuke.allNodes():
			name = i.name()
			if i.knob('disable'):
				select = i['disable'].value()
				if select:
					self.dicModif[name] = self.goodColor
				else:
					self.dicModif[name] = self.darkColor
			else:
				self.dicModif[name] = self.darkColor
		#Store Data
		self.edit(0)

def add_RmsPanel():
	global Rms
	Rms = Rms()
	return Rms.addToPane()

paneMenu = nuke.menu( 'Pane' )
paneMenu.addCommand( 'Rms', add_RmsPanel )
nukescripts.registerPanel('com.romainbouvard.Rms', add_RmsPanel )