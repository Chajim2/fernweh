import numpy as np

def normalize_embeding(old_embeding_values: list[float]) -> np.ndarray:
    # might wanna check for 0 division later
    np_values = np.array(old_embeding_values, dtype=np.float64)
    return np_values / np.linalg.norm(np_values)
    