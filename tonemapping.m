function img = LocalToneMapping(hdr, output)
%input
hdr = hdrread(hdr);
%get double precision
img = double(hdr);
%convert 2 grayscale
grayScale = 0.299 * img(:, :, 1) + 0.587 * img(:, :, 2) + 0.114 * img(:, :, 3);
%get log
grayScale_log = log10(grayScale);
grayScale_log = grayScale_log./log10(10);
%apply bfilter2 to get low high
LowFrequency = imbilatfilt(grayScale_log);
HighFrequency = grayScale_log - LowFrequency;
%Compute the new intensity channel
max_ = max(LowFrequency(:));
min_ = min(LowFrequency(:));
gamma = (log10(50)/log10(10)) / (max_ - min_);
newIntensity = LowFrequency * gamma + HighFrequency;
newIntensity = power(10, newIntensity);
%recompose color image
img = img.* newIntensity;
img = img./ grayScale;
img = (img - min(img(:))) / (max(img(:)) - min(img(:)));
img = img*3;
%imshow(img);
imwrite(img, output);
end
