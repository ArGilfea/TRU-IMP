# README File
# TRU-IMP
# Techniques for Reliable Use of Images in Medical Physics
# v.1.0.0
# 'The Imp is in the Details'
## Use:
This package and the GUI are used to visualize dynamic images, segment them and extract parameters. 
It was created for the sake of working with Dynamic Nuclear Medicine images.
It might thus work with other types of images, but will probably not be optimized.

## Note:
The GUI and the code are functional on a MacBookPro computer with iOS 13.2.1 Ventura. 
It has not yet been tested with another OS.

For any question, please contact philippe.laporte.3@umontreal.ca

## Location:

The source code is available at: [GitHub](https://github.com/ArGilfea/TRU-IMP)

A .dmg file for use without installation is available at: [DropBox](https://www.dropbox.com/scl/fo/567k83rjf3hucael7bgii/h?rlkey=9r7f8sb5cn9smerflco0lhzl3&dl=0)

Temporary host website with infos and links: [PhilippeTheMedicalPhysicist.com](https://argilfea.github.io/philippethemedicalphysicist.github.io/science/TRU-IMP/)

## Packages Required:
* Numpy          --For all computations
* Scipy          --To compute the parameters
* SkImage        --For filters and Canny edge detection algorithm
* Time           --To track the time elapsed for processes
* Numba          --To increase the speed of some functions
* Dynesty        --To compute the parameters
* os             --To clear the screen (easily circumvented)
* matplotlib     --To create the images and graphs
* pydicom        --To extract the images
* pickle         --To save and load data
* markdown       --To display some files in the GUI
* PyQt5          --For the GUI
* functools      --For part of the GUI interface to link buttons

## GUI:
The GUI is the easy way to work with the code. 
It consists of the main functions with the basic commands.
The more in-depth commands and analyses are not directly accessible and must be done by code.
### Opening a File:
A path can be input or browsed at the top left of the screen to locate the dicom files.
By clicking "Extract", the dicom files will be opened and put together to form a 4-D volume.
Otherwise, if a pickle file (.pkl) of a DicomImage (in-package code) class is selected,
the GUI will open it with the "Load" button,
instantiating all the segmentations and other analyses already done.

Once the acquisition is loaded or extracted, it cannot be removed or changed directly:
the GUI must be reinitialized to change it. 
If the extract or load option is selected again, a second acquisition will be loaded in the GUI.
This second acquisition can be used to coregister the first one and see both at the same time.
Note that this second acquisition is not used for any segmentation or other schemes, for now.
### Visualising an Image:
When an image is loaded, the sliders on the left-hand side can be moved to change the view.
To see exactly where one is looking, the right hand side focus option can be toggled:
this will create a focus on the views to show where the pointer is located.
For images that are hard to visualize, a "log" button can be toggled:
this will take the log_10 of the image, making details more visible;
it also increases the visible artefacts and noise.
There is also an option to view the limits of the subimage, as determined by the parameters:
this will create yellow lines delimitating the location of the subimage.
A drop-down menu, initially set at "Slice" can allow different views of the image:
* The "Slice" shows slices of the image;
* The "Flat" shows the flattened image;
* The "Sub. Slice" shows the slices of the subimage;
* The "Sub. Flat" shows the flattened subimage;
* The "Segm. Slice" shows the slices of a segmentation;
* The "Segm. Flat" shows the flattened segmentation;
* The "Segm. Sub. Slice" shows the slices of the subsegmentation;
* The "Segm. Sub. Flat" shows the flattened subsegmentation;
### Image Visualisation Options:
A drop-down menu, initially set at "Array: Base Image" can allow different views of the image:
* "Array: Base Image": Shows the acquisition with voxel indices as axes.
* "Physical: Base Image": Shows the acquisitions with physical dimensions as axes, as given by the DICOM file headers.
* "Array: CT": Shows the second acquisition loaded with voxel indices as axes. Note that this is not properly implemented yet.
* "Physical: CT": Shows the second acquisition with physical dimensions for the axes, as given by the DICOM file headers.
* "Physical: Combined": Shows the superposed images, with different colour schemes. The superposition
is done with the physical dimensions, as given by the DICOM files. Note that for the visualisation, 
a closest neighbour interpolation is done to visualize the slices. In this mode, only the slice and subslice
options will lead to a visualization of both acquisitions.

### Visualising a TAC:
- The middle image, in its default setting, shows the Time-Activity Curve for the 
voxel selected by the sliders on the left.
- If focus is toggled, the focus on the views will be the point for the central TAC.
- If the subimage button is toggled, lines will be added to limit the TACs.
- If the superpose button is toggled, the selected segmentation will be superposed to the image.
### Visualising Sliced Signal:
The botton row of images show slices at the position of the sliders.
The y-axis represents the signal in that specific slice.
- If the focus button is toggled, a red line will indicate the position on those slices.
- If the subimage button is toggled, yellow lines will delimitate the subimage.
- If the superpose button is toggled and a segmentation selected, the sliced signal will show where the segmentation overlap, as the curve will be filled where the segmentation is present.

Once a segmentation is computed and selected, the bottom row of images can be modified to show the slice TACs. These slice TACs are computed like normal TACs. The only noteworthy detail is that, for each slice, the slice is considered as the whole spatial image (it impacts the denominator in the averaging)
### Infos Button:
This button will create a pop-up with the basic information of the acquisition.
### Parameters Button:
This will open a parameters window.
In this window, the parameters for segmentations, errors, and analyses can be selected.
Each tab represents one family of parameters.
For each tab, a specific model can be selected: this will make the relevant parameters appear.
Even if a new model is selected, the parameters are kept.
The verbose parameter (default True) is recommended, as it allows to see the progresses.
### Noise Button:
This will add noise to the whole image, i.e. to all timeframes and all voxels, according to the parameters.
Only one method will be used, as specified in the parameters window.
### Deformation Button:
This will deform a given segmentation, according to the specified parameters. The result will be stored as a new segmentation.
Only one method will be used, as specified in the parameters window.
### Segmentation Button:
This will segment the images according to the selected parameters.
Only one method will be used, as specified in the parameters window.
This step can take a lot of time, depending upon the segmentation scheme.
The results will be stored in the instance of the GUI.
### ErrorBars Button:
This will compute the error of the segmentations according to the selected parameters.
Only one method will be used, as specified in the parameters window.
This step can take a lot of time, depending upon the method selected.
The results will be stored in the instance of the GUI.
### Bayesian Button:
This will use Bayesian analysis to extract coefficients of the TACs,
according to the parameters selected.
Only one method will be used, as specified in the parameters window.
This step can take a lot of time, depending upon the method selected.
The results will be stored in the instance of the GUI.
### Erase Button:
This will use erase a previously computed aspect, either a segmentation,
an error bar, or a Bayesian analysis, as determined by the parameters.
This option is not retrievable, meaning that whatever will have been discarded
will be permanently gone.
### Visualising Results:
The initial results that can be seen is "TAC".
The results can be seen in the central image.
This can be changed to visualise other results:
* TAC:
Shows the TAC of the voxel, of a segmentation or of a segmentation error scheme,
depending on the position of the sliders "Segm" and "Segm.Errors". 
If both are -1, it will show the voxel of the leftern sliders;
otherwise, it will show the curves for the sliders not equal to -1.
* TAC Slice: Shows the TAC slices in the bottom row of images.
* Dice:
This will show the Dice coefficients for all segmentations,
if they have been computed.
* Jaccard:
This will show the Jaccard coefficients for all segmentations,
if they have been computed.
* Energy:
This will show the energy of the system for all iterations. 
If segmentation slider is -1, will show all segmentations, otherwise will show a specific one.
The energies are for the ICM and FCM segmentations.
* Mus:
This will show the centers of mass of the statistical distributions for all iterations. 
If segmentation slider is -1, will show all segmentations, otherwise will show a specific one.
The centers are for the ICM and FCM segmentations.
* Factor f:
This will show the factor f and the associated segmented volume. Used to confirm the convergence of the algorithm.
This is only for the filling f segmentation
* Bayesian:
This will show the parameters extracted with Bayesian analyses.
The parameter shown will be the one given by the "Bay. Values" slider.
If it is set to -1, it will show them all:
this can be hard to visualise if they don't have the same magnitude.
The bottom row will be updated to show the Bayesian processes done by Dynesty, for the selected segmentation. 
* Center of Mass: shows a 3D representation of the center of mass of the segmentations.
* Moments Shows: a 3D representation of the 2nd moments of the segmentations.
### Exporting Results:
Clicking the Export Button will open a window from where the exportation can be done.
Whatever will be checked will be exported.
The file destination can be entered manually or the folder selected via the "Browse" button.
The extension used will be the base name of the exported data.
For each type of data exported, a suffix will be appended to describe it, making the 
selection of the relevant data easier afterward.
The whole instance of the GUI and its computations, i.e. a DicomImage class, can be extracted.
This file can latter be reloaded by the GUI. 
This allows to keep the computations saved elsewhere
and save computing time.
The parameters of the parameter window can also be extracted, allowing to keep 
track of the parameters used for a specific analysis. 
This is useful for reproducibility concerns.
The other results, (TACs, segmentation images, curves, etc.) can
be extracted either as images or as data.
The data will be in a .csv file, where the first column will either be 
the time and the others related to each segmentation,
or the segmentation number and the other columns will be the extracted parameters.
This can allow to process the results and the data outside of the GUI.
This was done to avoid putting a huge burden upon the inner processing of the results in
the GUI, as this task can be easily done outside of the interface.
### Exit Button:
Shuts down the GUI

--- 

## User Options
This section will describe the main choices that the user can make.
The goal is to make the process easier to understand. 
Where relevant, references will be given.
These will also be present at the end in the reference sections.

For a segmentation, the Acq. Segm. slider allows to select which timeframe to segment.
If the slider is set to -1, this will segment all timeframes individually.

Otherwise, if the Acq. part of the Subimage is not for all the timeframes, the segmentation will be done on that specific range of timeframes.
For example, if the acquisition has 40 timeframes and the SubImage acq part is 10 - 35, 
this will do segmentations on the timeframes 10 to 35 exclusively, notwithstanding the value of the Acq. Segm. slider. 
## Segmentation Schemes:
### Canny and Canny Filled: 
The Canny part will use the Canny
edge detection algorithm to determine the edges
of the image.
Since Canny only yields results in 2-D,
a combination will be used to determine if a given
voxel belongs to the segmentation,
i.e. it will belong to it only if it belongs
to at least a certain number of 2-D slices.
The other parameter is sigma, is used
for the Gaussian filter used.
For the Canny filled, a Canny part is used
first. This yields a contour.
Afterward, this image is filled to yield
the resulting segmentation.
Reference: Canny, J. A Computational Approach to Edge Detection. 
IEEE Transactions on Pattern Analysis and Machine Intelligence 8(6). 1986.
### ICM and K-Mean: 
This method presupposes a statistical distribution in the
distribution of the signal in the image:
one distribution for the volume to be segmented and one for the rest.
The k-mean part looks for the parameters of this distribution, 
supposed to be Gaussians. 
Once the mean and std determined, the segmentation is done.
The ICM part starts with a k-mean, then further pinpoints the
segmentation by taking into account the current neighbours of
a voxel; in other words, a voxel will more probably belong to 
a class if its neighbours belong to the same class.
Reference: Besag, J. On the Statistical Analysis of Dirty Pictures. 1986 48(3):259-79
### FCM (Fuzzy C-means):
This method is similar to the ICM and K-mean, but supposes that a voxel
can belong to more than one class at the same time. Each voxel will thus
belong to different classes at the same time.
This presupposes a Gaussian distribution underlying the distribution of intensity.
The m parameters determines the fuzziness of the segmentation and the alpha is used for
the Lp-norm. 
Reference: Lapuyade-Lahorgue et al. SPEQTACLE: An automated generalized fuzzy C-means algorithm for tumor delineation in PET. Medical Physics. 42(10). 2015.
### Filling and Filling f: 
This method takes a seed as a starting point.
For each iteration, until convergence, any voxel 
adjacent to the current segmentation will be added
if it is contained between the mean +/- f std,
where f is the factor selected by the user.
After convergence of the segmentations, the last
one will be kept as the result.
Alternatively, to not have to select a specific factor f,
Filling f will take a range of values as input.
The final segmentation will be the one for which the growth
of the segmented volume will be the starkest.
Reference: Adams, R., Bischof, L. 1994. Seeded Region Growing. 
IEEE Transactions on Pattern Analysis and Machine Intelligence. 16(6): 641-7.
### Ellipsoid: 
This creates an ellipsoid with a given center with the specified lengths for each axis.
### Prism: 
This creates a prism with dimensions given by the subimage parameters.
### Threshold: 
This takes an already determined segmentation and will only keep all the voxels that
are above a certain percentage of the maximal value. 
To determine the maximal value and avoid extreme values,
a Gaussian filter with sigma can be used.

## Distance Schemes:
### TaxiCab Distance: 
This computes the taxicab distance between two points, where relevant.
In topological terms, this represents L1, 
i.e. the distance between two points (x0,y0,z0) and (x1,y1,z1)
is |x1-x0| + |y1-y0| + |z1-z0|

## Deformation Schemes:

This allows the modification of a segmentation by specific spatial transformations (all segmentations if set to -1). In each cases, it takes a segmentation, modifies it, saves the new result, along with the new TAC.
If the erase_after option is selected, the original segmentations used for the deformation are erased.

### Linear Shift:
This will shift the whole segmentation by a number of voxel in each spatial dimension, as specified. 

The units are in voxels.
### Rotate:
This will rotate the whole segmentation by a number of degree in each spatial dimensions, according to its center of mass. 
Note, the order of rotation is fixed. The first value is the first axis of rotation, and so forth. Plan accordingly the desired values.

The units are in degrees (they are converted in radiants inside the program).
### Expansion:
This will expand the whole segmentation around its center of mass. Each factor representes an axis.

The units are proportions (unitless), with 1 being an identity expansion.
### Reflection
This will reflect the whole segmentation along an axis centered on the center of mass.
The choice of axis will determine along which axis the segmentation is reflected, 0 being axis, 1 being coronal, and 2 being sagittal. 
### Flip All
This will flip the image and all the segmentations along a specific spatial axis.
This is useful when the loading doesn't bring the image in the good direction.
## Error Bar Schemes:
### Linear Shift: 
This will take a given segmentation and shift it by
a number of voxels, as specified in the parameters (all if -1).
The result will be a new TAC with an error bar,
corresponding to the average of the new segmentations 
and its standard deviation.
Only the resulting curve will be saved.
### Rotation
This will take a given segmentation and rotate it by
a certain degree, as specified in the parameters (all if -1).
The result will be a new TAC with an error bar,
corresponding to the average of the new segmentations 
and its standard deviation.
Only the resulting curve will be saved.
### Expansion
This will take a given segmentation and expand it by
a certain proportion, as specified in the parameters (all if -1).
The factor used will both be used for an expansion and a contraction, i.e.
both an expansion by the factor and 1/factor.
The result will be a new TAC with an error bar,
corresponding to the average of the new segmentations 
and its standard deviation.
Only the resulting curve will be saved.
### Reflection
This will take a given segmentation and reflect it along the three axis from the center of masse, 
as specified in the parameters (all if -1).
The result will be a new TAC with an error bar,
corresponding to the average of the new segmentations 
and its standard deviation.
Only the resulting curve will be saved.
### FCM
For a segmentation that was produced through the Fuzzy C-Mean algorithm, a fuzzy map is saved,
i.e. the probability of each voxel to belong to each class, normalized.
This error method will sample a normal distribution for each voxel and determine whether a voxel belongs to the segmentation or not.
This will be done for a number of iteration as specified by the relevant parameter.
From this new segmentation, a TAC will be computed, for each iteration.
After all the iterations, an average TAC with the relevant standard deviation will be produced, leading to a new TAC with error.
Only the resulting curve will be saved.
## Bayesian Analysis Schemes:
### Dynesty: 
This will use Dynesty to fit a "Bayesian Curves Used" to the "Bayesian Analysis Model".
Dynesty is a nested sampling method to estimate the parameters of a curve.
This method can be relatively lengthy, but the results are more transparent than other methods.
The description of the results, beside the values, can not yet be obtainable directly from the GUI (work in progress).
Full reference can be found here: https://dynesty.readthedocs.io/en/latest/
### SciPy: 
This will use scipy.optimize.curve_fit to fit a "Bayesian Curves Used" to the "Bayesian Analysis Model"
Reference: https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.curve_fit.html

## Bayesian Analysis Models:
See the reference section for links.
### 2_Comp_A1: 
This will use the first compartment equation for a 3-compartment
pharmacokinetic model. 
Three parameters will be extracted:

* The initial activity;
* An exponential factor.

The model has the following equation:
A_1(t) = A_0 e^(-k t)
### 2_Comp_A2: 
This will use the second compartment equation for a 3-compartment
pharmacokinetic model. 
Three parameters will be extracted:

* The initial activity;
* A first exponential factor;
* A second exponential factor.

The model has the following equation:
A_2(t) = A_0 [e^(-k_1 t) - e^(-k_2 t)]
### 2_Comp_A2_Pause: 
This will use the second compartment equation for a 3-compartment
pharmacokinetic model. This will also model that a pause
happened in the process, for an unknown period of time.
Five parameters will be extracted:

* The initial activity;
* A first exponential factor;
* A second exponential factor.
* The start of the pause;
* The length of the pause.

## Bayesian Curves Used:
* Average: This will use the TACs from the segmentations directly.
* Errors: This will use the errorbars extracted from the segmentations.

When using the curve with errors, the user can select a minimal value for errorbars. 
The Thresh Perc option will take all errorbars that are smaller than that percentage of the maximum value of the curve
and will bring them to the selected percentage of the maximal value, as given by Thresh Value.

## Noise Type
It is possible to add noise to the whole image. 
Through the parameters window, noise can be added to the whole image.
This noise will be added to each voxel of each timeframe in the same fashion.
The noise is randomly generated from a given probability distribution. 
When possible, the analytic inverse cumulative distribution is used directly; 
when this cannot be done, a computational method is done.

The selected noise distribution is shown through the probability density distribution (pdf), 
with its cumulative density distribution (cdf), to help
visualise the type and parameters of the needed noise. 
The Fourier transforms of both the pdf and the cdf are also shown.

For ease of analysis, the pdf, mean, and standard deviation equations and values are shown. 

The currently available types of noise are:

* Gaussian: Traditional gaussian (normal) distribution;
* Poisson: To be added;
* Rayleigh;
* Erlang (Gamma);
* Exponential: This is the Erlang distribution with the second parameter (b) set to 1;
* Uniform: Constant distribution, spread equally over a given range.

## Options
Options are available in a specific tab of the parameters for the GUI, among which the colour maps and the transparency when many 
aspects are shown.
An option allows the user to select between various ways of combining the two images, when two acquisitions are loaded (such as a PET and a CT).

* Closest Neighbour: Looks for the closest neighbour. Fastest method, but with some errors;
* Linear approximation: If a slice would fall between two slices of a given axis, 
this option will approximate the position by assuming a linear variation between slices.

## References:
* Canny: Canny, J. A Computational Approach to Edge Detection. IEEE Transactions on Pattern Analysis and Machine Intelligence 8(6). 1986.
* Dynesty: https://dynesty.readthedocs.io/en/latest/
* FCM: Lapuyade-Lahorgue et al. SPEQTACLE: An automated generalized fuzzy C-means algorithm for tumor delineation in PET. Medical Physics. 42(10). 2015.
* Filling: Adams, R., Bischof, L. 1994. Seeded Region Growing. IEEE Transactions on Pattern Analysis and Machine Intelligence. 16(6): 641-7.
* ICM: Besag, J. On the Statistical Analysis of Dirty Pictures. 1986 48(3):259-79
* Pharmacokinetic modeling: Maguire, R.P. et al. PET Pharmacokinetic Course. 
Montreal Neurological Institute: Montréal. 2003.
* SciPy: https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.curve_fit.html