Another Compiler
================


- configure ply(python-lex-yacc)

method1: [recommended] install pip(2|3) then
```bash
sudo pip(2|3) install ply
```


method2: download ply-3.4.tar.gz then extract it
```bash
cp -r PLY_EXTRACT_PATH/ply-3.4/ply GIT_REPO_ROOT/ply-version/
```
- install C/C++ compiler llvm-3.3(only version 3.2/3.3 supported) python pyhton-dev


debian-based linux:
```bash
sudo apt-get install llvm-3.3-dev gcc python python-dev
```
archlinux:
```bash
pacman -syu llvm-3.3 pyhton pyhton-dev gcc
```

- configure llvmpy
```bash
cd GIT_REPO_ROOT/ply-version
git clone https://github.com/llvmpy/llvmpy.git
cd llvmpy
sudo LLVM_CONFIG_PATH=LLVM_INSTALL_PATH/bin/llvm-config python setup.py install
```
then run the test
```bash
python -c "import llvm; llvm.test()"
```
