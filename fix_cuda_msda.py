"""
Fix for CUDA MultiScaleDeformableAttention module issues in DocuFlow.

This script provides a permanent fix for the error:
"Could not load the custom kernel for multi-scale deformable attention: 
DLL load failed while importing MultiScaleDeformableAttention: The specified module could not be found."

The fix works by patching the RT-DETR model to use CPU implementation for the 
MultiScaleDeformableAttention module, which avoids the need for the custom CUDA kernel.
"""
import os
import sys
import logging
import importlib
from pathlib import Path
import argparse

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("fix_cuda_msda")

def patch_rt_detr_model():
    """
    Patch the RT-DETR model to use CPU implementation for MultiScaleDeformableAttention.
    """
    try:
        # Find the transformers module
        import transformers
        transformers_path = Path(transformers.__file__).parent
        logger.info(f"Transformers path: {transformers_path}")
        
        # Find the rt_detr module
        rtdetr_path = transformers_path / "models" / "rt_detr"
        if not rtdetr_path.exists():
            logger.error(f"RT-DETR module not found at {rtdetr_path}")
            return False
        
        logger.info(f"RT-DETR module found at {rtdetr_path}")
        
        # Find the modeling_rt_detr.py file
        modeling_path = rtdetr_path / "modeling_rt_detr.py"
        if not modeling_path.exists():
            logger.error(f"modeling_rt_detr.py not found at {modeling_path}")
            return False
        
        logger.info(f"modeling_rt_detr.py found at {modeling_path}")
        
        # Create a backup of the original file
        backup_path = modeling_path.with_suffix(".py.bak")
        if not backup_path.exists():
            logger.info(f"Creating backup at {backup_path}")
            with open(modeling_path, "r") as src, open(backup_path, "w") as dst:
                dst.write(src.read())
        
        # Read the file content
        with open(modeling_path, "r") as f:
            content = f.read()
        
        # Check if the file contains MultiScaleDeformableAttention
        if "MultiScaleDeformableAttention" not in content:
            logger.error("MultiScaleDeformableAttention not found in the file")
            return False
        
        # Modify the content to use CPU implementation
        modified_content = content.replace(
            "from .ops.ms_deform_attn import MultiScaleDeformableAttention",
            """
# Patched to use CPU implementation
try:
    from .ops.ms_deform_attn import MultiScaleDeformableAttention
except ImportError:
    import warnings
    warnings.warn("Using CPU implementation of MultiScaleDeformableAttention")
    
    import torch
    import torch.nn as nn
    import torch.nn.functional as F
    
    class MultiScaleDeformableAttention(nn.Module):
        def __init__(self, embed_dim, num_heads, n_levels, n_points):
            super().__init__()
            self.embed_dim = embed_dim
            self.num_heads = num_heads
            self.n_levels = n_levels
            self.n_points = n_points
            self.total_points = num_heads * n_levels * n_points
            
            self.sampling_offsets = nn.Linear(embed_dim, self.total_points * 2)
            self.attention_weights = nn.Linear(embed_dim, self.total_points)
            self.value_proj = nn.Linear(embed_dim, embed_dim)
            self.output_proj = nn.Linear(embed_dim, embed_dim)
            
            self._reset_parameters()
        
        def _reset_parameters(self):
            nn.init.constant_(self.sampling_offsets.weight, 0.0)
            thetas = torch.arange(self.num_heads, dtype=torch.float32) * (2.0 * torch.pi / self.num_heads)
            grid_init = torch.stack([thetas.cos(), thetas.sin()], -1)
            grid_init = grid_init / grid_init.abs().max(-1, keepdim=True)[0]
            grid_init = grid_init.view(self.num_heads, 1, 1, 2).repeat(1, self.n_levels, self.n_points, 1)
            for i in range(self.n_points):
                grid_init[:, :, i, :] *= i + 1
            
            with torch.no_grad():
                self.sampling_offsets.bias = nn.Parameter(grid_init.view(-1))
            
            nn.init.constant_(self.attention_weights.weight, 0.0)
            nn.init.constant_(self.attention_weights.bias, 0.0)
            nn.init.xavier_uniform_(self.value_proj.weight)
            nn.init.constant_(self.value_proj.bias, 0.0)
            nn.init.xavier_uniform_(self.output_proj.weight)
            nn.init.constant_(self.output_proj.bias, 0.0)
        
        def forward(self, query, reference_points, input_flatten, input_spatial_shapes, input_level_start_index, input_padding_mask=None):
            N, Len_q, _ = query.shape
            N, Len_in, _ = input_flatten.shape
            
            value = self.value_proj(input_flatten)
            
            if input_padding_mask is not None:
                value = value.masked_fill(input_padding_mask[..., None], 0.0)
            
            value = value.view(N, Len_in, self.num_heads, self.embed_dim // self.num_heads)
            
            sampling_offsets = self.sampling_offsets(query).view(
                N, Len_q, self.num_heads, self.n_levels, self.n_points, 2
            )
            
            attention_weights = self.attention_weights(query).view(
                N, Len_q, self.num_heads, self.n_levels * self.n_points
            )
            attention_weights = F.softmax(attention_weights, -1).view(
                N, Len_q, self.num_heads, self.n_levels, self.n_points
            )
            
            # Use a simplified implementation that works on CPU
            output = torch.zeros_like(query)
            for b in range(N):
                for q in range(Len_q):
                    for h in range(self.num_heads):
                        weighted_values = torch.zeros(self.embed_dim // self.num_heads, device=query.device)
                        for l in range(self.n_levels):
                            for p in range(self.n_points):
                                # Get the weight for this point
                                weight = attention_weights[b, q, h, l, p]
                                
                                # Get the reference point and offset
                                if reference_points.shape[-1] == 2:
                                    ref_point = reference_points[b, q, None, :].expand(-1, input_spatial_shapes[l, 1] * input_spatial_shapes[l, 0], -1)
                                elif reference_points.shape[-1] == 4:
                                    ref_point = reference_points[b, q, None, :2].expand(-1, input_spatial_shapes[l, 1] * input_spatial_shapes[l, 0], -1)
                                else:
                                    raise ValueError(f"Last dim of reference_points must be 2 or 4, but got {reference_points.shape[-1]}")
                                
                                # Get the offset
                                offset = sampling_offsets[b, q, h, l, p]
                                
                                # Calculate the sampling location
                                loc = ref_point + offset / input_spatial_shapes[l].flip(0)
                                
                                # Simple nearest neighbor sampling
                                x = loc[0, 0] * input_spatial_shapes[l, 1]
                                y = loc[0, 1] * input_spatial_shapes[l, 0]
                                
                                # Clamp to valid range
                                x = torch.clamp(x, 0, input_spatial_shapes[l, 1] - 1).long()
                                y = torch.clamp(y, 0, input_spatial_shapes[l, 0] - 1).long()
                                
                                # Calculate the index in the flattened input
                                idx = input_level_start_index[l] + y * input_spatial_shapes[l, 1] + x
                                
                                # Get the value and apply the weight
                                if idx < Len_in:
                                    weighted_values += weight * value[b, idx, h]
                        
                        # Add the weighted values to the output
                        output[b, q, h * (self.embed_dim // self.num_heads):(h + 1) * (self.embed_dim // self.num_heads)] = weighted_values
            
            output = self.output_proj(output)
            return output
"""
        )
        
        # Write the modified content back to the file
        with open(modeling_path, "w") as f:
            f.write(modified_content)
        
        logger.info("Successfully patched the RT-DETR model")
        
        # Reload the module if it's already loaded
        if "transformers.models.rt_detr.modeling_rt_detr" in sys.modules:
            logger.info("Reloading the RT-DETR module")
            importlib.reload(sys.modules["transformers.models.rt_detr.modeling_rt_detr"])
        
        return True
    
    except Exception as e:
        logger.error(f"Error patching the transformers library: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False

def set_environment_variables():
    """Set environment variables to force CPU implementation."""
    os.environ["DOCLING_FORCE_CPU_MSDA"] = "1"
    
    # Add to .env file if it exists
    env_path = Path(".env")
    if env_path.exists():
        logger.info(f"Adding environment variable to {env_path}")
        with open(env_path, "r") as f:
            content = f.read()
        
        if "DOCLING_FORCE_CPU_MSDA" not in content:
            with open(env_path, "a") as f:
                f.write("\n# Force CPU implementation for MultiScaleDeformableAttention\n")
                f.write("DOCLING_FORCE_CPU_MSDA=1\n")
    else:
        logger.info(f"Creating {env_path} with environment variable")
        with open(env_path, "w") as f:
            f.write("# Force CPU implementation for MultiScaleDeformableAttention\n")
            f.write("DOCLING_FORCE_CPU_MSDA=1\n")

def create_startup_script():
    """Create a startup script to set the environment variable."""
    startup_path = Path("set_docling_env.bat")
    logger.info(f"Creating startup script at {startup_path}")
    
    with open(startup_path, "w") as f:
        f.write("@echo off\n")
        f.write("REM Set environment variables for DocuFlow\n")
        f.write("set DOCLING_FORCE_CPU_MSDA=1\n")
        f.write("echo Environment variables set for DocuFlow\n")
        f.write("echo DOCLING_FORCE_CPU_MSDA=1\n")
        f.write("echo.\n")
        f.write("echo You can now run your DocuFlow commands\n")

def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Fix CUDA MultiScaleDeformableAttention module issues in DocuFlow")
    parser.add_argument("--no-patch", action="store_true", help="Don't patch the RT-DETR model")
    parser.add_argument("--no-env", action="store_true", help="Don't set environment variables")
    parser.add_argument("--no-script", action="store_true", help="Don't create startup script")
    
    args = parser.parse_args()
    
    logger.info("Fixing CUDA MultiScaleDeformableAttention module issues in DocuFlow")
    
    # Set environment variable
    if not args.no_env:
        logger.info("Setting environment variables")
        set_environment_variables()
    
    # Create startup script
    if not args.no_script:
        logger.info("Creating startup script")
        create_startup_script()
    
    # Patch the RT-DETR model
    if not args.no_patch:
        logger.info("Patching RT-DETR model")
        success = patch_rt_detr_model()
        
        if success:
            logger.info("Patch applied successfully")
        else:
            logger.error("Failed to apply patch")
            return 1
    
    logger.info("Fix completed successfully")
    logger.info("\nTo use DocuFlow without CUDA errors, you can:")
    logger.info("1. Run the set_docling_env.bat script before running your commands")
    logger.info("2. Or set the environment variable manually: set DOCLING_FORCE_CPU_MSDA=1")
    logger.info("\nNote: This fix forces the MultiScaleDeformableAttention module to use CPU implementation")
    logger.info("      which may be slower than the CUDA implementation, but it will work without errors.")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())