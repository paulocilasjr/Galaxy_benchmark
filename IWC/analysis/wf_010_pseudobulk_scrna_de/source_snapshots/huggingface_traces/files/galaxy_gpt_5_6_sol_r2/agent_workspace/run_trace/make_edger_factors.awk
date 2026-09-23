BEGIN { FS = OFS = "\t" }
NR > 1 { gsub(/#/, "Num", $1) }
{ print }
