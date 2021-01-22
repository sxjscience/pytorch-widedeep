import string

import numpy as np
import pytest
from torch import nn

from pytorch_widedeep.models import Wide, TabMlp, WideDeep, TabTransformer

# Wide array
X_wide = np.random.choice(50, (32, 10))

# Deep Array
colnames = list(string.ascii_lowercase)[:10]
embed_cols = [np.random.choice(np.arange(5), 32) for _ in range(5)]
embed_input = [(u, i, j) for u, i, j in zip(colnames[:5], [5] * 5, [16] * 5)]
embed_input_tt = [(u, i) for u, i in zip(colnames[:5], [5] * 5)]
cont_cols = [np.random.rand(32) for _ in range(5)]
deep_column_idx = {k: v for v, k in enumerate(colnames)}
X_tab = np.vstack(embed_cols + cont_cols).transpose()

# Target
target_regres = np.random.random(32)
target_binary = np.random.choice(2, 32)
target_multic = np.random.choice(3, 32)

# Test dictionary
X_test = {"X_wide": X_wide, "X_tab": X_tab}


##############################################################################
# Test that the three possible methods (regression, binary and mutliclass)
# work well
##############################################################################
@pytest.mark.parametrize(
    "X_wide, X_tab, target, method, X_wide_test, X_tab_test, X_test, pred_dim, probs_dim",
    [
        (X_wide, X_tab, target_regres, "regression", X_wide, X_tab, None, 1, None),
        (X_wide, X_tab, target_binary, "binary", X_wide, X_tab, None, 1, 2),
        (X_wide, X_tab, target_multic, "multiclass", X_wide, X_tab, None, 3, 3),
        (X_wide, X_tab, target_regres, "regression", None, None, X_test, 1, None),
        (X_wide, X_tab, target_binary, "binary", None, None, X_test, 1, 2),
        (X_wide, X_tab, target_multic, "multiclass", None, None, X_test, 3, 3),
    ],
)
def test_fit_methods(
    X_wide,
    X_tab,
    target,
    method,
    X_wide_test,
    X_tab_test,
    X_test,
    pred_dim,
    probs_dim,
):
    wide = Wide(np.unique(X_wide).shape[0], pred_dim)
    deeptabular = TabMlp(
        mlp_hidden_dims=[32, 16],
        dropout=[0.5, 0.5],
        deep_column_idx=deep_column_idx,
        embed_input=embed_input,
        continuous_cols=colnames[-5:],
    )
    model = WideDeep(wide=wide, deeptabular=deeptabular, pred_dim=pred_dim)
    model.compile(method=method, verbose=0)
    model.fit(X_wide=X_wide, X_tab=X_tab, target=target, batch_size=16)
    preds = model.predict(X_wide=X_wide, X_tab=X_tab, X_test=X_test)
    if method == "binary":
        pass
    else:
        probs = model.predict_proba(X_wide=X_wide, X_tab=X_tab, X_test=X_test)
    assert preds.shape[0] == 32, probs.shape[1] == probs_dim


##############################################################################
# Simply Test that runs with the deephead parameter
##############################################################################
def test_fit_with_deephead():
    wide = Wide(np.unique(X_wide).shape[0], 1)
    deeptabular = TabMlp(
        mlp_hidden_dims=[32, 16],
        deep_column_idx=deep_column_idx,
        embed_input=embed_input,
        continuous_cols=colnames[-5:],
    )
    deephead = nn.Sequential(nn.Linear(16, 8), nn.Linear(8, 4))
    model = WideDeep(wide=wide, deeptabular=deeptabular, pred_dim=1, deephead=deephead)
    model.compile(method="binary", verbose=0)
    model.fit(X_wide=X_wide, X_tab=X_tab, target=target_binary, batch_size=16)
    preds = model.predict(X_wide=X_wide, X_tab=X_tab, X_test=X_test)
    probs = model.predict_proba(X_wide=X_wide, X_tab=X_tab, X_test=X_test)
    assert preds.shape[0] == 32, probs.shape[1] == 2


##############################################################################
# Repeat 1st set of tests with the TabTransformer
##############################################################################


@pytest.mark.parametrize(
    "X_wide, X_tab, target, method, X_wide_test, X_tab_test, X_test, pred_dim, probs_dim",
    [
        (X_wide, X_tab, target_regres, "regression", X_wide, X_tab, None, 1, None),
        (X_wide, X_tab, target_binary, "binary", X_wide, X_tab, None, 1, 2),
        (X_wide, X_tab, target_multic, "multiclass", X_wide, X_tab, None, 3, 3),
        (X_wide, X_tab, target_regres, "regression", None, None, X_test, 1, None),
        (X_wide, X_tab, target_binary, "binary", None, None, X_test, 1, 2),
        (X_wide, X_tab, target_multic, "multiclass", None, None, X_test, 3, 3),
    ],
)
def test_fit_methods_tab_transformer(
    X_wide,
    X_tab,
    target,
    method,
    X_wide_test,
    X_tab_test,
    X_test,
    pred_dim,
    probs_dim,
):
    wide = Wide(np.unique(X_wide).shape[0], pred_dim)
    tab_transformer = TabTransformer(
        deep_column_idx={k: v for v, k in enumerate(colnames)},
        embed_input=embed_input_tt,
        continuous_cols=colnames[5:],
    )
    model = WideDeep(wide=wide, deeptabular=tab_transformer, pred_dim=pred_dim)
    model.compile(method=method, verbose=0)
    model.fit(X_wide=X_wide, X_tab=X_tab, target=target, batch_size=16)
    preds = model.predict(X_wide=X_wide, X_tab=X_tab, X_test=X_test)
    if method == "binary":
        pass
    else:
        probs = model.predict_proba(X_wide=X_wide, X_tab=X_tab, X_test=X_test)
    assert preds.shape[0] == 32, probs.shape[1] == probs_dim
