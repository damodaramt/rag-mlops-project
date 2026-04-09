#!/bin/bash

COUNT=900
FILE="rag_commands"

history | tail -$COUNT > $FILE.txt
awk '{$1=""; print substr($0,2)}' $FILE.txt > $FILE_clean.txt
pandoc $FILE_clean.txt -o $FILE.pdf

echo "✅ Exported to $FILE.pdf"
