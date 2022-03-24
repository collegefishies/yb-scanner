from objc_util import *
from ctypes import c_void_p
import ui
import sound

class barcodeScanner():
	'''
	'''

	def __init__():
		#wrap c objects in python
		self.AVCaptureSession = ObjCClass('AVCaptureSession')
		self.AVCaptureDevice = ObjCClass('AVCaptureDevice')
		self.AVCaptureDeviceInput = ObjCClass('AVCaptureDeviceInput')
		self.AVCaptureMetadataOutput = ObjCClass('AVCaptureMetadataOutput')
		self.AVCaptureVideoPreviewLayer = ObjCClass('AVCaptureVideoPreviewLayer')
		dispatch_get_current_queue = c.dispatch_get_current_queue
		dispatch_get_current_queue.restype = c_void_p

		def captureOutput_didOutputMetadataObjects_fromConnection_(_self, _cmd, _output, _metadata_objects, _conn):
			'''
				Reads strings from our QR code scans. Adds found codes into `found_codes'.
			'''
			objects = ObjCInstance(_metadata_objects)
			for obj in objects:
				try:
					s = str(obj.stringValue())
					if s not in found_codes:
						found_codes.add(s)
						sound.play_effect('digital:PowerUp7')
					main_view['label'].text = 'Last scan: ' + s
				except:
					pass

		self.MetadataDelegate = create_objc_class(
			'MetadataDelegate', 
			methods=[captureOutput_didOutputMetadataObjects_fromConnection_], 
			protocols=['AVCaptureMetadataOutputObjectsDelegate']
		)
		
	@on_main_thread
	def main():
		global main_view

		#create delegate object
		delegate = self.MetadataDelegate.new()

		#create ui object
		main_view = ui.View(frame=(0, 0, 400, 400))
		main_view.name = 'Barcode Scanner'

		#create resources for reading from camera
		session = self.AVCaptureSession.alloc().init()
		device = self.AVCaptureDevice.defaultDeviceWithMediaType_('vide')
		_input = self.AVCaptureDeviceInput.deviceInputWithDevice_error_(device, None)
		if _input:
			session.addInput_(_input)
		else:
			print('Failed to create input')
			return

		#create resources for read data
		output = self.AVCaptureMetadataOutput.alloc().init()
		
		queue = ObjCInstance(dispatch_get_current_queue())
		output.setMetadataObjectsDelegate_queue_(delegate, queue)
		session.addOutput_(output)
		output.setMetadataObjectTypes_(output.availableMetadataObjectTypes())
		prev_layer = self.AVCaptureVideoPreviewLayer.layerWithSession_(session)
		prev_layer.frame = ObjCInstance(main_view).bounds()
		prev_layer.setVideoGravity_('AVLayerVideoGravityResizeAspectFill')
		ObjCInstance(main_view).layer().addSublayer_(prev_layer)
		label = ui.Label(frame=(0, 0, 400, 30), flex='W', name='label')
		label.background_color = (0, 0, 0, 0.5)
		label.text_color = 'white'
		label.text = 'Nothing scanned yet'
		label.alignment = ui.ALIGN_CENTER
		main_view.add_subview(label)
		session.startRunning()
		main_view.present('sheet')
		main_view.wait_modal()
		session.stopRunning()
		delegate.release()
		session.release()
		output.release()
		if found_codes:
			print('All scanned codes:\n' + '\n'.join(found_codes))
		
class barcodeTransmitter():
	pass

if __name__ == '__main__':
	bc = barcodeScanner()
	bc.main()