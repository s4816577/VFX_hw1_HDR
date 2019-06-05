import argparse
import numpy as np
import skimage.transform as tf

from skimage import io, img_as_ubyte, img_as_bool
from skimage.color import rgb2gray

LEVEL=6

def get_args():
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--list', type=str)
    parser.add_argument('--level', default=LEVEL, type=int)
    return parser.parse_args()

def overlap(a, b):
    '''
    a is an array like object of lengh 4: up, down, left, right
    b is an array like object of lengh 4: up, down, left, right

    origin is at left-upper side
    '''

    up = b[0] if b[0] > a[0] else a[0]
    down = b[1] if b[1] < a[1] else a[1]
    left = b[2] if b[2] > a[2] else a[2]
    right = b[3] if b[3] < a[3] else a[3]

    if left >= right or up >= down:
        up = down = left = right = 0

    return up, down, left, right

def main():
    imgs = []
    with open(args.list) as f:
        for path in f:
            path = path.strip()

            img = io.imread(path)
            gimg = rgb2gray(img)

            imgs.append([img, gimg])

            '''
            for i, img in enumerate(img_pyramid):
                io.imsave('test_{}.jpg'.format(i), img_as_ubyte(img))
            for i, img in enumerate(exclude_pyramid):
                io.imsave('e_{}.jpg'.format(i), img_as_ubyte(img))
            '''

    m0 = np.median(imgs[0][1])
    exclusion = (imgs[0][1] > m0+0.01) | (imgs[0][1] < m0-0.01)
    exclude_pyramid = []
    for img in tf.pyramid_gaussian(exclusion, max_layer=args.level):
        exclude_pyramid.append(img_as_bool(img))

    ref_pyramid = []
    for img in tf.pyramid_gaussian(imgs[0][1] > m0, max_layer=args.level):
        ref_pyramid.append(img_as_bool(img))

    offset = []
    for img in imgs[1:]:
        cur_pyramid = []
        m = np.median(img[1])
        for scale_img in tf.pyramid_gaussian(img[1] > m, max_layer=args.level):
            cur_pyramid.append(img_as_bool(scale_img))

        total_hoffset = 0
        total_woffset = 0
        for exclude_map, img_ref, img_cur in zip(exclude_pyramid[::-1], ref_pyramid[::-1], cur_pyramid[::-1]):
            total_hoffset *= 2
            total_woffset *= 2

            min_diff = img_ref.size
            min_hoffset = 0
            min_woffset = 0
            for hoffset in [0, -1, 1]:
                for woffset in [0, -1, 1]:
                    cur_hoffset = total_hoffset + hoffset
                    cur_woffset = total_woffset + woffset

                    if cur_woffset > 0: 
                        rl = cur_woffset
                        cl = 0
                        rr = img_ref.shape[1]
                        cr = img_cur.shape[1] - cur_woffset
                    else:
                        rl = 0
                        cl = -cur_woffset
                        rr = img_ref.shape[1] + cur_woffset
                        cr = img_cur.shape[1]

                    if cur_hoffset > 0: 
                        ru = cur_hoffset
                        cu = 0
                        rd = img_ref.shape[0]
                        cd = img_cur.shape[0] - cur_hoffset
                    else:
                        ru = 0
                        cu = -cur_hoffset
                        rd = img_ref.shape[0] + cur_hoffset
                        cd = img_cur.shape[0]

                    raw_diff_map = np.logical_xor(img_ref[ru:rd, rl:rr], img_cur[cu:cd, cl:cr])
                    diff_map = np.logical_and(raw_diff_map, exclude_map[ru:rd, rl:rr])
                    diff = np.sum(diff_map)
                    if diff < min_diff:
                        min_diff = diff
                        min_hoffset = hoffset
                        min_woffset = woffset
            total_hoffset += min_hoffset
            total_woffset += min_woffset

        offset.append((total_hoffset, total_woffset))

    spatial_crop = (0, imgs[0][0].shape[0], 0, imgs[0][0].shape[1])
    for img, o in zip(imgs[1:], offset):
        print(o)
        cur_spatial = (o[0], o[0] + img[0].shape[0], o[1], o[1] + img[1].shape[1])
        spatial_crop = overlap(spatial_crop, cur_spatial)

    print(spatial_crop)
    offset.insert(0, (0, 0))

    for i, (img, o) in enumerate(zip(imgs, offset)):
        up, down, left, right = spatial_crop
        up -= o[0]
        down -= o[0]
        left -= o[1]
        right -= o[1]
        io.imsave('after_{}.jpg'.format(i), img_as_ubyte(img[0][up:down, left:right, :]))
        

if __name__ == '__main__':
    args = get_args()
    main()
