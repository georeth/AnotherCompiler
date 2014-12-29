#!/bin/bash
while true; do
    phase=$(kdialog --combobox "Please select the phase you want to use." \
        "Lex" "Parse" "Analyze (TBD)" "Code Generation (TBD)" --default "Lex" \
        --title "MyLang Compiler")
    [ -z "$phase" ] && exit 0

    if [ "$phase" == "Lex" ]; then
        tool=./lex-test.py
    elif [ "$phase" == "Parse" ]; then
        tool=./parser-test.py
    else
        kdialog --msgbox 'This phase is not ready for presentation yet.'
        continue
    fi

    file=$(cd ../codes && kdialog --getopenfilename final.code)
    if [ $? == 0 ]; then

        $tool $file > /tmp/another-compiler-result
        kdialog --textbox /tmp/another-compiler-result 1200 800
    fi
done
