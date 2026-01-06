"""
Export Model for NVIDIA Jetson Deployment
Supports: TorchScript, FP16 quantization, optimization
"""
import torch
import torch.nn as nn
import os
import argparse
import time
from models import GeneratorResNet


def export_to_torchscript(model, output_path, example_input):
    """Export model to TorchScript for efficient deployment"""
    print("Exporting to TorchScript...")
    model.eval()
    
    # Trace the model
    traced_model = torch.jit.trace(model, example_input)
    
    # Optimize for inference
    traced_model = torch.jit.optimize_for_inference(traced_model)
    
    # Save
    torch.jit.save(traced_model, output_path)
    print(f"✅ TorchScript model saved to: {output_path}")
    
    return traced_model


def export_fp16(model, output_path):
    """Export model with FP16 precision for Jetson"""
    print("Converting to FP16...")
    model.eval()
    model_fp16 = model.half()
    
    torch.save({
        'model_state_dict': model_fp16.state_dict(),
        'precision': 'fp16'
    }, output_path)
    
    print(f"✅ FP16 model saved to: {output_path}")
    return model_fp16


def benchmark_model(model, device, input_size=(1, 3, 256, 256), num_iterations=100):
    """Benchmark model inference speed"""
    print(f"\nBenchmarking on {device}...")
    model.eval()
    model = model.to(device)
    
    # Warmup
    dummy_input = torch.randn(input_size).to(device)
    for _ in range(10):
        with torch.no_grad():
            _ = model(dummy_input)
    
    # Benchmark
    times = []
    with torch.no_grad():
        for _ in range(num_iterations):
            if device.type == 'cuda':
                torch.cuda.synchronize()
            
            start = time.time()
            _ = model(dummy_input)
            
            if device.type == 'cuda':
                torch.cuda.synchronize()
            
            end = time.time()
            times.append((end - start) * 1000)  # Convert to ms
    
    avg_time = sum(times) / len(times)
    fps = 1000 / avg_time
    
    print(f"\nBenchmark Results ({num_iterations} iterations):")
    print(f"  Average inference time: {avg_time:.2f} ms")
    print(f"  FPS: {fps:.2f}")
    print(f"  Min time: {min(times):.2f} ms")
    print(f"  Max time: {max(times):.2f} ms")
    
    return avg_time, fps


def main():
    parser = argparse.ArgumentParser(description='Export Model for Jetson Deployment')
    parser.add_argument('--checkpoint', type=str, required=True, help='Path to checkpoint')
    parser.add_argument('--output_dir', type=str, default='jetson_export', help='Output directory')
    parser.add_argument('--fp16', action='store_true', help='Export FP16 version')
    parser.add_argument('--benchmark', action='store_true', help='Run benchmark')
    args = parser.parse_args()
    
    # Create output directory
    os.makedirs(args.output_dir, exist_ok=True)
    
    # Device
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Using device: {device}")
    
    # Load model
    print(f"\nLoading checkpoint from {args.checkpoint}...")
    generator = GeneratorResNet(
        in_channels=3,
        out_channels=3,
        n_residual_blocks=16
    )
    
    checkpoint = torch.load(args.checkpoint, map_location='cpu')
    if 'generator_state_dict' in checkpoint:
        generator.load_state_dict(checkpoint['generator_state_dict'])
        print(f"Loaded from epoch {checkpoint.get('epoch', 'N/A')}")
        print(f"Best PSNR: {checkpoint.get('best_psnr', 'N/A'):.4f} dB")
    else:
        generator.load_state_dict(checkpoint)
    
    generator.to(device)
    generator.eval()
    
    print("\n" + "="*80)
    print("MODEL EXPORT FOR JETSON")
    print("="*80)
    
    # Example input for tracing
    example_input = torch.randn(1, 3, 256, 256).to(device)
    
    # Export to TorchScript
    torchscript_path = os.path.join(args.output_dir, 'model_jetson.pt')
    traced_model = export_to_torchscript(generator, torchscript_path, example_input)
    
    # Get file size
    torchscript_size = os.path.getsize(torchscript_path) / (1024 * 1024)  # MB
    print(f"   Model size: {torchscript_size:.2f} MB")
    
    # Export FP16 if requested
    if args.fp16:
        print("\n" + "-"*80)
        fp16_path = os.path.join(args.output_dir, 'model_jetson_fp16.pth')
        model_fp16 = export_fp16(generator, fp16_path)
        fp16_size = os.path.getsize(fp16_path) / (1024 * 1024)
        print(f"   Model size: {fp16_size:.2f} MB")
        print(f"   Size reduction: {((torchscript_size - fp16_size) / torchscript_size * 100):.1f}%")
    
    # Benchmark if requested
    if args.benchmark:
        print("\n" + "-"*80)
        print("BENCHMARK - FP32")
        benchmark_model(generator, device)
        
        if args.fp16 and device.type == 'cuda':
            print("\n" + "-"*80)
            print("BENCHMARK - FP16")
            benchmark_model(model_fp16, device)
    
    # Create deployment README
    readme_path = os.path.join(args.output_dir, 'README_JETSON.md')
    with open(readme_path, 'w') as f:
        f.write("# Jetson Deployment Guide\n\n")
        f.write("## Model Files\n\n")
        f.write(f"- **TorchScript (FP32)**: `model_jetson.pt` ({torchscript_size:.2f} MB)\n")
        if args.fp16:
            f.write(f"- **FP16**: `model_jetson_fp16.pth` ({fp16_size:.2f} MB)\n")
        f.write("\n## Usage Example\n\n")
        f.write("```python\n")
        f.write("import torch\n")
        f.write("from PIL import Image\n")
        f.write("import torchvision.transforms as transforms\n\n")
        f.write("# Load model\n")
        f.write("device = torch.device('cuda')\n")
        f.write("model = torch.jit.load('model_jetson.pt').to(device)\n")
        f.write("model.eval()\n\n")
        f.write("# Prepare image\n")
        f.write("transform = transforms.Compose([\n")
        f.write("    transforms.Resize((256, 256)),\n")
        f.write("    transforms.ToTensor(),\n")
        f.write("    transforms.Normalize(mean=[0.5, 0.5, 0.5], std=[0.5, 0.5, 0.5])\n")
        f.write("])\n\n")
        f.write("img = Image.open('blurred.jpg').convert('RGB')\n")
        f.write("input_tensor = transform(img).unsqueeze(0).to(device)\n\n")
        f.write("# Inference\n")
        f.write("with torch.no_grad():\n")
        f.write("    output = model(input_tensor)\n\n")
        f.write("# Post-process\n")
        f.write("output = (output[0].cpu().numpy().transpose(1, 2, 0) + 1) / 2  # Denormalize\n")
        f.write("output = (output * 255).clip(0, 255).astype('uint8')\n")
        f.write("Image.fromarray(output).save('deblurred.jpg')\n")
        f.write("```\n\n")
        f.write("## Jetson Setup\n\n")
        f.write("### 1. Install PyTorch for Jetson\n")
        f.write("```bash\n")
        f.write("# For Jetson (use NVIDIA's PyTorch builds)\n")
        f.write("wget https://nvidia.box.com/shared/static/[version].whl\n")
        f.write("pip3 install torch-[version].whl\n")
        f.write("```\n\n")
        f.write("### 2. Copy model to Jetson\n")
        f.write("```bash\n")
        f.write("scp model_jetson.pt jetson@<jetson-ip>:~/models/\n")
        f.write("```\n\n")
        f.write("### 3. Run inference\n")
        f.write("```bash\n")
        f.write("python3 inference_jetson.py --model models/model_jetson.pt --input test.jpg\n")
        f.write("```\n\n")
        f.write("## Performance Notes\n\n")
        f.write("- **Target FPS**: 5-10 FPS on Jetson Xavier, 15-30 FPS on Jetson Orin\n")
        f.write("- **Memory**: ~500-700 MB GPU memory\n")
        f.write("- **Optimization**: Use FP16 for 2x speedup on Jetson\n")
        f.write("- **Batch Processing**: Can process batches of 2-4 images depending on Jetson model\n")
    
    print("\n" + "="*80)
    print("EXPORT COMPLETE!")
    print("="*80)
    print(f"Output directory: {args.output_dir}")
    print(f"Deployment guide: {readme_path}")
    print("="*80)


if __name__ == '__main__':
    main()
