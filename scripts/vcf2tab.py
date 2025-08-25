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
        # 如果过 info 中没有 AO 字段，则跳过该行
        if "AO" not in info:
            continue
        info_dict = dict(item.split("=") for item in info.split(";"))
        ao = info_dict["AO"]
        dp = info_dict["DP"]
        # 多 ALT 拆成多条
        # todo 是不是有多 ALT 的 MNP
        if "," in ao:
            aos = [int(x) for x in ao.split(",")]
            alts = alt.split(",")
            for i in range(len(aos)):
                curalt = alts[i]
                if (len(ref) > 1) and (len(ref) == len(curalt)):
                    for i in range(len(ref)):
                        if ref[i] != curalt[i]:
                            f.write("\t".join((chrom, str(int(pos) + i), ref[i], curalt[i],
                                               str(aos[i]), dp, f"{aos[i] / int(dp):.4f}")) + "\n")
                else:
                    f.write("\t".join((chrom, pos, ref, alts[i], str(
                        aos[i]), dp, f"{aos[i] / int(dp):.4f}")) + "\n")
        else:
            freq = f"{int(ao) / int(dp):.4f}"
            # MNP 拆成单个 SNP
            if (len(ref) > 1) and (len(ref) == len(alt)):
                for i in range(len(ref)):
                    if ref[i] != alt[i]:
                        f.write("\t".join((chrom, str(int(pos) + i),
                                ref[i], alt[i], ao, dp, freq)) + "\n")
            # 正常情况
            else:
                f.write("\t".join((chrom, pos, ref, alt, ao, dp, freq)) + "\n")
