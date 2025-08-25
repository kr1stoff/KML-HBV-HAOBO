# KML-HBV-HAOBO

## 运行

- 主脚本

    ```bash
    /home/mengxf/miniforge3/envs/python3.12/bin/python scripts/kml_haobo_hbv.py \
        --samplesheet /data/mengxf/Project/KML250822-HAOBO-HBV-KMNOVA-16SAMPLE/250820_A00932_1394_AH3WLKDMX2.JML.csv \
        --fqdir /data/mengxf/Project/KML250822-HAOBO-HBV-KMNOVA-16SAMPLE/FASTQ \
        --outdir /data/mengxf/Project/KML250822-HAOBO-HBV-KMNOVA-16SAMPLE/results/250822
    ```

- 合并变异到一个 Excel 文件

    ```bash
    csvtk csv2xlsx -t -f */variant/*.tsv -o KML250822-HAOBO-HBV-KMNOVA-16SAMPLE.variants.xlsx
    ```
