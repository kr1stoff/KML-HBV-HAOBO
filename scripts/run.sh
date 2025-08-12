# SAMPLE_ID="AB19-1"
# FQ1="/data/mengxf/Project/KML250618-haobo-hbv/fastq/AB19-1_R1.fastq.gz"
# FQ2="/data/mengxf/Project/KML250618-haobo-hbv/fastq/AB19-1_R2.fastq.gz"
# OUTDIR="/data/mengxf/Project/KML250618-haobo-hbv/work/250618_analysis/$SAMPLE_ID"

# fastqc
mkdir -p $OUTDIR/fastqc
source /home/mengxf/miniforge3/bin/activate basic
fastqc --threads 8 \
    --outdir $OUTDIR/fastqc \
    $FQ1 $FQ2
conda deactivate

# fastp
mkdir -p $OUTDIR/fastp
/home/mengxf/miniforge3/envs/basic2/bin/fastp --thread 8 \
    --qualified_quality_phred 15 --unqualified_percent_limit 40 --length_required 15 \
    --cut_right --cut_window_size 4 --cut_mean_quality 20 --correction \
    --in1 $FQ1 \
    --in2 $FQ2 \
    --json $OUTDIR/fastp/$SAMPLE_ID.json \
    --html $OUTDIR/fastp/$SAMPLE_ID.html \
    --out1 $OUTDIR/fastp/$SAMPLE_ID.clean.1.fastq \
    --out2 $OUTDIR/fastp/$SAMPLE_ID.clean.2.fastq

# align
mkdir -p $OUTDIR/align
/home/mengxf/miniforge3/envs/basic/bin/bwa mem -t 8 -M -Y -R '@RG\tID:'$SAMPLE_ID'\tSM:'$SAMPLE_ID \
    1 \
    $OUTDIR/fastp/$SAMPLE_ID.clean.1.fastq \
    $OUTDIR/fastp/$SAMPLE_ID.clean.2.fastq |
    /home/mengxf/miniforge3/envs/basic/bin/samtools view -@ 8 -hbS - |
    /home/mengxf/miniforge3/envs/basic/bin/samtools sort -@ 8 -o $OUTDIR/align/$SAMPLE_ID.sorted.bam -
/home/mengxf/miniforge3/envs/basic/bin/samtools index $OUTDIR/align/$SAMPLE_ID.sorted.bam
# depth
/home/mengxf/miniforge3/envs/basic2/bin/bedtools genomecov -bga -ibam $OUTDIR/align/$SAMPLE_ID.sorted.bam |
    awk '$4<20' |
    /home/mengxf/miniforge3/envs/basic2/bin/bedtools merge -i - |
    awk '$3-$2>20' 1>$OUTDIR/align/$SAMPLE_ID.lowcovmask.bed

# variant
mkdir -p $OUTDIR/variant
# lowcov mask
/home/mengxf/miniforge3/envs/basic2/bin/bedtools maskfasta \
    -fi /data/mengxf/Database/genome/Hepatitis_B_virus/HaoBoRef/D00330.fa \
    -bed $OUTDIR/align/$SAMPLE_ID.lowcovmask.bed \
    -fo $OUTDIR/variant/$SAMPLE_ID.masked.fa
# freebayes
/home/mengxf/miniforge3/envs/basic2/bin/freebayes --ploidy 1 --min-repeat-size 10 --read-indel-limit 15 \
    --use-best-n-alleles 4 --theta 0.001 --haplotype-length 0 --min-alternate-fraction 0.001 \
    --min-base-quality 30 --min-coverage 20 --min-alternate-count 2 --min-mapping-quality 30 \
    --max-complex-gap 1 --trim-complex-tail \
    --targets /data/mengxf/GitHub/KML-HBV-HAOBO/assets/target.bed \
    --fasta-reference $OUTDIR/variant/$SAMPLE_ID.masked.fa \
    $OUTDIR/align/$SAMPLE_ID.sorted.bam >$OUTDIR/variant/$SAMPLE_ID.vcf

# variant table
/home/mengxf/miniforge3/bin/python /data/mengxf/GitHub/KML-HBV-HAOBO/scripts/vcf2tab.py \
    $OUTDIR/variant/$SAMPLE_ID.vcf \
    $OUTDIR/variant/$SAMPLE_ID.tsv
