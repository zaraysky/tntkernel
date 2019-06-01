from ipykernel.kernelapp import IPKernelApp
from .tntkernel import TNTKernel
IPKernelApp.launch_instance(kernel_class=TNTKernel)
