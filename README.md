# art
To run the code, please place the **final_data** folder in the same directory as the pipeline.py file, and run 
```
python pipeline.py
```

## Part 1
Q: How did you verify that you are parsing the contours correctly?

A: By overlaying the boolean mask contour on the original DICOM image and visually inspect whether the contour looks correct. As an example:

![Overlay](https://github.com/rongen/art/blob/master/overlay48.png?raw=true "Overlay of boolean mask on dicom image")

However, this was done using matplotlib in a Jupyter notebook, and not included in the pipeline.py file as this was exploratory.

Q: What changes did you make to the code, if any, in order to integrate it into our production code base? 

A: I placed the folder directories as parameters that can be modified at the bottom of the pipeline.py file; updated the dicom code to pydicom as I am using Pydicom v1.0.2; and using the __name__ variable in case the pipeline.py file is imported into another file which might be the case for production use.


## Part 2
Q: Did you change anything from the pipelines built in Parts 1 to better streamline the pipeline built in Part 2? If so, what? If not, is there anything that you can imagine changing in the future?
    
A: Yes, a few things were changed. After knowing how the mask data is to be used in Part 2, the pipeline built in Part 1 was modified such that the masks were stored in an array instead of a dictonary. Additionally, a unique ID comprising the patient ID and the contour ID, was added as the first entry of each array of images and masks, so that the random batching of datasets across patients could be done.


Q: How do you/did you verify that the pipeline was working correctly?

A: I verified the pipeline by testing each part of the pipeline, then running the entire pipeline with print statements at each step to observe the results and compare against expectations. For random steps (eg the data shuffling step), the seed was fixed for reproducibility of results. After randomization, I also checked that each batch contained data across different patients.


Q: Given the pipeline you have built, can you see any deficiencies that you would change if you had more time? If not, can you think of any improvements/enhancements to the pipeline that you could build in?

A: Yes, given more time, I would add test cases and more error catching. Also, I would build in a way to display a random set of dicom images overlaid with their respective boolean masks in order to enable visual inspection that the output of this pipeline is correct.
As for improvements, it seems that only dicom images with contours/masks should be included in the training dataset; the rest of the dicom images can be used as a test dataset. The ratio of dicom images with contours to those without contours is quite imbalanced in favor of dicom images without contours. This suggests that there might be insufficient data to train the model on (ideally the training-validation-test split would be around 70%-20%-10%). To overcome this, augmentation of the training data (i.e. both dicom images and masks) could be done, in the form of horizontal and vertical flipping, scaling, rotation and random cropping (with the constraint that the mask is still fully within the image). Additionally, normalization of voxel intensities could be done for each dicom image. I'm also assuming that there will be an additional step in the pipeline to perform a training and validation split.
