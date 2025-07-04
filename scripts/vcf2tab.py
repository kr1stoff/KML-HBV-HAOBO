import sys
import csv

vcf_file = sys.argv[1]
out_file = sys.argv[2]

with open(vcf_file) as f:
    lines = (line for line in f.readlines() if not line.startswith("##"))
reader = csv.DictReader(lines, delimiter="\t")

with open(out_file, "w") as f:
    # Chrom	Pos	Ref	Alt	Alt_Depth	Total_Depth	Alt_Freq
    f.write("Chrom\tPos\tRef\tAlt\tAlt_Depth\tTotal_Depth\tAlt_Freq\n")
    for row in reader:
        chrom = row["#CHROM"]
        pos = row["POS"]
        ref = row["REF"]
        alt = row["ALT"]
        info = row["INFO"]
        # * 如果过 info 中没有 AO 字段，则跳过该行
        if "AO" not in info:
            continue
        info_dict = dict(item.split("=") for item in info.split(";"))
        ao = info_dict["AO"]
        dp = info_dict["DP"]
        # 计算频率, 看 AO 是否有 ",",即多个变异碱基. 保留 4 位小数
        if "," in ao:
            aos = [int(x) for x in ao.split(",")]
            freqs = ",".join([f"{int(ao) / int(dp):.4f}" for ao in aos])
        else:
            freqs = f"{int(ao) / int(dp):.4f}"
        f.write("\t".join((chrom, pos, ref, alt, ao, dp, freqs)) + "\n")
