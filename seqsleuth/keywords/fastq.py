from seqsleuth.keywords._seqtech import seqtech
from seqsleuth.keywords._centers import centers
from seqsleuth.keywords._samps import sample_ids, trios

## Define dictionary of metadata keywords and their corresponding categories
metadata_keywords = {
    "sequencing_technology": seqtech,
    "center": centers,
    "trio": trios,
    "sample_id": sample_ids,
}
