import argparse
import random
import numpy as np
import imageio

SAMPLE_POINT=50
SMOOTH_WEIGHT=10
OUTPUT='output.hdr'

def get_args():
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--list', type=str)
    parser.add_argument('--sample-point', default=SAMPLE_POINT, type=int)
    parser.add_argument('--smooth-weight', default=SMOOTH_WEIGHT, type=float)
    parser.add_argument('--output', default=OUTPUT, type=str)
    return parser.parse_args()

def main():
    imageio.plugins.freeimage.download()
    data = []
    with open(args.list) as f:
        for path in f:
            path, exposure_time = path.split(',')
            path = path.strip()
            img = imageio.imread(path)
            exposure_time = float(exposure_time.strip())
            data.append((img, exposure_time))

    height, width, _ = data[0][0].shape
    # initialize weight (hat weighting function)
    weight = np.zeros(256)
    for i in range(256):
        if i <= 127:
            weight[i] = i
        else:
            weight[i] = 255 - i

    # choose samples
    samples = []
    for i in range(args.sample_point):
        y = random.randint(0, height-1)
        x = random.randint(0, width-1)
        samples.append((y, x))

    output = np.zeros(data[0][0].shape)
    plt_color = ['r', 'g', 'b']
    for c in range(3):
        A = np.zeros((args.sample_point * len(data) + 255, 256 + args.sample_point))
        b = np.zeros(args.sample_point * len(data) + 255)

        for i, s in enumerate(samples):
            for j, (p, t) in enumerate(data):
                z = p[s[0], s[1], c]
                w = weight[z]
                A[i*len(data)+j, z] = w
                A[i*len(data)+j, 256+i] = -w
                b[i*len(data)+j] = w*np.log(t)

        k = args.sample_point * len(data)

        A[k, 127] = 1

        k += 1
        for i in range(254):
            w = weight[i+1]
            A[k, i] = args.smooth_weight * w
            A[k, i+1] = -2 * args.smooth_weight * w
            A[k, i+2] = args.smooth_weight * w
            k += 1

        result = np.linalg.lstsq(A, b, rcond=None)

        g_curve = result[0][:256]

        fractions = 0
        numerator = 0
        for (p, t) in data:
            z = p[:, :, c]
            fractions += weight[z] * (g_curve[z] - np.log(t))
            numerator += weight[z]
        output[:, :, c] = fractions / numerator

    imageio.imwrite(args.output, output.astype(np.float32), format='HDR-FI')

if __name__ == '__main__':
    args = get_args()
    main()
