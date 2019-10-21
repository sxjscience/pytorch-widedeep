import numpy as np
import pandas as pd
import pytest

from pytorch_widedeep.preprocessing import ImagePreprocessor

df = pd.DataFrame({'galaxies': ['galaxy1.png', 'galaxy2.png']})
img_col = 'galaxies'
imd_dir = 'images'
processor = ImagePreprocessor()
X_imgs = processor.fit_transform(df, img_col, img_path=imd_dir)

###############################################################################
# There is not much to test here, since I only resize.
###############################################################################
def test_sizes():
	img_width = X_imgs.shape[1]
	img_height = X_imgs.shape[2]
	assert np.all((img_width==processor.width, img_height==processor.height))