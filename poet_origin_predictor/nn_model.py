# -*- coding: utf-8 -*-
"""
Neural-network classifier for regional-origin prediction.

A feed-forward MLP over the same combined feature vector used by the linear
models (character n-gram TF-IDF + interpretable domain features). It is wrapped
in a scikit-learn compatible estimator so it drops straight into the existing
StratifiedKFold / cross_val_predict evaluation in train.py.

Why an MLP rather than a fine-tuned Transformer: each example here is a whole
poet's corpus represented as a fixed feature vector, the dataset is small
(~240 poets) and runs on CPU. An MLP captures non-linear feature interactions
without the data/compute a Transformer fine-tune would need; the architecture is
the deep-learning counterpart called for in the paper's methodology.
"""
import numpy as np
from scipy.sparse import issparse

from sklearn.base import BaseEstimator, ClassifierMixin
from sklearn.utils.class_weight import compute_class_weight

import torch
import torch.nn as nn


def _seed(s=42):
    torch.manual_seed(s)
    np.random.seed(s)


class _MLP(nn.Module):
    def __init__(self, in_dim, n_classes, hidden, dropout):
        super().__init__()
        layers, d = [], in_dim
        for h in hidden:
            layers += [nn.Linear(d, h), nn.ReLU(), nn.BatchNorm1d(h),
                       nn.Dropout(dropout)]
            d = h
        layers.append(nn.Linear(d, n_classes))
        self.net = nn.Sequential(*layers)

    def forward(self, x):
        return self.net(x)


class TorchMLP(BaseEstimator, ClassifierMixin):
    """sklearn-compatible feed-forward NN with balanced-class training."""

    def __init__(self, hidden=(256, 64), dropout=0.4, lr=1e-3,
                 weight_decay=1e-4, epochs=120, batch_size=32,
                 class_weight="balanced", random_state=42):
        self.hidden = hidden
        self.dropout = dropout
        self.lr = lr
        self.weight_decay = weight_decay
        self.epochs = epochs
        self.batch_size = batch_size
        self.class_weight = class_weight
        self.random_state = random_state

    @staticmethod
    def _to_dense(X):
        return X.toarray().astype(np.float32) if issparse(X) else \
            np.asarray(X, dtype=np.float32)

    def fit(self, X, y):
        _seed(self.random_state)
        X = self._to_dense(X)
        y = np.asarray(y)
        self.classes_ = np.unique(y)
        y_idx = np.searchsorted(self.classes_, y)

        if self.class_weight == "balanced":
            w = compute_class_weight("balanced", classes=self.classes_, y=y)
            cw = torch.tensor(w, dtype=torch.float32)
        else:
            cw = None

        self.model_ = _MLP(X.shape[1], len(self.classes_),
                           self.hidden, self.dropout)
        opt = torch.optim.Adam(self.model_.parameters(), lr=self.lr,
                               weight_decay=self.weight_decay)
        loss_fn = nn.CrossEntropyLoss(weight=cw)

        Xt = torch.from_numpy(X)
        yt = torch.from_numpy(y_idx).long()
        n = len(yt)
        self.model_.train()
        for _ in range(self.epochs):
            perm = torch.randperm(n)
            for i in range(0, n, self.batch_size):
                idx = perm[i:i + self.batch_size]
                if len(idx) < 2:        # BatchNorm needs >1 sample
                    continue
                opt.zero_grad()
                loss = loss_fn(self.model_(Xt[idx]), yt[idx])
                loss.backward()
                opt.step()
        return self

    def predict(self, X):
        self.model_.eval()
        with torch.no_grad():
            logits = self.model_(torch.from_numpy(self._to_dense(X)))
            idx = logits.argmax(1).numpy()
        return self.classes_[idx]
