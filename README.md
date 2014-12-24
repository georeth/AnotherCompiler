1.configure ply(python-lex-yacc)
download ply-3.4.tar.gz then extract it
cp -r PLY_EXTRACT_PATH/ply-3.4/ply GIT_REPO_ROOT/ply-version/
2.install C/C++ compiler llvm python pyhton-dev
    debian-based linux:
        sudo apt-get install clang gcc python python-dev
    archlinux:
        pacman -syu clang pyhton pyhton-dev gcc
3.configure llvmpy
    cd GIT_REPO_ROOT/ply-version
    git clone https://github.com/llvmpy/llvmpy.git
    cd llvmpy
    LLVM_CONFIG_PATH=LLVM_INSTALL_PATH/bin/llvm-config python setup.py install

    then run the test
    python -c "import llvm; llvm.test()"
