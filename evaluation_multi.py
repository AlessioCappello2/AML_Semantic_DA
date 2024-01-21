import torch.nn as nn
import torch
import numpy as np
from utils import reverse_one_hot, compute_global_accuracy, fast_hist, per_class_iu
import argparse
from cityscapes import CityScapes
from torch.utils.data import DataLoader

def parse_args():
    parse = argparse.ArgumentParser()

    parse.add_argument('--num_classes',
                       type=int,
                       default=19,
                       help='num of object classes (with void)')
    parse.add_argument('--num_workers',
                       type=int,
                       default=2,
                       help='num of workers')

    return parse.parse_args()

def main():
    args = parse_args()
    """ model1 = CreateModel(args)
    model1.eval()
    model1.cuda()

    model2 = CreateModel(args)
    model2.eval()
    model2.cuda() """

    val_dataset = CityScapes(mode='val')
    targetloader = DataLoader(val_dataset,
                       batch_size=1,
                       shuffle=False,
                       num_workers=args.num_workers,
                       drop_last=False)

    # ------------------------------------------------- #
    # compute scores and save them
    with torch.no_grad():
        precision_record = []
        hist = np.zeros((args.num_classes, args.num_classes))
        for image, label, _ in targetloader:
            # forward
            output1, _, _ = model1(image)
            output1 = nn.functional.softmax(output1, dim=1)

            output2, _, _ = model2(image)
            output2 = nn.functional.softmax(output2, dim=1)

            a, b = 0.5, 0.5
            predict = a*output1 + b*output2 
            predict = reverse_one_hot(predict)
            predict = np.array(predict.cpu())

            # get RGB label image
            label = label.squeeze()
            label = np.array(label.cpu())

            # compute per pixel accuracy
            precision = compute_global_accuracy(predict, label)
            hist += fast_hist(label.flatten(), predict.flatten(), args.num_classes)

            # there is no need to transform the one-hot array to visual RGB array
            # predict = colour_code_segmentation(np.array(predict), label_info)
            # label = colour_code_segmentation(np.array(label), label_info)
            precision_record.append(precision)

        precision = np.mean(precision_record)
        miou_list = per_class_iu(hist)
        miou = np.mean(miou_list)
        print('precision per pixel for test: %.3f' % precision)
        print('mIoU for validation: %.3f' % miou)
        print(f'mIoU per class: {miou_list}')



if __name__ == '__main__':
    main()