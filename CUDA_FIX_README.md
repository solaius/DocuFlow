# DocuFlow CUDA Fix

This document explains how to fix the CUDA-related error in DocuFlow:

```
Could not load the custom kernel for multi-scale deformable attention: module 'distutils' has no attribute '_msvccompiler'
Could not load the custom kernel for multi-scale deformable attention: DLL load failed while importing MultiScaleDeformableAttention: The specified module could not be found.
```

## Quick Fix

Run the provided fix script:

```bash
python fix_cuda_msda.py
```

This script will:
1. Patch the RT-DETR model to use CPU implementation for MultiScaleDeformableAttention
2. Set the necessary environment variables
3. Create a startup script for Windows

## Manual Fix

If you prefer to fix the issue manually, you can:

1. Set the environment variable to force CPU implementation:
   ```bash
   # On Windows
   set DOCLING_FORCE_CPU_MSDA=1
   
   # On Linux/Mac
   export DOCLING_FORCE_CPU_MSDA=1
   ```

2. Add this environment variable to your `.env` file:
   ```
   DOCLING_FORCE_CPU_MSDA=1
   ```

## What's Happening?

The error occurs because the custom CUDA kernel for MultiScaleDeformableAttention can't be loaded. This can happen for several reasons:

1. Missing CUDA toolkit
2. Incompatible CUDA version
3. Missing Visual C++ compiler on Windows
4. Path issues with the DLL files

The fix works by replacing the CUDA implementation with a CPU implementation, which is slower but more compatible.

## Alternative Solutions

If you want to use the CUDA implementation for better performance, you can try:

1. Install the correct CUDA toolkit version (12.1)
2. Install Visual C++ Build Tools
3. Add CUDA bin directory to your PATH
4. Rebuild the custom CUDA extensions

## Need Help?

If you encounter any issues with this fix, please open an issue on the repository.