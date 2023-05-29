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
        'GRCh37': ['grch37', 'hs37d5', 'hg19']
    },
    'variant_caller': {
        'VarScan': ['varscan'],
        'Mutect2': ['mutect2', 'mutect'],
        'Strelka2': ['strelka2', 'strelka'],
        'deepvariant': ['deepvariant'],
        'pbsv': ['pbsv'],
        'GATK': ['gatk', 'gatk4','haplotypecaller', 'gatk_hc'],
        'tardis': ['tardis'],
        'mrCaNaVar': ['mrCanavar', 'mrcanavar'],
        'sniffles': ['sniffles'],
        'rtg': ['rtg'],
        'tnscope': ['tnscope'],
        'LongRanger': ['longranger'],
        'Supernova': ['supernova'],
        'MetaSV' : ['metasv'],
        'Krunch': ['krunch'],
        'fermikit': ['fermikit'],
        'manta': ['manta'],
        'snpeff': ['snpeff'],
        'svaba': ['svaba'],
        'DISCOVAR': ['discovar'],
        'cortext': ['cortext'],
        'freebayes': ['freebayes'],
        'tnscope' : ['tnscope'],
        'sniffles': ['sniffles'],
        'PBHoney': ['pbhoney'],
        'breakseq': ['breakseq'],
        'cnvnator': ['cnvnator'],
        'lumpy': ['lumpy'],
        'PALMER': ['palmer'],
        'Parliament': ['parliament'],
        'scalpel' : ['scalpel'],
        'CGAtools' : ['cgatools'],
        'delly' : ['delly'],
        'TVC' : ['tvc'],
        'GangSTR' : ['gangstr'],
        'HipSTR' : ['hipstr'],
        'HySA' : ['hysa'],
        'BreakScan' :  ['breakscan'],
        'Bionano' : ['bioNano'],
        'Assemblytics' :  ['assemblytics'],
        'Jitterbug' : ['Jitterbug'],
    }
}