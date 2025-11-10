import numpy as np
from nnunetv2.training.dataloading.base_data_loader import nnUNetDataLoaderBase
from nnunetv2.training.dataloading.nnunet_dataset import nnUNetDataset
import torch


class nnUNetDataLoader3D(nnUNetDataLoaderBase):
    def generate_train_batch(self):
        selected_keys = self.get_indices()
        # preallocate memory for data and seg
        data_all = np.zeros(self.data_shape, dtype=np.float32)
        seg_all = np.zeros(self.seg_shape, dtype=np.int16)
        case_properties = []
        positives = torch.zeros((self.seg_shape[0], self.seg_shape[1]), dtype=torch.int64)

        for j, i in enumerate(selected_keys):
            # oversampling foreground will improve stability of model training, especially if many patches are empty
            # (Lung for example)
            force_fg = self.get_do_oversample(j)

            data, seg, properties = self._data.load_case(i)
            lesion_all = np.sum(seg)

            # If we are doing the cascade then the segmentation from the previous stage will already have been loaded by
            # self._data.load_case(i) (see nnUNetDataset.load_case)
            shape = data.shape[1:]
            dim = len(shape)
            bbox_lbs, bbox_ubs = self.get_bbox(shape, force_fg, properties['dilate_locations'], properties['vessel_locations'])

            # whoever wrote this knew what he was doing (hint: it was me). We first crop the data to the region of the
            # bbox that actually lies within the data. This will result in a smaller array which is then faster to pad.
            # valid_bbox is just the coord that lied within the data cube. It will be padded to match the patch size
            # later
            valid_bbox_lbs = [max(0, bbox_lbs[i]) for i in range(dim)]
            valid_bbox_ubs = [min(shape[i], bbox_ubs[i]) for i in range(dim)]

            # At this point you might ask yourself why we would treat seg differently from seg_from_previous_stage.
            # Why not just concatenate them here and forget about the if statements? Well that's because segneeds to
            # be padded with -1 constant whereas seg_from_previous_stage needs to be padded with 0s (we could also
            # remove label -1 in the data augmentation but this way it is less error prone)
            this_slice = tuple([slice(0, data.shape[0])] + [slice(i, j) for i, j in zip(valid_bbox_lbs, valid_bbox_ubs)])
            data = data[this_slice]

            this_slice = tuple([slice(0, seg.shape[0])] + [slice(i, j) for i, j in zip(valid_bbox_lbs, valid_bbox_ubs)])
            seg = seg[this_slice]

            padding = [(-min(0, bbox_lbs[i]), max(bbox_ubs[i] - shape[i], 0)) for i in range(dim)]
            data_all[j] = np.pad(data, ((0, 0), *padding), 'constant', constant_values=0)
            seg_all[j] = np.pad(seg, ((0, 0), *padding), 'constant', constant_values=-1)
            lesion_patch = np.sum(seg_all[j]) #data: (10, 1, 16, 32, 32)
            c_i, z_i, y_i, x_i = np.where(seg_all[j] > 0)
            if len(z_i) > 0:
                z_long = np.max(z_i) - np.min(z_i) + 1 #種樹要加1
                y_long = np.max(y_i) - np.min(y_i) + 1 #種樹要加1
                x_long = np.max(x_i) - np.min(x_i) + 1 #種樹要加1

                #正樣本條件判斷
                if lesion_patch >= lesion_all:
                    positives[j, 0] = 1 #先假定只有一類。邏輯：整個 seg 的所有 voxel 幾乎都在這個 patch 中了。推測目的：這個 patch 含有全部或幾乎全部病灶，標記為正樣本
                elif z_long >= self.data_shape[1]:
                    positives[j, 0] = 1 #先假定只有一類。邏輯：在 z 軸方向的延伸 >= patch 的 depth。 推測目的：這個病灶貫穿整個 patch 的 z 向，推測應為大病灶，視為正樣本
                elif y_long >= self.data_shape[2] and x_long >= self.data_shape[3]*0.6:
                    positives[j, 0] = 1 #先假定只有一類。 邏輯：在 y 軸達到 patch full，高度同時 x 軸有夠寬 (大於 60%)。推測目的：病灶在橫切面相對大（可能是大片腦動脈瘤），標記為正樣本
                elif y_long >= self.data_shape[2]/2 and x_long >= self.data_shape[3]*0.6:
                    positives[j, 0] = 1 #先假定只有一類。 邏輯：稍微放寬的面積條件，允許 y 高一半也算，只要 x 還夠寬。推測目的：收錄中型病灶（可能只佔半高但夠寬），避免漏掉潛在重要 patch
                else:
                    positives[j, 0] = 0 #先假定只有一類
            else:
                positives[j, 0] = 0 #先假定只有一類

        return {'data': data_all, 'seg': seg_all, 'properties': case_properties, 'positives': positives, 'keys': selected_keys}


if __name__ == '__main__':
    folder = '/media/fabian/data/nnUNet_preprocessed/Dataset002_Heart/3d_fullres'
    ds = nnUNetDataset(folder, 0)  # this should not load the properties!
    dl = nnUNetDataLoader3D(ds, 5, (16, 16, 16), (16, 16, 16), 0.33, None, None)
    a = next(dl)
