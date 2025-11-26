"""
Async Model Loader with Warmup

Provides async model loading to avoid blocking the main thread,
with warmup support for better performance.
"""

import asyncio
import logging
import time
from typing import Optional, Callable, Any
from concurrent.futures import ThreadPoolExecutor
import threading

logger = logging.getLogger(__name__)


class AsyncModelLoader:
    """
    Async model loader with warmup and preloading support
    """
    
    def __init__(
        self,
        loader_func: Callable,
        warmup_samples: Optional[list] = None,
        num_workers: int = 1
    ):
        """
        Initialize async model loader
        
        Args:
            loader_func: Function to load model
            warmup_samples: Sample data for warmup
            num_workers: Number of worker threads
        """
        self.loader_func = loader_func
        self.warmup_samples = warmup_samples or []
        self.num_workers = num_workers
        
        self.model = None
        self.is_loading = False
        self.is_loaded = False
        self.load_error = None
        
        self._load_lock = threading.Lock()
        self._executor = ThreadPoolExecutor(max_workers=num_workers)
    
    async def load_async(self) -> bool:
        """
        Load model asynchronously
        
        Returns:
            True if loaded successfully, False otherwise
        """
        if self.is_loaded:
            logger.info("Model already loaded")
            return True
        
        if self.is_loading:
            logger.info("Model loading in progress, waiting...")
            while self.is_loading:
                await asyncio.sleep(0.1)
            return self.is_loaded
        
        with self._load_lock:
            if self.is_loaded:
                return True
            
            self.is_loading = True
            self.load_error = None
        
        try:
            logger.info("🔄 Starting async model loading...")
            start_time = time.time()
            
            # Run loader in thread pool
            loop = asyncio.get_event_loop()
            self.model = await loop.run_in_executor(
                self._executor,
                self.loader_func
            )
            
            load_time = time.time() - start_time
            logger.info(f"✅ Model loaded in {load_time:.2f}s")
            
            # Warmup if samples provided
            if self.warmup_samples:
                await self.warmup()
            
            self.is_loaded = True
            return True
            
        except Exception as e:
            logger.error(f"❌ Model loading failed: {e}")
            self.load_error = e
            return False
            
        finally:
            self.is_loading = False
    
    async def warmup(self) -> bool:
        """
        Warmup model with sample data
        
        Returns:
            True if warmup successful, False otherwise
        """
        if not self.model:
            logger.warning("Cannot warmup: model not loaded")
            return False
        
        if not self.warmup_samples:
            logger.info("No warmup samples provided")
            return True
        
        try:
            logger.info(f"🔥 Warming up model with {len(self.warmup_samples)} samples...")
            start_time = time.time()
            
            # Run warmup predictions
            for i, sample in enumerate(self.warmup_samples):
                try:
                    # Run prediction in thread pool
                    loop = asyncio.get_event_loop()
                    await loop.run_in_executor(
                        self._executor,
                        self._warmup_predict,
                        sample
                    )
                    
                    logger.debug(f"Warmup {i+1}/{len(self.warmup_samples)} completed")
                    
                except Exception as e:
                    logger.warning(f"Warmup sample {i+1} failed: {e}")
                    continue
            
            warmup_time = time.time() - start_time
            logger.info(f"✅ Warmup completed in {warmup_time:.2f}s")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Warmup failed: {e}")
            return False
    
    def _warmup_predict(self, sample: Any):
        """Run a single warmup prediction"""
        if hasattr(self.model, 'predict'):
            self.model.predict(sample)
        elif callable(self.model):
            self.model(sample)
    
    async def predict_async(self, *args, **kwargs) -> Any:
        """
        Run prediction asynchronously
        
        Args:
            *args: Positional arguments for prediction
            **kwargs: Keyword arguments for prediction
            
        Returns:
            Prediction result
        """
        # Ensure model is loaded
        if not self.is_loaded:
            loaded = await self.load_async()
            if not loaded:
                raise RuntimeError(f"Model loading failed: {self.load_error}")
        
        # Run prediction in thread pool
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            self._executor,
            self._predict_sync,
            args,
            kwargs
        )
        
        return result
    
    def _predict_sync(self, args, kwargs):
        """Run synchronous prediction"""
        if hasattr(self.model, 'predict'):
            return self.model.predict(*args, **kwargs)
        elif callable(self.model):
            return self.model(*args, **kwargs)
        else:
            raise RuntimeError("Model is not callable")
    
    def get_model(self) -> Any:
        """Get loaded model (synchronous)"""
        return self.model
    
    def is_ready(self) -> bool:
        """Check if model is ready for predictions"""
        return self.is_loaded and self.model is not None
    
    async def reload(self) -> bool:
        """
        Reload model
        
        Returns:
            True if reloaded successfully, False otherwise
        """
        logger.info("Reloading model...")
        
        # Reset state
        self.is_loaded = False
        self.model = None
        self.load_error = None
        
        # Load again
        return await self.load_async()
    
    def shutdown(self):
        """Shutdown executor"""
        logger.info("Shutting down model loader executor...")
        self._executor.shutdown(wait=True)


class ModelPool:
    """
    Pool of models for concurrent predictions
    """
    
    def __init__(
        self,
        loader_func: Callable,
        pool_size: int = 2,
        warmup_samples: Optional[list] = None
    ):
        """
        Initialize model pool
        
        Args:
            loader_func: Function to load model
            pool_size: Number of models in pool
            warmup_samples: Samples for warmup
        """
        self.loader_func = loader_func
        self.pool_size = pool_size
        self.warmup_samples = warmup_samples
        
        self.models = []
        self.available_models = asyncio.Queue()
        self.is_initialized = False
    
    async def initialize(self) -> bool:
        """
        Initialize model pool
        
        Returns:
            True if initialized successfully, False otherwise
        """
        if self.is_initialized:
            return True
        
        logger.info(f"🔄 Initializing model pool (size={self.pool_size})...")
        start_time = time.time()
        
        try:
            # Load models concurrently
            tasks = [
                self._load_model(i)
                for i in range(self.pool_size)
            ]
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Check results
            loaded_count = sum(1 for r in results if r is True)
            
            if loaded_count == 0:
                logger.error("❌ Failed to load any models")
                return False
            
            init_time = time.time() - start_time
            logger.info(f"✅ Model pool initialized ({loaded_count}/{self.pool_size} models) in {init_time:.2f}s")
            
            self.is_initialized = True
            return True
            
        except Exception as e:
            logger.error(f"❌ Model pool initialization failed: {e}")
            return False
    
    async def _load_model(self, index: int) -> bool:
        """Load a single model into the pool"""
        try:
            logger.info(f"Loading model {index+1}/{self.pool_size}...")
            
            loader = AsyncModelLoader(
                self.loader_func,
                warmup_samples=self.warmup_samples if index == 0 else None
            )
            
            loaded = await loader.load_async()
            
            if loaded:
                self.models.append(loader)
                await self.available_models.put(loader)
                logger.info(f"✅ Model {index+1} loaded")
                return True
            else:
                logger.error(f"❌ Model {index+1} loading failed")
                return False
                
        except Exception as e:
            logger.error(f"❌ Model {index+1} error: {e}")
            return False
    
    async def acquire(self, timeout: float = 30.0) -> Optional[AsyncModelLoader]:
        """
        Acquire a model from the pool
        
        Args:
            timeout: Timeout in seconds
            
        Returns:
            Model loader or None if timeout
        """
        try:
            model = await asyncio.wait_for(
                self.available_models.get(),
                timeout=timeout
            )
            return model
        except asyncio.TimeoutError:
            logger.error("Model acquisition timeout")
            return None
    
    async def release(self, model: AsyncModelLoader):
        """Release model back to pool"""
        await self.available_models.put(model)
    
    async def predict(self, *args, **kwargs) -> Any:
        """
        Run prediction using pool
        
        Args:
            *args: Positional arguments for prediction
            **kwargs: Keyword arguments for prediction
            
        Returns:
            Prediction result
        """
        if not self.is_initialized:
            await self.initialize()
        
        model = await self.acquire()
        if not model:
            raise RuntimeError("Failed to acquire model from pool")
        
        try:
            result = await model.predict_async(*args, **kwargs)
            return result
        finally:
            await self.release(model)

