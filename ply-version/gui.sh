#!/bin/bash
while true; do
    phase=$(kdialog --combobox "Please select the phase you want to use." \
        "Lex" "Parse" "Analyze" "Code Generation" "Run" --default "Lex" \
        --title "MyLang Compiler")
    [ -z "$phase" ] && exit 0

    if [ "$phase" == "Lex" ]; then
        args=--lex
    elif [ "$phase" == "Parse" ]; then
        args=--parse
    elif [ "$phase" == "Analyze" ]; then
        args=--analyze
    elif [ "$phase" == "Code Generation" ]; then
        args=
    elif [ "$phase" == "Run" ]; then
        args=
    fi

    file=$(cd ../codes && kdialog --getopenfilename final.code)
    if [ $? == 0 ]; then

        ./mylang.py $args $file > /tmp/another-compiler-result
        if [ "$phase" == "Run" ]; then
            lli /tmp/another-compiler-result > /tmp/another-compiler-result-1
            cp /tmp/another-compiler-result-1 /tmp/another-compiler-result
            rm /tmp/another-compiler-result-1
        fi
        kdialog --textbox /tmp/another-compiler-result 1200 800
    fi
done
