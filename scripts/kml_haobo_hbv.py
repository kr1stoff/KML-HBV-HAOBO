import click
import pandas as pd
from pathlib import Path


@click.command()
@click.option('--samplesheet', required=True, help='输入 illlumina samplesheet 表.')
@click.option('--fqdir', required=True, help='fastq 文件夹, samplesheet 中对应的')
@click.option('--outdir', type=str, default='kml-haobo-hbv-out', show_default=True, help='结果生成目录.')
@click.help_option(help='显示帮助信息')
def main(samplesheet, fqdir, outdir):
    """KML-HBV-HAOBO 分析流程"""
    fqdir = Path(fqdir).resolve()
    outdir = Path(outdir).resolve()
    home = Path(__file__).parent.resolve()
    # 模板
    with open(home / 'run.sh') as f:
        template = f.read()
    # 脚本目录
    scriptsdir = outdir / '.scripts'
    scriptsdir.mkdir(parents=True, exist_ok=True)
    # 从 samplesheet 获取样本列表
    flag = 0
    matrix = []
    with open(samplesheet, 'r') as f:
        for line in f:
            if line.startswith('Sample_ID'):
                flag = 1
            if flag:
                matrix.append(line.strip().split(','))
    samples = pd.DataFrame(matrix[1:], columns=matrix[0])['Sample_ID'].tolist()
    # 样本 shell
    f0 = open(scriptsdir / 'all.sh', 'w')
    for samp in samples:
        fq1 = list(fqdir.glob(f'{samp}_*_R1_*.fastq.gz'))[0]
        fq2 = list(fqdir.glob(f'{samp}_*_R2_*.fastq.gz'))[0]
        with open(scriptsdir / f'{samp}.sh', 'w') as f:
            f.write(f'SAMPLE_ID="{samp}"\nFQ1="{fq1}"\nFQ2="{fq2}"\nOUTDIR="{outdir}/{samp}"\n')
            f.write(template)
        f0.write(f'bash {scriptsdir / f"{samp}.sh"}\n')
    f0.close()


# 运行
main()
