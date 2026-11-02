"""
Model Management Service.
Handles lazy loading, in-memory caching, device selection (CUDA / CPU),
and memory-safe model transitions.
"""
import os
import gc
import logging
from typing import Tuple, Dict, Any, Optional
import torch
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import config

logger = logging.getLogger(__name__)

class ModelManager:
    """
    Singleton-style Model Manager for loading and managing Transformer models.
    Caches the currently active model to prevent redundant downloads or out-of-memory spikes.
    """
    _instance = None
    _loaded_model_key: Optional[str] = None
    _model = None
    _tokenizer = None
    _device: Optional[torch.device] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ModelManager, cls).__new__(cls)
            cls._instance._init_device()
        return cls._instance

    _last_load_time: float = 0.0

    def _init_device(self):
        """Detects whether CUDA is available and selects the optimal device."""
        if torch.cuda.is_available():
            self._device = torch.device("cuda")
            logger.info("CUDA GPU available. Using GPU for Transformer inference.")
        else:
            self._device = torch.device("cpu")
            # Set thread budget on CPU to prevent contention while maximizing throughput
            cpu_threads = min(4, os.cpu_count() or 4)
            try:
                torch.set_num_threads(cpu_threads)
            except Exception:
                pass
            logger.info(f"CUDA GPU not detected. Using CPU with {cpu_threads} threads for Transformer inference.")

    @property
    def device(self) -> torch.device:
        if self._device is None:
            self._init_device()
        return self._device

    @property
    def device_name(self) -> str:
        if self.device.type == "cuda":
            return f"CUDA ({torch.cuda.get_device_name(0)}) - FP16 Accelerated"
        return "CPU (Optimized with torch.inference_mode)"

    def get_loaded_model_info(self) -> Optional[Dict[str, Any]]:
        if self._loaded_model_key and self._loaded_model_key in config.SUPPORTED_MODELS:
            info = dict(config.SUPPORTED_MODELS[self._loaded_model_key])
            info["key"] = self._loaded_model_key
            info["device"] = self.device_name
            info["last_load_time"] = self._last_load_time
            return info
        return None

    def resolve_model_key(self, model_key: str) -> str:
        """Resolves model key with backward compatibility aliases."""
        if hasattr(config, "MODEL_ALIASES") and model_key in config.MODEL_ALIASES:
            return config.MODEL_ALIASES[model_key]
        return model_key

    def load_model_with_timing(self, model_key: str = "t5_small") -> Tuple[Any, Any, float]:
        """
        Loads the specified model and tokenizer, measuring initialization time.
        If already cached in memory, returns cached instances with load_time = 0.0.
        Returns: (tokenizer, model, load_time_seconds)
        """
        import time
        model_key = self.resolve_model_key(model_key)
        if model_key not in config.SUPPORTED_MODELS:
            raise ValueError(f"Unsupported model key '{model_key}'. Allowed: {list(config.SUPPORTED_MODELS.keys())}")

        # If already loaded in memory, return cached instances with 0.0s load time
        if self._loaded_model_key == model_key and self._model is not None and self._tokenizer is not None:
            return self._tokenizer, self._model, 0.0

        t0 = time.time()

        # Evict previous model if different to save RAM/VRAM
        if self._model is not None:
            logger.info(f"Unloading previous model '{self._loaded_model_key}' to conserve memory.")
            del self._model
            del self._tokenizer
            self._model = None
            self._tokenizer = None
            self._loaded_model_key = None
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
            gc.collect()

        model_cfg = config.SUPPORTED_MODELS[model_key]
        model_id = model_cfg["model_id"]
        logger.info(f"Loading tokenizer and model for '{model_id}' onto {self.device_name}...")

        try:
            tokenizer = AutoTokenizer.from_pretrained(model_id)
            model = AutoModelForSeq2SeqLM.from_pretrained(model_id)

            if self.device.type == "cuda":
                model.half()  # FP16 on compatible CUDA GPUs

            model.to(self.device)
            model.eval()

            load_time = round(time.time() - t0, 3)
            self._tokenizer = tokenizer
            self._model = model
            self._loaded_model_key = model_key
            self._last_load_time = load_time

            logger.info(f"Successfully loaded '{model_id}' in {load_time}s.")
            return self._tokenizer, self._model, load_time
        except Exception as e:
            logger.error(f"Failed to load model '{model_id}': {e}")
            raise RuntimeError(f"Error loading model '{model_id}': {str(e)}")

    def load_model(self, model_key: str = "t5_small") -> Tuple[Any, Any]:
        """Backward-compatible loader returning (tokenizer, model)."""
        tokenizer, model, _ = self.load_model_with_timing(model_key)
        return tokenizer, model

    def unload(self):
        """Frees any resident model to release system resources."""
        if self._model is not None:
            del self._model
            del self._tokenizer
            self._model = None
            self._tokenizer = None
            self._loaded_model_key = None
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
            gc.collect()
            logger.info("Model unloaded from memory.")
