I took a scientific approach and made only one change at a time. For changes which improved the overall accuracy I kept and changes which didn't I reverted back.

I decided to make the number of neurons in each layer propotional to the number of categories. The reason for doing so is to easily experiment with different sizes rather than just trying arbitrary values.

Some findings and things I tried:
4 x # categories worth of nodes works better than 6 x categories worth of nodes in the hidden layer
2 hidden layers works better than 3
Reducing dropout from .5 to .1 helped but below .1 doesn’t seem to help and seems to make things worse
Removing pooling completely makes it too slow for my laptop
3 convolution layers worked better than 2
Doing just one max pooling after all of the convolution layers, instead of after each layer, seemed to help improve things.
Overall accuracy is around 98% which was great however it was taking much longer than before, up to around 15 minutes
I added the two max pooling layers back which brought the accuracy down to around 96% but allowed me to complete the run in the 5 minute time allotment for the video recording

