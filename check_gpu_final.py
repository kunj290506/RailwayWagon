
import torch
import sys

print(f"Python: {sys.version}")
print(f"Torch: {torch.__version__}")
try:
    print(f"CUDA Available: {torch.cuda.is_available()}")
    if torch.cuda.is_available():
        print(f"Device: {torch.cuda.get_device_name(0)}")
        t = torch.tensor([1,2,3]).cuda()
        print("Tensor successfully created on GPU!")
    else:
        print("CUDA NOT AVAILABLE.")
except Exception as e:
    print(f"Error: {e}")
