from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
import yaml
import torch
import os

# Model path to change with code/hf_cache
def load_llm():
    """
    Load a local or remote HF model and return a callable that generates text.

    Args:
        model_source: optional model identifier (HF id or local path). If None, read from `LLM/config.yaml`.
        cache_dir: optional directory to use for model/tokenizer cache (useful to store model files on another drive).
    """
    with open("LLM/config.yaml", "r") as f:
        cfg = yaml.safe_load(f)

    model_name = cfg.get("model_name")
    print(f"🔄 Loading model '{model_name}'...")

    # allow overriding cache directory via config or parameter
    try:
        cache_dir = cfg.get("cache_dir")
    except:
        print("No cache_dir found in config")
        return None

    # If a cache_dir is provided, ensure it exists and is writable
    if cache_dir:
        try:
            os.makedirs(cache_dir, exist_ok=True)
        except Exception as e:
            raise RuntimeError(f"Unable to create cache directory '{cache_dir}': {e}")

        if not os.access(cache_dir, os.W_OK):
            raise RuntimeError(f"Cache directory '{cache_dir}' is not writable.")

    tokenizer = AutoTokenizer.from_pretrained(model_name, cache_dir=cache_dir)

    # Detect GPU availability and optionally use 8-bit loading (requires bitsandbytes)
    use_gpu = torch.cuda.is_available()

    # decide whether to load in 8-bit: config > env var > default False
    env_use_8bit = os.environ.get("USE_8BIT", "").lower() in ("1", "true", "yes")
    cfg_use_8bit = cfg.get("use_8bit", None)
    use_8bit = cfg_use_8bit if cfg_use_8bit is not None else env_use_8bit
    use_fp16 = cfg.get("torch_dtype", "float16") == "float16"

    # check bitsandbytes availability when 8-bit requested
    if use_fp16:
        torch_dtype = torch.float16
    elif use_8bit:
        try:
            import bitsandbytes as bnb  # noqa: F401
            bnb_available = True
            print("✅ bitsandbytes is available for 8-bit model loading.")
        except Exception:
            bnb_available = False
            use_8bit = False
            print("⚠️  bitsandbytes not available, cannot load model in 8-bit. Falling back to full precision.")
            
    

    try:
        if use_gpu:
            print("✅ GPU detected, loading model on GPU.")
            if use_fp16:
                print("🔄 Loading model in 16-bit precision.")
                # load with float16 precision
                model = AutoModelForCausalLM.from_pretrained(
                    model_name,
                    torch_dtype=cfg.get("torch_dtype", torch.float16),
                    device_map="auto",
                    cache_dir=cache_dir,
                    temperature=cfg.get("temperature", 0.3),
                    do_sample=cfg.get("do_sample", False),
                    top_p=cfg.get("top_p", 0.9),
                )
            elif use_8bit:
                print("🔄 Loading model in 8-bit precision.")
                # load with bitsandbytes in 8-bit to reduce VRAM usage
                model = AutoModelForCausalLM.from_pretrained(
                    model_name,
                    device_map="auto",
                    cache_dir=cache_dir,
                    load_in_8bit=cfg.get("use_8bit", True),
                    temperature=cfg.get("temperature", 0.3),
                    do_sample=cfg.get("do_sample", False),
                    top_p=cfg.get("top_p", 0.9),
                )
            else:
                print("🔄 Loading model in 16-bit precision.")
                model = AutoModelForCausalLM.from_pretrained(
                    model_name,
                    torch_dtype=torch.float16,
                    device_map="auto",
                    cache_dir=cache_dir,
                    temperature=cfg.get("temperature", 0.3),
                    do_sample=cfg.get("do_sample", False),
                    top_p=cfg.get("top_p", 0.9),
                )
        else:
            print("⚠️  GPU not available, loading model on CPU. This may be very slow.")
            # CPU fallback (may be very slow); use low_cpu_mem_usage to reduce memory
            model = AutoModelForCausalLM.from_pretrained(
                model_name,
                device_map="cpu",
                low_cpu_mem_usage=True,
                cache_dir=cache_dir,
                temperature=cfg.get("temperature", 0.3),
                do_sample=cfg.get("do_sample", False),
                top_p=cfg.get("top_p", 0.9),
            )
    except Exception as e:
        raise RuntimeError(f"Failed to load model '{model_name}': {e}")

    pipe = pipeline(
        "text-generation",
        model=model,
        tokenizer=tokenizer,
        max_new_tokens=cfg.get("max_tokens", 2048),
        temperature=cfg.get("temperature", 0.3),
        do_sample=cfg.get("do_sample", False)
    )

    def call(prompt):
        result = pipe(prompt)[0]["generated_text"]
        return result

    return call
