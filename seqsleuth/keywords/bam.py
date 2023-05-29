from _seqtech import seqtech
from _centers import centers
from _samps import sample_ids, trios

## Define dictionary of metadata keywords and their corresponding categories
metadata_keywords = {
    'sequencing_technology': seqtech,
    'center': centers,
    'trio' : trios,  
    'sample_id': sample_ids,
    'ref_genome': {
        'GRCh38': ['grch38', 'hg38'],
        'GRCh37': ['grch37', 'hs37d5', 'hg19'],
        'CHM13': ['chm13'],
    },
    'aligner' : {
        'bwa': ['bwa', 'bwamem'],
        'bowtie2': ['bowtie2'],
        'novalign': ['novalign'],
        'minimap2': ['minimap2'],
        'ngmlr': ['ngmlr'],
        'pbmm2': ['pbmm2'],
    }
}